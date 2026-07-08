from fastapi import FastAPI

from app.core.safety import evaluate_safety


app = FastAPI(title="Agente 19 - 19 CRPM", version="0.1.0")


@app.get("/")
def read_root():
    return {"message": "Agente 19 API - Fundacao Tecnica Segura"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    safety = evaluate_safety()
    return {
        "status": "ready" if safety.ok else "blocked",
        "safety_ok": safety.ok,
        "violations": list(safety.violations),
        "human_review_required": True,
        "official_sei_actions_allowed": False,
    }
