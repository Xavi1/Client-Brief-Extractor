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
    company_name: str | None = Field(
        description=(
            "The explicitly stated company or business name. "
            "Extract names such as Oak & Home. Return null "
            "when no company name is stated."
        )
    )

    business_type: str | None = Field(
        description=(
            "The type of business, such as furniture company "
            "or bakery. Return null if not stated."
        )
    )

    project_type: str | None = Field(
        description=(
            "The complete project type, such as ecommerce website "
            "or mobile application. Return null if unknown."
        )
    )

    requested_features: list[str] = Field(
        description="Explicitly requested functional features."
    )

    budget: float | None = Field(
        ge=0,
        description=(
            "The numeric budget amount without currency symbols "
            "or separators. Return null only when no amount "
            "is provided."
        )
    )

    currency: str | None = Field(
        description=(
            "The ISO 4217 currency code, such as PHP or USD. "
            "Return null if no currency is identifiable."
        )
    )

    deadline: str | None = Field(
        description="A concrete deadline formatted as YYYY-MM-DD. "
                    "Return null if no concrete date is provided."
    )

    timeline_notes: str | None = Field(
    description=(
        "Additional vague, approximate, or conditional timing "
        "information not already represented by deadline. "
        "Do not repeat a concrete deadline. Return null when "
        "no additional timeline context is provided."
    )
)

    missing_information: list[str] = Field(
        description="Important project information not yet provided."
    )

    extraction_confidence: Literal["high", "medium", "low"]

    constraints: list[str] = Field(
        description="Explicit project restrictions and negative requirements."
    )

    budget_notes: str | None = Field(
        description=(
            "Additional budget qualifications, flexibility, or ranges. "
            "Return null if no additional budget context is provided."
        )
    )