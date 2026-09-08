# app/main.py
from fastapi import FastAPI, HTTPException

from app.schemas import ClientBrief, ClientBriefRequest
from app.services.brief_extractor import (
    BriefExtractionError,
    extract_client_brief,
)

app = FastAPI(title="Client Brief Extractor")


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@app.post("/briefs/extract", response_model=ClientBrief)
async def extract_brief(request: ClientBriefRequest) -> ClientBrief:
    try:
        return await extract_client_brief(request.message)
    except BriefExtractionError as exc:
        raise HTTPException(
            status_code=502,
            detail="The client brief could not be extracted.",
        ) from exc