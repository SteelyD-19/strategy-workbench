# Strategy Workbench (Prototype · Steps 1–3)

A Streamlit demo of the first three stages of a strategy workbench with a live **Strategy Story** summary.

## Scope
- **Step 1 — Strategic Prompt & Clarifications**
- **Step 2 — Primary Assessments** (canonical + dynamic suggestions, user toggles)
- **Step 3 — Sub-Assessments** (confirm/edit per assessment)
- **Step 4 — Not implemented** (placeholder)

## Visual / UX
- Conversational center pane (Chat-style).
- **Left Sidebar “New Strategic Area”** shows: status, **toggled assessments**, **canonical (turned OFF)**, and expandable **sub-assessments**.

## Run
1) `pip install -r requirements.txt`  
2) `streamlit run app.py`

## Files
- `app.py` — UI
- `core/canonical.py` — canonical lists, dynamic suggests, sub-assessment defaults
- `core/story.py` — session model
- `core/export.py` — JSON / DOCX export
