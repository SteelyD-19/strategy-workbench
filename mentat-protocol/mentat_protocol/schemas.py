STEP1 = {
    "type": "object",
    "required": ["brief_summary", "assumption_gaps", "clarifying_questions", "defer_to_next_step_signal", "initial_response"],
    "properties": {
        "brief_summary": {"type": "string", "maxLength": 1000},
        "assumption_gaps": {"type": "array", "items": {"type": "string"}, "maxItems": 6},
        "clarifying_questions": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "defer_to_next_step_signal": {"type": "boolean"},
        "initial_response": {"type": "string", "maxLength": 300},
        "focus_area": {"type": "string", "maxLength": 200},
        "purpose": {"type": "string", "maxLength": 200},
        "industry": {"type": "string", "maxLength": 200},
        "geography": {"type": "string", "maxLength": 200},
        "time_horizon": {"type": "string", "maxLength": 200},
        "decision_outcomes": {"type": "array", "items": {"type": "string"}, "maxItems": 5},
        "notes": {"type": "string"}
    },
    "additionalProperties": False
}

STEP2 = {
    "type": "object",
    "required": ["brief_summary", "recommended_assessments", "clarifying_questions", "defer_to_next_step_signal"],
    "properties": {
        "brief_summary": {"type": "string", "maxLength": 1000},
        "recommended_assessments": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["id", "label", "reason", "priority"],
                "properties": {
                    "id": {"type": "string"},
                    "label": {"type": "string"},
                    "reason": {"type": "string", "maxLength": 300},
                    "priority": {"type": "string", "enum": ["low", "medium", "high"]}
                },
                "additionalProperties": False
            },
            "maxItems": 10
        },
        "clarifying_questions": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "defer_to_next_step_signal": {"type": "boolean"},
        "notes": {"type": "string"}
    },
    "additionalProperties": False
}

STEP3 = {
    "type": "object",
    "required": ["brief_summary", "subassessments_by_assessment", "clarifying_questions", "defer_to_next_step_signal"],
    "properties": {
        "brief_summary": {"type": "string", "maxLength": 1000},
        "subassessments_by_assessment": {
            "type": "object",
            "additionalProperties": {
                "type": "array",
                "items": {
                    "type": "object",
                    "required": ["name", "why_it_matters", "required_inputs", "effort"],
                    "properties": {
                        "name": {"type": "string"},
                        "why_it_matters": {"type": "string", "maxLength": 280},
                        "required_inputs": {"type": "array", "items": {"type": "string"}, "maxItems": 6},
                        "effort": {"type": "string", "enum": ["low", "medium", "high"]}
                    },
                    "additionalProperties": False
                },
                "maxItems": 10
            }
        },
        "clarifying_questions": {"type": "array", "items": {"type": "string"}, "maxItems": 3},
        "defer_to_next_step_signal": {"type": "boolean"},
        "notes": {"type": "string"}
    },
    "additionalProperties": False
}

PROMPT_DOCTOR = {
    "type": "object",
    "required": ["reframed_prompt", "missing_elements", "confirm_question"],
    "properties": {
        "reframed_prompt": {"type": "string", "maxLength": 500},
        "missing_elements": {"type": "array", "items": {"type": "string"}, "maxItems": 8},
        "confirm_question": {"type": "string", "maxLength": 140}
    },
    "additionalProperties": False
}
