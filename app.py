import streamlit as st
import sys
import os
from datetime import datetime
from core.canonical import canonical_all, suggest_dynamic_assessments, suggest_subassessments_for
from core.story import StrategyStory
from core.export import export_json, export_docx_bytes

# Load environment variables from config.env file if it exists (for local development)
def load_env_file():
    possible_paths = [
        os.path.join(os.path.dirname(__file__), 'config.env'),
        os.path.join(os.path.dirname(__file__), '.env'),
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
                return
            except Exception as e:
                print(f"Error loading {env_path}: {e}")

# Load config file for local development
load_env_file()

# For Streamlit Cloud deployment, use secrets
if 'OPENAI_API_KEY' not in os.environ and hasattr(st, 'secrets'):
    if 'OPENAI_API_KEY' in st.secrets:
        os.environ['OPENAI_API_KEY'] = st.secrets['OPENAI_API_KEY']

# Add mentat-protocol to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'mentat-protocol'))
from mentat_protocol import run_step, ENVELOPES

st.set_page_config(page_title="Strategy Workbench (Steps 1–3)", layout="wide")

# Initialize session state
if "story" not in st.session_state:
    st.session_state.story = StrategyStory()
if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "current_step" not in st.session_state:
    st.session_state.current_step = 1
if "assessments_recommended" not in st.session_state:
    st.session_state.assessments_recommended = []
if "sub_assessments_generated" not in st.session_state:
    st.session_state.sub_assessments_generated = {}
if "project_name" not in st.session_state:
    st.session_state.project_name = ""
if "project_started" not in st.session_state:
    st.session_state.project_started = False
if "show_project_naming" not in st.session_state:
    st.session_state.show_project_naming = False
if "step2_initialized" not in st.session_state:
    st.session_state.step2_initialized = False

story = st.session_state.story

# Sidebar
with st.sidebar:
    # Add Mentat icon
    st.image("icons/bot_icon.png", width=300)
    
    # Small spacing below logo
    st.markdown("")
    
    # Project naming and initialization
    if not st.session_state.project_started:
        if not st.session_state.show_project_naming:
            if st.button("Start a New Project", type="primary"):
                st.session_state.show_project_naming = True
                st.rerun()
        else:
            project_name = st.text_input("Project Name:", 
                                       placeholder="Enter project name...",
                                       key="project_name_input")
            
            col1, col2 = st.columns(2)
            with col1:
                # Button is always enabled - user can type and immediately click
                if st.button("Begin Project", type="primary"):
                    if project_name.strip():
                        st.session_state.project_name = project_name.strip()
                        st.session_state.project_started = True
                        st.session_state.show_project_naming = False
                        st.session_state.story = StrategyStory()
                        st.session_state.chat_messages = []
                        st.session_state.current_step = 1
                        st.session_state.assessments_recommended = []
                        st.session_state.sub_assessments_generated = {}
                        st.session_state.step2_initialized = False
                        # Clear any cached responses to prevent cross-session contamination
                        if "mentat_response" in st.session_state:
                            del st.session_state["mentat_response"]
                        if "mentat_defer_signal" in st.session_state:
                            del st.session_state["mentat_defer_signal"]
                        if "project_context" in st.session_state:
                            del st.session_state["project_context"]
                        # Clear project name input
                        if "project_name_input" in st.session_state:
                            del st.session_state["project_name_input"]
                        st.rerun()
                    else:
                        st.error("Please enter a project name to continue")
            with col2:
                if st.button("Cancel", type="secondary"):
                    st.session_state.show_project_naming = False
                    st.rerun()
            
            if not project_name.strip():
                st.info("Please enter a project name to continue")
    else:
        st.markdown(f"**Current Project:** {st.session_state.project_name}")
        if st.button("Start New Project", type="secondary"):
            st.session_state.project_name = ""
            st.session_state.project_started = False
            st.session_state.show_project_naming = False
            st.session_state.story = StrategyStory()
            st.session_state.chat_messages = []
            st.session_state.current_step = 1
            st.session_state.assessments_recommended = []
            st.session_state.sub_assessments_generated = {}
            st.session_state.step2_initialized = False
            # Clear any cached responses to prevent cross-session contamination
            if "mentat_response" in st.session_state:
                del st.session_state["mentat_response"]
            if "mentat_defer_signal" in st.session_state:
                del st.session_state["mentat_defer_signal"]
            if "project_context" in st.session_state:
                del st.session_state["project_context"]
            # Clear project name input
            if "project_name_input" in st.session_state:
                del st.session_state["project_name_input"]
            st.rerun()

    st.markdown("### Project Status")
    
    # Step 1: Strategic Focus
    step1_complete = story.clarifications_complete
    if step1_complete:
        st.markdown("✅ **Step 1: Strategic Focus**")
    elif (st.session_state.current_step == 1 or st.session_state.current_step == 1.5) and st.session_state.get("project_started", False):
        st.markdown("🔵 **Step 1: Strategic Focus**")
    else:
        st.markdown("⚪ **Step 1: Strategic Focus**")
    
    # Step 2: Assessments
    step2_complete = bool(story.assessments.get('selected'))
    if step2_complete:
        st.markdown("✅ **Step 2: Assessments**")
    elif st.session_state.current_step == 2 and st.session_state.get("project_started", False):
        st.markdown("🔵 **Step 2: Assessments**")
    else:
        st.markdown("⚪ **Step 2: Assessments**")
    
    # Step 3: Sub-assessments
    step3_complete = bool(story.sub_assessments.get('selected'))
    if step3_complete:
        st.markdown("✅ **Step 3: Sub-assessments**")
    elif st.session_state.current_step == 3 and st.session_state.get("project_started", False):
        st.markdown("🔵 **Step 3: Sub-assessments**")
    else:
        st.markdown("⚪ **Step 3: Sub-assessments**")

    st.markdown("### Strategic Assessments")
    
    # Group assessments by category
    from core.canonical import CANONICAL_EXTERNAL, CANONICAL_INTERNAL, CANONICAL_OPTIONAL
    
    # External Assessments
    st.markdown("**External:**")
    for assessment in CANONICAL_EXTERNAL:
        if assessment in story.assessments.get("selected", []):
            st.markdown(f"✅ {assessment}")
        else:
            st.markdown(f"⚪ {assessment}")
    
    # Internal Assessments
    st.markdown("**Internal:**")
    for assessment in CANONICAL_INTERNAL:
        if assessment in story.assessments.get("selected", []):
            st.markdown(f"✅ {assessment}")
        else:
            st.markdown(f"⚪ {assessment}")
    
    # Optional/Dynamic Assessments
    st.markdown("**Optional/Dynamic:**")
    if step2_complete:
        dynamic = suggest_dynamic_assessments(story)
        for assessment in dynamic:
            if assessment in story.assessments.get("selected", []):
                st.markdown(f"✅ {assessment}")
            else:
                st.markdown(f"⚪ {assessment}")
    else:
        st.markdown("*Available after Step 2 completion*")

# Main Content Area
if st.session_state.get("project_started", False):
    # Chat Interface
    chat_container = st.container()
    with chat_container:
        st.markdown(f"### Strategy Project: {st.session_state.project_name}")
        
        # Display chat messages with step-aware logic
        # Only show chat messages for the current step and previous steps
        if st.session_state.current_step == 1:
            # For Step 1, show all messages normally
            total_messages = len(st.session_state.chat_messages)
            response_count = 0
            
            for i, message in enumerate(st.session_state.chat_messages):
                if message["role"] == "assistant":
                    # Always show the initial welcome message (first assistant message)
                    if i == 0 and "Welcome to the Strategy Workbench" in message["content"]:
                        with st.chat_message("assistant", avatar="icons/bot_icon.png"):
                            st.markdown(message["content"])
                        continue
                    
                    response_count += 1
                    # Show current response normally, collapse previous ones
                    if i == total_messages - 1:  # Most recent response
                        with st.chat_message("assistant", avatar="icons/bot_icon.png"):
                            st.markdown(message["content"])
                    else:  # Previous responses - show collapsed
                        with st.expander(f"Previous Response #{response_count}", expanded=False):
                            with st.chat_message("assistant", avatar="icons/bot_icon.png"):
                                st.markdown(message["content"])
                            
                            # Show full envelope response if available
                            if "full_response" in message and message["full_response"]:
                                st.markdown("**Full Response:**")
                                full_resp = message["full_response"]
                                
                                # Display the summary
                                if "brief_summary" in full_resp:
                                    st.markdown(f"**Summary:** {full_resp['brief_summary']}")
                                
                                # Display strategic fields
                                fields_to_show = ["focus_area", "purpose", "industry", "geography", "time_horizon", "decision_outcomes"]
                                for field in fields_to_show:
                                    if field in full_resp and full_resp[field]:
                                        if field == "decision_outcomes" and isinstance(full_resp[field], list):
                                            st.markdown(f"**{field.replace('_', ' ').title()}:** {', '.join(full_resp[field])}")
                                        else:
                                            st.markdown(f"**{field.replace('_', ' ').title()}:** {full_resp[field]}")
                                
                                # Display clarifying questions if any
                                if "clarifying_questions" in full_resp and full_resp["clarifying_questions"]:
                                    st.markdown("**Clarifying Questions:**")
                                    for q in full_resp["clarifying_questions"]:
                                        st.markdown(f"- {q}")
                else:
                    # User messages - show normally
                    with st.chat_message("user", avatar="icons/user_Icon.png"):
                        st.markdown(message["content"])
        elif st.session_state.current_step >= 2:
            # For Step 2 and beyond, don't show any previous chat messages
            pass
        
        # Step 1: Strategic Focus
        if st.session_state.current_step == 1:
            if not st.session_state.chat_messages:
                # Initial AI message
                initial_message = """### Welcome to the Strategy Workbench!

I'm here to help you structure your strategic analysis. Let's start with your strategic prompt and work through the framework step by step.

### Step 1: Strategic Focus

Please share your strategic situation or question, and I'll help extract the key clarifications we need."""
                
                st.session_state.chat_messages.append({"role": "assistant", "content": initial_message})
                st.rerun()

            # User input for strategic prompt
            with st.chat_message("user", avatar="icons/user_Icon.png"):
                st.markdown("### Share your strategic situation:")
                # Fresh text area for each new project
                user_prompt = st.text_area("", 
                                          value="", 
                                          placeholder="e.g., We are a laboratory products distribution business...",
                                          height=120,
                                          max_chars=None,
                                          key="strategic_prompt_input")
            
            if st.button("Submit Strategic Prompt", type="primary"):
                if user_prompt.strip():
                    story.prompt = user_prompt
                    # Don't store in session state - let it clear after submission
                    
                    # Add user message
                    st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
                    
                    # Use Mentat Protocol for structured ChatGPT analysis
                    try:
                        # Create project context for Mentat Protocol
                        project_context = {
                            "title": user_prompt[:50] + "..." if len(user_prompt) > 50 else user_prompt,
                            "purpose": "",
                            "industry": "",
                            "geography": "",
                            "time_horizon": "",
                            "decision_outcomes": []
                        }
                        
                        # Store project context in session state for clarifications
                        st.session_state.project_context = project_context
                        
                        # Use step1_clarify envelope for structured analysis
                        env = ENVELOPES.step1_clarify(
                            project_context=project_context,
                            user_input=user_prompt
                        )
                        
                        response = run_step(env)
                        
                        # Extract structured data from response
                        brief_summary = response.get("brief_summary", "")
                        assumption_gaps = response.get("assumption_gaps", [])
                        clarifying_questions = response.get("clarifying_questions", [])
                        defer_signal = response.get("defer_to_next_step_signal", False)
                        
                        # Store structured response in session state
                        st.session_state.mentat_response = response
                        st.session_state.mentat_defer_signal = defer_signal
                        
                        # Use envelope response only - get initial_response field
                        initial_response = response.get("initial_response", "")
                        ai_response = initial_response
                        
                    except Exception as e:
                        # Fall back to simple analysis if API fails
                        st.error(f"AI analysis failed: {str(e)}")
                        ai_response = "I apologize, but I'm having trouble analyzing your strategic prompt right now. Please try again or contact support if the issue persists."
                        st.session_state.mentat_response = None
                        st.session_state.mentat_defer_signal = False
                    
                    st.session_state.chat_messages.append({
                        "role": "assistant", 
                        "content": ai_response,
                        "full_response": response  # Store the full envelope response
                    })
                    st.session_state.current_step = 1.5
                    st.rerun()
                else:
                    st.error("Please enter a strategic prompt to continue.")

        # Step 1.5: Conversational Clarification
        elif st.session_state.current_step == 1.5:
            # Display all chat messages including the initial response
            for message in st.session_state.chat_messages:
                if message["role"] == "assistant":
                    with st.chat_message("assistant", avatar="icons/bot_icon.png"):
                        st.markdown(message["content"])
                else:
                    with st.chat_message("user", avatar="icons/user_Icon.png"):
                        st.markdown(message["content"])
            
            # Create containers for each category with visual attention
            st.markdown("""
            <style>
            .category-header {
                text-align: right;
                font-weight: bold;
                padding-right: 15px;
                color: currentColor;
                display: flex;
                align-items: center;
                justify-content: flex-end;
                height: 40px;
            }
            .answer-container {
                background-color: #262730;
                border-radius: 8px;
                padding: 8px 12px;
                margin: 4px 0;
                border: 1px solid #4a4a4a;
                color: white;
                min-height: 40px;
                display: flex;
                align-items: center;
            }
            </style>
            """, unsafe_allow_html=True)
            
            # Use structured Mentat Protocol response data
            mentat_response = st.session_state.get("mentat_response", {})
            
            # Handle case where mentat_response might be None
            if mentat_response is None:
                mentat_response = {}
            
            # Extract data from structured response or use defaults
            mentat_summary = mentat_response.get("brief_summary", "")
            assumption_gaps = mentat_response.get("assumption_gaps", [])
            
            # Use a more structured approach with proper alignment
            # Directly map from mentat response (no fallbacks - only envelope returns)
            mentat_focus_area = mentat_response.get("focus_area", "")
            mentat_purpose = mentat_response.get("purpose", "")
            mentat_industry = mentat_response.get("industry", "")
            mentat_geography = mentat_response.get("geography", "")
            mentat_time_horizon = mentat_response.get("time_horizon", "")
            mentat_decision_outcomes = mentat_response.get("decision_outcomes", [])
            
            for i, (header, answer) in enumerate([
                ("Mentat Summary:", mentat_summary),
                ("Focus Area:", mentat_focus_area),
                ("Purpose:", mentat_purpose),
                ("Industry:", mentat_industry),
                ("Geography:", mentat_geography),
                ("Time Horizon:", mentat_time_horizon),
                ("Decision Outcomes:", ", ".join(mentat_decision_outcomes) if isinstance(mentat_decision_outcomes, list) else mentat_decision_outcomes)
            ]):
                col1, col2 = st.columns([1, 2])
                with col1:
                    st.markdown(f'<div class="category-header">{header}</div>', unsafe_allow_html=True)
                with col2:
                    st.markdown(f'<div class="answer-container">{answer}</div>', unsafe_allow_html=True)
            
            # Add space after the table
            st.markdown("")
            
            # Run ChatGPT analysis with full assessment context
            from core.canonical import CANONICAL_EXTERNAL, CANONICAL_INTERNAL, CANONICAL_OPTIONAL, DEFAULT_SUBS
            
            assessment_context = f"""
            STRATEGIC FOCUS ANALYSIS CONTEXT:
            
            Current Strategic Focus:
            - Focus Area: {mentat_focus_area}
            - Purpose: {mentat_purpose}
            - Industry: {mentat_industry}
            - Geography: {mentat_geography}
            - Time Horizon: {mentat_time_horizon}
            - Decision Outcomes: {', '.join(mentat_decision_outcomes) if isinstance(mentat_decision_outcomes, list) else mentat_decision_outcomes}
            
            AVAILABLE ASSESSMENTS:
            
            External Assessments:
            {chr(10).join(f"- {assessment}" for assessment in CANONICAL_EXTERNAL)}
            
            Internal Assessments:
            {chr(10).join(f"- {assessment}" for assessment in CANONICAL_INTERNAL)}
            
            Optional/Dynamic Assessments:
            {chr(10).join(f"- {assessment}" for assessment in CANONICAL_OPTIONAL)}
            
            SUB-ASSESSMENT DETAILS:
            {chr(10).join(f"- {main}: {', '.join(subs)}" for main, subs in DEFAULT_SUBS.items())}
            
            Based on this comprehensive assessment framework, analyze if the current strategic focus needs additional clarification for effective assessment planning.
            """
            
            # Use structured clarifying questions from Mentat Protocol
            clarifying_questions = mentat_response.get("clarifying_questions", [])
            defer_signal = st.session_state.get("mentat_defer_signal", False)
            
            if clarifying_questions and not defer_signal:
                # Show structured clarifying questions from Mentat Protocol
                clarification_text = "After thinking about your ask, it may help if you could tell me a little bit about:\n\n"
                for i, question in enumerate(clarifying_questions, 1):
                    clarification_text += f"- **{question}**\n"
            else:
                clarification_text = "Below this you can tell me anything that needs changed or further nuance I should be aware of."
            
            st.markdown(clarification_text)
            
            # New conversational prompt for clarification
            with st.chat_message("user", avatar="icons/user_Icon.png"):
                clarification_input = st.text_area("", 
                                                placeholder="Provide additional details or clarifications about your strategic focus...",
                                                height=100,
                                                max_chars=None,
                                                value="",
                                                key="clarification_input")
            
            if st.button("Submit Clarification", type="primary"):
                if clarification_input.strip():
                    # Add user clarification to chat
                    st.session_state.chat_messages.append({"role": "user", "content": clarification_input})
                    
                    # Use step1_clarify envelope with conversation history for clarification
                    env = ENVELOPES.step1_clarify(
                        project_context=st.session_state.project_context,
                        user_input=clarification_input,
                        conversation_history=st.session_state.chat_messages[:-1]  # Exclude the current message
                    )
                    
                    response = run_step(env)
                    
                    # Extract structured data from response
                    brief_summary = response.get("brief_summary", "")
                    assumption_gaps = response.get("assumption_gaps", [])
                    clarifying_questions = response.get("clarifying_questions", [])
                    defer_signal = response.get("defer_to_next_step_signal", False)
                    initial_response = response.get("initial_response", "")
                    
                    # Store updated structured response in session state
                    st.session_state.mentat_response = response
                    st.session_state.mentat_defer_signal = defer_signal
                    
                    # Add AI response to chat
                    st.session_state.chat_messages.append({
                        "role": "assistant", 
                        "content": initial_response,
                        "full_response": response  # Store the full envelope response
                    })
                    
                    # Clear the clarification input
                    if "clarification_input" in st.session_state:
                        del st.session_state["clarification_input"]
                    
                    st.rerun()
                else:
                    st.error("Please provide clarification to continue.")
            
            # Add "or" text and Complete Step 1 button below Submit Clarification (outside the if block)
            st.markdown("**or**")
            if st.button("Complete Step 1", type="primary", help="Click to finish Step 1 and proceed to Step 2"):
                st.session_state.current_step = 2
                st.rerun()

        # Step 2: Assessments
        elif st.session_state.current_step == 2:
            # Chat Interface for Step 2
            with st.chat_message("assistant", avatar="icons/bot_icon.png"):
                st.markdown("### Step 2: Assessments")
                st.markdown("TBD")

else:
    # Welcome section with minimal top spacing
    st.markdown("### Meet Mentat! Your Strategy Assistant")
    st.markdown("Please start a new project from the sidebar to begin your strategic analysis.")

# Live Summary and Export
if st.session_state.get("project_started", False) and story.clarifications_complete:
    st.divider()
    st.subheader("Step 1: Strategic Focus Summary")
    st.markdown(f"**Strategy Story:** {story.prompt or '—'}")
    st.markdown(f"**Focus:** {story.clarifications.get('focus_area','—')}")
    st.markdown(f"**Purpose:** {story.clarifications.get('purpose','—')}")
    st.markdown(f"**Industry:** {story.clarifications.get('industry','—')}")
    st.markdown(f"**Geography:** {story.clarifications.get('geography','—')}")
    st.markdown(f"**Time Horizon:** {story.clarifications.get('time_horizon','—')}")
    st.markdown(f"**Decision Outcomes:** {', '.join(story.clarifications.get('decision_outcomes',[])) or '—'}")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button("Download JSON", data=export_json(story), file_name="strategy_story.json")
    with col2:
        st.download_button("Download .docx", data=export_docx_bytes(story),
                           file_name="strategy_story.docx",
                           mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")