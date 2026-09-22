import streamlit as st

from supplier_intel.engine import demo_engine

st.set_page_config(page_title="Supplier Intelligence", layout="wide")
engine = demo_engine()
summary = engine.portfolio_summary()

st.title("Semiconductor Supplier Intelligence")
st.caption("Synthetic decision-support demo - every score is explainable")
c1, c2, c3 = st.columns(3)
c1.metric("Suppliers", summary["supplier_count"])
c2.metric("300 mm-equivalent capacity", f"{summary['total_300mm_equivalent_capacity']:,.0f}")
c3.metric("Concentration HHI", summary["concentration_hhi"])

supplier = st.selectbox("Supplier", [row["supplier_id"] for row in engine.records()])
score = engine.score(supplier)
st.metric("Risk score", f"{score['risk_score']}/100", score["risk_band"].upper())
st.bar_chart(score["components"])
st.subheader("Reason codes")
st.write(score["reason_codes"] or ["No elevated component"])
st.subheader("Cited executive brief")
st.json(engine.executive_brief(supplier))

