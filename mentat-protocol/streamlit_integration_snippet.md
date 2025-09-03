# Streamlit integration

```python
import streamlit as st
from mentat_protocol import run_step, ENVELOPES

if "mentat_ctx" not in st.session_state:
    st.session_state.mentat_ctx = {
        "title": st.session_state.story.prompt,
        "purpose": st.session_state.story.clarifications.get("purpose", ""),
        "industry": st.session_state.story.clarifications.get("industry", ""),
        "geography": st.session_state.story.clarifications.get("geography", ""),
        "time_horizon": st.session_state.story.clarifications.get("time_horizon", ""),
        "decision_outcomes": st.session_state.story.clarifications.get("decision_outcomes", []),
    }

canonical = {
    "external": [...],
    "internal": [...],
    "optional": [...],
}

if st.button("Mentat: Recommend Assessments"):
    env = ENVELOPES.step2_assessment_toggle(
        project_context=st.session_state.mentat_ctx,
        user_input=st.session_state.story.prompt,
        canonical=canonical
    )
    resp = run_step(env)
    st.write(resp.get("brief_summary", ""))
    for item in resp.get("recommended_assessments", []):
        st.checkbox(f"{item['label']} — {item['reason']}", value=False, key=item["id"])
    if resp.get("defer_to_next_step_signal"):
        st.success("Ready to proceed to Step 3")
```
