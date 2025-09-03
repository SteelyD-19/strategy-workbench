from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Any

@dataclass
class StrategyStory:
    prompt: str = ""
    clarifications: Dict[str, Any] = field(default_factory=lambda: {
        "focus_area": "",
        "purpose": "",
        "industry": "",
        "geography": "",
        "time_horizon": "",
        "decision_outcomes": [],
    })
    assessments: Dict[str, Any] = field(default_factory=lambda: {
        "canonical": [],
        "dynamic": [],
        "selected": [],
    })
    sub_assessments: Dict[str, Any] = field(default_factory=lambda: {
        "by_assessment": {},
        "selected": {},
    })
    updated_at: str = ""

    @property
    def clarifications_complete(self) -> bool:
        c = self.clarifications
        req = ["focus_area", "purpose", "industry", "geography", "time_horizon"]
        return all(bool(c.get(k)) for k in req)

    def update_clarifications(
        self,
        focus_area: str,
        purpose: str,
        industry: str,
        geography: str,
        time_horizon: str,
        decision_outcomes: List[str],
    ) -> None:
        self.clarifications["focus_area"] = focus_area
        self.clarifications["purpose"] = purpose
        self.clarifications["industry"] = industry
        self.clarifications["geography"] = geography
        self.clarifications["time_horizon"] = time_horizon
        self.clarifications["decision_outcomes"] = decision_outcomes or []
        self.touch()

    def touch(self) -> None:
        from datetime import datetime
        self.updated_at = datetime.utcnow().isoformat()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "prompt": self.prompt,
            "clarifications": self.clarifications,
            "assessments": self.assessments,
            "sub_assessments": self.sub_assessments,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "StrategyStory":
        s = cls()
        s.prompt = d.get("prompt", "")
        s.clarifications = d.get("clarifications", s.clarifications)
        s.assessments = d.get("assessments", s.assessments)
        s.sub_assessments = d.get("sub_assessments", s.sub_assessments)
        s.updated_at = d.get("updated_at", "")
        return s
