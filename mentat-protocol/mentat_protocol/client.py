import os, json
from typing import Tuple, Dict, Any, List
from jsonschema import validate, ValidationError
from openai import OpenAI

from . import schemas
from .config import MODEL, TEMPERATURE, RESPONSE_FORMAT

# Load environment variables from config.env file if it exists
def load_env_file():
    # Try multiple possible locations for the config file
    possible_paths = [
        os.path.join(os.path.dirname(__file__), '..', '..', 'config.env'),
        os.path.join(os.path.dirname(__file__), '..', '..', '.env'),
        os.path.join(os.getcwd(), 'config.env'),
        os.path.join(os.getcwd(), '.env')
    ]
    
    for env_path in possible_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
                print(f"✅ Loaded environment variables from: {env_path}")
                return
            except Exception as e:
                print(f"❌ Error loading {env_path}: {e}")
    
    print("ℹ️  No config.env file found. Set OPENAI_API_KEY environment variable manually.")

# Load config file on import
load_env_file()

SYSTEM_PROMPT = """
You are Mentat, a stepwise strategy workbench copilot.

STRATEGIC ASSESSMENT FRAMEWORK CONTEXT:
You are helping structure strategic analysis through a comprehensive assessment framework. The user will progress through:
- Step 1: Strategic focus clarification (current step)
- Step 2: Assessment selection from canonical framework
- Step 3: Sub-assessment planning and execution

AVAILABLE ASSESSMENT CATEGORIES:
External: Market size & demand growth, Competitive intensity, Customer adoption/dependency, Regulatory/contracting environment
Internal: Profitability & cost structure, Capabilities/Fit with core business, Organizational readiness  
Optional/Dynamic: Bargaining leverage potential, Strategic optionality, Partnerships/Ecosystem/Brand/Talent

Each assessment has detailed sub-assessments for thorough analysis.

INSTRUCTIONS:
Return ONLY the fields requested in the 'fields' array of the user message,
as valid JSON that conforms to the JSON schema for the current step.
Do not include prose outside JSON. Do not invent data.

For Step 1 (clarification):
- CRITICAL: In "brief_summary", summarize ONLY the strategic situation from the user's input message. Do NOT include any introductory text, welcome messages, or project metadata. Focus exclusively on the business/strategic content the user provided. 
- Directly populate the strategic fields based on user input:
  * focus_area: The main strategic focus/area being evaluated
  * purpose: The primary objective or goal of the strategic analysis
  * industry: The industry/sector (e.g., "laboratory/healthcare", "technology", "manufacturing")
  * geography: The geographic scope (e.g., "United States", "Global", "North America")
  * time_horizon: The timeframe (e.g., "1-2 years", "12-36 months", "near-term")
  * decision_outcomes: Array of clear statements of decisions that will be supported by the analysis (e.g., ["Whether to retain the business unit", "Whether to divest operations", "How to restructure for maximum value"])
- Make educated guesses for these fields based on the user input - don't default to "needs clarification"
- ALWAYS populate ALL strategic fields (focus_area, purpose, industry, geography, time_horizon, decision_outcomes) with your best interpretation of the user's input
- CRITICAL: Step 1 is ONLY about getting clear strategic context (focus_area, purpose, industry, geography, time_horizon, decision_outcomes)
- Do NOT ask questions about assessments, sub-assessments, analysis methods, or Step 2/3 topics - those are for later steps
- Only ask clarifying questions if strategic fields are genuinely unclear or missing
- If all strategic fields are clear and well-defined, set defer_to_next_step_signal: true and ask NO clarifying questions
- Ask up to 3 targeted clarifying questions ONLY about missing or unclear strategic context
- Use the assessment framework context to inform decision_outcomes but don't ask about the assessments themselves
- If current step's objective is satisfied, set "defer_to_next_step_signal": true
- If you lack data, show it under 'assumption_gaps' as an array of strings (not an object)
- Return assumption_gaps as: ["gap 1", "gap 2", "gap 3"] not as an object
- In the "initial_response" field, provide an acknowledgment that shows confidence in understanding the prompt, asks the user to contemplate the analysis below, and mentions clarification questions if they exist. Example: "I've analyzed your strategic situation and have what I need to proceed. Please review the summary and strategic categorization below, and consider any clarification questions I've included to help refine our focus."
- IMPORTANT: If conversation_history is provided, this is a clarification round. Provide a dynamic response that acknowledges the new information and indicates whether Step 1 is complete or needs more clarification. Examples: "Thank you for that clarification, I now have what I need to proceed" or "That helps, but I still need clarification on [specific field]" or "Perfect, that clarifies the strategic focus completely."
- For clarification rounds, the "brief_summary" should summarize the updated strategic understanding based on the user's clarification input, incorporating any new information provided.
"""

SCHEMA_BY_STEP = {
    "step_1_clarify": schemas.STEP1,
    "step_2_assessment_toggle": schemas.STEP2,
    "step_3_subassessments": schemas.STEP3,
    "prompt_doctor": schemas.PROMPT_DOCTOR,
}

def enforce_fields_only(data: Dict[str, Any], allowed_fields: List[str]) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if k in allowed_fields}

def validate_response(step: str, payload: Dict[str, Any]) -> Tuple[bool, str | None]:
    schema = SCHEMA_BY_STEP[step]
    try:
        validate(payload, schema)
        return True, None
    except ValidationError as e:
        return False, str(e)

def _call_openai(envelope: Dict[str, Any], model: str = MODEL, temperature: float = TEMPERATURE) -> Dict[str, Any]:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # Build messages with conversation history if provided
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add conversation history if present
    conversation_history = envelope.get("conversation_history", [])
    if conversation_history:
        messages.extend(conversation_history)
    
    # Add current envelope as user message
    messages.append({"role": "user", "content": json.dumps(envelope)})
    
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        response_format=RESPONSE_FORMAT
    )
    content = resp.choices[0].message.content
    return json.loads(content)

def run_step(envelope: Dict[str, Any]) -> Dict[str, Any]:
    step = envelope["step"]
    fields = envelope.get("fields", [])
    raw = _call_openai(envelope)
    clean = enforce_fields_only(raw, fields)
    ok, err = validate_response(step, clean)
    if ok:
        return clean

    retry_env = {
        **envelope,
        "constraints": {
            **envelope.get("constraints", {}),
            "do": ["Return JSON that exactly matches the step schema and the 'fields' keys only."]
        }
    }
    raw_retry = _call_openai(retry_env, temperature=0.0)
    clean_retry = enforce_fields_only(raw_retry, fields)
    ok2, err2 = validate_response(step, clean_retry)
    if not ok2:
        raise ValueError(f"Model response invalid: {err2}")
    return clean_retry
