# app/schemas.py
from typing import Literal
from pydantic import AliasChoices, BaseModel, Field, field_validator


class ClientBriefRequest(BaseModel):
    message: str = Field(
        min_length=10,
        max_length=10_000,
        validation_alias=AliasChoices("message", "prompt"),
    )

    @field_validator("message", mode="before")
    @classmethod
    def trim_message(cls, value: object) -> object:
        return value.strip() if isinstance(value, str) else value


class ClientBrief(BaseModel):
    client_name: str | None = None
    business_type: str | None = None
    project_type: str
    requested_features: list[str]
    budget: float | None = Field(default=None, ge=0)
    currency: str | None = None
    deadline: str | None = None
    timeline_notes: str | None = None
    missing_information: list[str]
    extraction_confidence: Literal["high", "medium", "low"]
    constraints: list[str] = Field(default_factory=list)
    budget_notes: str | None = None