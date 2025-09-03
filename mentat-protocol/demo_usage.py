import json
from mentat_protocol import run_step, ENVELOPES

def demo():
    project_context = {
        "title": "Lab Products Distributor — Acute Health Systems",
        "purpose": "Profitability & strategic options review",
        "industry": "Healthcare distribution",
        "geography": "US",
        "time_horizon": "12–24 months",
        "decision_outcomes": ["Sell", "Leverage for contract renegotiation", "Retain & optimize"]
    }
    canonical = {
        "external": [
            "Market size & demand growth",
            "Competitive intensity",
            "Customer adoption/dependency",
            "Regulatory/contracting environment"
        ],
        "internal": [
            "Profitability & cost structure",
            "Capabilities / Fit with core business",
            "Organizational readiness"
        ],
        "optional": [
            "Bargaining leverage potential",
            "Strategic optionality",
            "Partnerships / Ecosystem / Brand / Talent"
        ]
    }
    env = ENVELOPES.step2_assessment_toggle(
        project_context=project_context,
        user_input="We think customer dependency matters due to specimen collection kit volumes.",
        canonical=canonical
    )
    resp = run_step(env)
    print(json.dumps(resp, indent=2))

if __name__ == "__main__":
    demo()
