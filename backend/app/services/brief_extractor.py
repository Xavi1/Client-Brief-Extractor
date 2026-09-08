# app/services/brief_extractor.py
from app.schemas import ClientBrief


class BriefExtractionError(Exception):
    """Raised when the model cannot produce a valid client brief."""


async def extract_client_brief(message: str) -> ClientBrief:
    # Replace this temporary implementation with the provider API call.
    return ClientBrief(
        client_name=None,
        business_type=None,
        project_type="Unknown",
        requested_features=[],
        budget=None,
        currency=None,
        deadline=None,
        missing_information=[
            "Model integration has not been implemented"
        ],
    )