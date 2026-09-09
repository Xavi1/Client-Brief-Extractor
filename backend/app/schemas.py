# app/schemas.py
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class ClientBriefRequest(BaseModel):
    message: str = Field(min_length=10, max_length=10_000)


class ClientBrief(BaseModel):
    client_name: str | None = None
    business_type: str | None = None
    project_type: str
    requested_features: list[str]
    budget: float | None = Field(default=None, ge=0)
    currency: str | None = None
    deadline: str | None = None
    missing_information: list[str]
    extraction_confidence: Literal["high", "medium", "low"] 