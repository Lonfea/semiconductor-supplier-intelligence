from __future__ import annotations

from collections.abc import Iterable
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from math import isfinite


@dataclass(frozen=True)
class SupplierObservation:
    supplier_id: str
    country: str
    wafer_mm: int
    monthly_wafer_starts: float
    process_nodes_nm: tuple[int, ...]
    on_time_delivery: float
    financial_exposure: float
    geopolitical_risk: float
    evidence_ids: tuple[str, ...] = ()

    def validate(self) -> None:
        if not self.supplier_id.strip():
            raise ValueError("supplier_id is required")
        if self.wafer_mm not in {150, 200, 300}:
            raise ValueError("wafer_mm must be 150, 200 or 300")
        if not isfinite(self.monthly_wafer_starts) or self.monthly_wafer_starts <= 0:
            raise ValueError("monthly_wafer_starts must be positive")
        if not self.process_nodes_nm or any(node <= 0 for node in self.process_nodes_nm):
            raise ValueError("at least one positive process node is required")
        for name, value in {
            "on_time_delivery": self.on_time_delivery,
            "financial_exposure": self.financial_exposure,
            "geopolitical_risk": self.geopolitical_risk,
        }.items():
            if not 0 <= value <= 1:
                raise ValueError(f"{name} must be between 0 and 1")


DEFAULT_WEIGHTS = {
    "geographic": 0.25,
    "delivery": 0.20,
    "financial": 0.15,
    "technology": 0.25,
    "uncertainty": 0.15,
}


class IntelligenceEngine:
    def __init__(self, observations: Iterable[SupplierObservation], evidence: dict[str, str] | None = None):
        self.observations = tuple(observations)
        if not self.observations:
            raise ValueError("at least one observation is required")
        for item in self.observations:
            item.validate()
        self.evidence = evidence or {}

    @staticmethod
    def equivalent_300mm(item: SupplierObservation) -> float:
        return round(item.monthly_wafer_starts * (item.wafer_mm / 300) ** 2, 2)

    def portfolio_summary(self) -> dict[str, object]:
        capacity = {x.supplier_id: self.equivalent_300mm(x) for x in self.observations}
        total = sum(capacity.values())
        shares = {key: value / total for key, value in capacity.items()}
        hhi = sum(share**2 for share in shares.values()) * 10_000
        nodes = sorted({node for item in self.observations for node in item.process_nodes_nm})
        return {
            "supplier_count": len(self.observations),
            "total_300mm_equivalent_capacity": round(total, 2),
            "capacity_share": {key: round(value, 4) for key, value in shares.items()},
            "concentration_hhi": round(hhi, 1),
            "process_nodes_nm": nodes,
        }

    def score(self, supplier_id: str, weights: dict[str, float] | None = None) -> dict[str, object]:
        item = next((x for x in self.observations if x.supplier_id == supplier_id), None)
        if item is None:
            raise KeyError(supplier_id)
        chosen = weights or DEFAULT_WEIGHTS
        if set(chosen) != set(DEFAULT_WEIGHTS) or abs(sum(chosen.values()) - 1) > 1e-8:
            raise ValueError("weights must contain all components and sum to 1")

        node_frequency = {
            node: sum(node in other.process_nodes_nm for other in self.observations)
            for node in item.process_nodes_nm
        }
        single_source_share = sum(count == 1 for count in node_frequency.values()) / len(node_frequency)
        evidence_coverage = min(len(set(item.evidence_ids)) / 3, 1)
        components = {
            "geographic": item.geopolitical_risk,
            "delivery": 1 - item.on_time_delivery,
            "financial": item.financial_exposure,
            "technology": single_source_share,
            "uncertainty": 1 - evidence_coverage,
        }
        score = 100 * sum(components[key] * chosen[key] for key in components)
        reasons = []
        if components["geographic"] >= 0.6:
            reasons.append("GEOGRAPHIC_CONCENTRATION")
        if components["delivery"] >= 0.15:
            reasons.append("DELIVERY_VARIANCE")
        if components["technology"] > 0:
            reasons.append("SINGLE_SOURCE_NODE")
        if components["uncertainty"] > 0.33:
            reasons.append("LIMITED_EVIDENCE")
        return {
            "supplier_id": supplier_id,
            "risk_score": round(score, 1),
            "risk_band": "high" if score >= 65 else "medium" if score >= 35 else "low",
            "components": {key: round(value, 3) for key, value in components.items()},
            "weights": chosen,
            "reason_codes": reasons,
            "data_quality": round(evidence_coverage, 2),
        }

    def executive_brief(self, supplier_id: str) -> dict[str, object]:
        item = next((x for x in self.observations if x.supplier_id == supplier_id), None)
        if item is None:
            raise KeyError(supplier_id)
        missing = [ref for ref in item.evidence_ids if ref not in self.evidence]
        if missing:
            raise ValueError(f"unregistered evidence: {missing}")
        result = self.score(supplier_id)
        statement = (
            f"{supplier_id} provides {self.equivalent_300mm(item):,.0f} monthly 300 mm-equivalent "
            f"wafer starts across nodes {sorted(item.process_nodes_nm)} nm. "
            f"The governed risk score is {result['risk_score']}/100 ({result['risk_band']})."
        )
        return {
            "as_of": datetime.now(UTC).date().isoformat(),
            "statement": statement,
            "reason_codes": result["reason_codes"],
            "citations": [{"id": ref, "source": self.evidence[ref]} for ref in item.evidence_ids],
        }

    def records(self) -> list[dict[str, object]]:
        return [asdict(item) | {"capacity_300mm_eq": self.equivalent_300mm(item)} for item in self.observations]


def demo_engine() -> IntelligenceEngine:
    evidence = {
        "E1": "Synthetic annual-report extract, retrieved 2026-09-22",
        "E2": "Synthetic capacity survey, retrieved 2026-09-22",
        "E3": "Synthetic delivery KPI ledger, retrieved 2026-09-22",
    }
    rows = [
        SupplierObservation("alpha-foundry", "DE", 300, 52_000, (28, 40, 65), 0.94, 0.35, 0.20, ("E1", "E2", "E3")),
        SupplierObservation("beta-semi", "SG", 300, 76_000, (40, 65, 90), 0.82, 0.55, 0.48, ("E1", "E2")),
        SupplierObservation("gamma-fab", "US", 200, 90_000, (90, 130), 0.97, 0.20, 0.12, ("E2", "E3")),
    ]
    return IntelligenceEngine(rows, evidence)
