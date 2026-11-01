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
    default=None,
    description=(
        "The name of the company or business associated "
        "with the project. For example, Oak & Home. "
        "Return null if no company name is provided."
    )
)
    business_type: str | None = None
    project_type: str
    requested_features: list[str]
    budget: float | None = Field(
    default=None,
    ge=0,
    description=(
        "The numeric budget amount only, without currency symbols "
        "or formatting. For example, PHP 120,000 must be extracted "
        "as 120000. Return null only if no budget amount is stated."
    )
)
    currency: str | None = Field(
    default=None,
    description=(
        "The ISO 4217 currency code associated with the budget. "
        "For example, PHP for Philippine pesos, USD for US dollars. "
        "Extract the currency whenever it is explicitly stated."
    )
)

    deadline: str | None = None
    timeline_notes: str | None = None
    missing_information: list[str] = Field(
    default_factory=list,
    description=(
        "Important project information that the client has not "
        "provided. Include the budget if no budget amount was given. "
        "Do not list the budget as missing when an amount was supplied."
    )
)
    extraction_confidence: Literal["high", "medium", "low"]
    constraints: list[str] = Field(default_factory=list)
    budget_notes: str | None = None