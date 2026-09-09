# app/main.py
from fastapi import FastAPI, HTTPException

from app.schemas import ClientBrief, ClientBriefRequest
from app.services.brief_extractor import (
    BriefExtractionError,
    extract_client_brief,
)
from app.settings import settings

app = FastAPI(title="Client Brief Extractor")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}

@app.get("/info")
def get_model_info():
    return {
        "message": "Settings loaded successfully!",
        "model_name": settings.MODEL_NAME,
        # Avoid exposing your actual API key entirely in production logs/responses
        "api_key_configured": bool(settings.MODEL_API_KEY) 
    }


@app.post("/briefs/extract", response_model=ClientBrief)
async def extract_brief(request: ClientBriefRequest) -> ClientBrief:
    try:
        return await extract_client_brief(request.message)
    except BriefExtractionError as exc:
        raise HTTPException(
            status_code=502,
            detail="The client brief could not be extracted.",
        ) from exc