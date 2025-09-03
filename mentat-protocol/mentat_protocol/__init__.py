from .client import run_step

class ENVELOPES:
    @staticmethod
    def step1_clarify(project_context: dict, user_input: str, conversation_history: list = None) -> dict:
        return {
            "project_context": project_context,
            "step": "step_1_clarify",
            "user_input": user_input,
            "conversation_history": conversation_history or [],
            "constraints": {
                "style": "comprehensive-summary",
                "max_chars": 1000,
                "do": [
                    "provide a well-written, comprehensive summary of the strategic situation",
                    "ask up to 3 targeted clarifying questions ONLY about Step 1 fields: focus_area, purpose, industry, geography, time_horizon, decision_outcomes",
                    "focus decision_outcomes on clear statements of decisions that will be supported by the analysis",
                    "end with guidance for user clarification if questions are asked"
                ],
                "dont": [
                    "no recommendations", 
                    "no assessment suggestions yet",
                    "no questions about analysis methods or assessment types",
                    "no questions about Step 2 or Step 3 topics"
                ]
            },
            "fields": ["brief_summary", "assumption_gaps", "clarifying_questions", "defer_to_next_step_signal", "initial_response", "focus_area", "purpose", "industry", "geography", "time_horizon", "decision_outcomes"]
        }

    @staticmethod
    def step2_assessment_toggle(project_context: dict, user_input: str, canonical: dict) -> dict:
        return {
            "project_context": project_context,
            "step": "step_2_assessment_toggle",
            "user_input": user_input,
            "constraints": {
                "style": "concise-bullets",
                "max_chars": 1200,
                "dont": ["no subassessments yet"]
            },
            "fields": ["brief_summary", "recommended_assessments", "clarifying_questions", "defer_to_next_step_signal"],
            "canonical": canonical,
            "ui_hints": {
                "selection_mode": "toggle",
                "return_ids_instead_of_labels": True
            }
        }

    @staticmethod
    def step3_subassessments(project_context: dict, user_input: str, selected_assessments: list[str]) -> dict:
        return {
            "project_context": project_context,
            "step": "step_3_subassessments",
            "user_input": user_input,
            "constraints": {
                "style": "table-ish",
                "max_chars": 1500,
                "do": ["return short why + required_inputs + effort"]
            },
            "fields": ["brief_summary", "subassessments_by_assessment", "clarifying_questions", "defer_to_next_step_signal"],
            "selected_assessments": selected_assessments
        }

    @staticmethod
    def prompt_doctor(raw_prompt: str) -> dict:
        return {
            "step": "prompt_doctor",
            "raw_prompt": raw_prompt,
            "constraints": {
                "max_chars": 500,
                "style": "tight-paragraph",
                "fields": ["reframed_prompt", "missing_elements", "confirm_question"]
            },
            "fields": ["reframed_prompt", "missing_elements", "confirm_question"]
        }
