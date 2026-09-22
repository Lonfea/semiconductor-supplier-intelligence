from fastapi import FastAPI, HTTPException

from .engine import demo_engine

app = FastAPI(title="Semiconductor Supplier Intelligence", version="1.0.0")
engine = demo_engine()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/portfolio")
def portfolio() -> dict[str, object]:
    return engine.portfolio_summary()


@app.get("/suppliers")
def suppliers() -> list[dict[str, object]]:
    return engine.records()


@app.get("/suppliers/{supplier_id}/risk")
def supplier_risk(supplier_id: str) -> dict[str, object]:
    try:
        return engine.score(supplier_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="supplier not found") from exc


@app.get("/suppliers/{supplier_id}/brief")
def supplier_brief(supplier_id: str) -> dict[str, object]:
    try:
        return engine.executive_brief(supplier_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="supplier not found") from exc

