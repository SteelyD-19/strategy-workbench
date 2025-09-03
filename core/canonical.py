from typing import List, Dict
from core.story import StrategyStory

CANONICAL_EXTERNAL = [
    "Market size & demand growth",
    "Competitive intensity",
    "Customer adoption/dependency",
    "Regulatory/contracting environment",
]

CANONICAL_INTERNAL = [
    "Profitability & cost structure",
    "Capabilities / Fit with core business",
    "Organizational readiness",
]

CANONICAL_OPTIONAL = [
    "Bargaining leverage potential",
    "Strategic optionality",
    "Partnerships / Ecosystem / Brand / Talent",
]

def canonical_all() -> List[str]:
    return CANONICAL_EXTERNAL + CANONICAL_INTERNAL + CANONICAL_OPTIONAL

def suggest_dynamic_assessments(story: StrategyStory) -> List[str]:
    dynamic: List[str] = []
    prompt = (story.prompt or "").lower()
    industry = (story.clarifications.get("industry") or "").lower()
    purpose = (story.clarifications.get("purpose") or "").lower()

    if any(k in prompt for k in ["divest", "sale", "spin", "carve"]):
        dynamic.append("Buyer landscape & valuation drivers")
    if any(k in prompt for k in ["negotia", "leverage", "contract"]):
        dynamic.append("Negotiation leverage mapping")
    if any(k in industry for k in ["health", "lab", "medical", "biotech"]):
        dynamic.append("Quality & compliance implications")
    if any(k in purpose for k in ["moat", "advantage", "defensible"]):
        dynamic.append("Differentiation & defensibility levers")

    seen = set(canonical_all())
    return [d for d in dynamic if d not in seen]

DEFAULT_SUBS: Dict[str, List[str]] = {
    "Market size & demand growth": [
        "Segment growth rates",
        "Price/mix stability",
        "Structural shifts (consolidation, automation)",
    ],
    "Competitive intensity": [
        "Share of top competitors",
        "Entry/exit dynamics",
        "Price-based vs. service-based competition",
    ],
    "Customer adoption/dependency": [
        "Revenue concentration",
        "Criticality of category to operations",
        "Switching costs & substitution risk",
    ],
    "Regulatory/contracting environment": [
        "Contract term constraints",
        "Compliance cost footprint",
        "Regulatory outlook (2–3y)",
    ],
    "Profitability & cost structure": [
        "Contribution margin by segment",
        "Fixed vs. variable allocation",
        "Logistics & service cost drivers",
    ],
    "Capabilities / Fit with core business": [
        "Strategic synergies (volume, suppliers)",
        "Distraction vs. capability building",
        "Alignment with brand & focus",
        "Customer needs vs. internal capability gap",
    ],
    "Organizational readiness": [
        "Systems & data separation",
        "Legal/contract unwind risk",
        "Change management capacity",
    ],
    "Bargaining leverage potential": [
        "Supplier leverage from combined volumes",
        "Customer dependency if exited",
        "Cross-leverage in broader contracts",
    ],
    "Strategic optionality": [
        "Retain & optimize scenario",
        "Divestiture/Buyer types & multiples",
        "JV/partnership alternative",
        "Cost of historical underinvestment",
    ],
    "Partnerships / Ecosystem / Brand / Talent": [
        "Required partners for scale",
        "Brand credibility with target buyers",
        "Talent availability for key roles",
    ],
    "Buyer landscape & valuation drivers": [
        "Strategic buyers vs. financial buyers",
        "Synergy narratives",
        "DCF vs. market comps sensitivities",
    ],
    "Negotiation leverage mapping": [
        "BATNA analysis (us vs. counterpart)",
    ],
    "Quality & compliance implications": [
        "Accreditation/quality dependencies",
        "Audit exposure",
        "Cost of non-compliance risk",
    ],
    "Differentiation & defensibility levers": [
        "Proprietary data/processes",
        "Switching costs & workflow embedding",
        "Speed/experience advantages",
    ],
}

def suggest_subassessments_for(assessment: str) -> List[str]:
    return DEFAULT_SUBS.get(assessment, ["Define scope", "Identify KPIs", "Data sources & timeline"])
