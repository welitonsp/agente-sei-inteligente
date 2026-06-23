from fastapi import FastAPI

app = FastAPI(title="Agente 19 - 19º CRPM", version="0.1.0")

@app.get("/")
def read_root():
    return {"message": "Agente 19 API - Fundação Técnica Segura"}
