import pytest

from supplier_intel.engine import IntelligenceEngine, SupplierObservation, demo_engine


def test_capacity_normalization_and_portfolio_hhi():
    engine = demo_engine()
    gamma = next(x for x in engine.observations if x.supplier_id == "gamma-fab")
    assert engine.equivalent_300mm(gamma) == 40_000
    summary = engine.portfolio_summary()
    assert summary["supplier_count"] == 3
    assert 3_333 <= summary["concentration_hhi"] <= 10_000


def test_risk_is_explainable_and_bounded():
    result = demo_engine().score("beta-semi")
    assert 0 <= result["risk_score"] <= 100
    assert set(result["components"]) == {"geographic", "delivery", "financial", "technology", "uncertainty"}
    assert "DELIVERY_VARIANCE" in result["reason_codes"]


def test_unknown_supplier_and_invalid_observation():
    with pytest.raises(KeyError):
        demo_engine().score("missing")
    bad = SupplierObservation("bad", "XX", 250, 1, (40,), 1, 0, 0)
    with pytest.raises(ValueError):
        IntelligenceEngine([bad])


def test_brief_rejects_unregistered_evidence():
    row = SupplierObservation("a", "DE", 300, 100, (40,), 1, 0, 0, ("UNKNOWN",))
    engine = IntelligenceEngine([row])
    with pytest.raises(ValueError, match="unregistered evidence"):
        engine.executive_brief("a")
