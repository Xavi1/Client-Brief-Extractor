
from ollama import AsyncClient
from pydantic import ValidationError

from app.schemas import ClientBrief
from app.services.extraction_prompts import EXTRACTION_INSTRUCTIONS


client = AsyncClient(host="http://localhost:11434")

MODEL_NAME = "qwen3:4b"


class LocalBriefExtractionError(Exception):
    """Raised when local AI extraction fails."""


async def extract_client_brief_local(message: str) -> ClientBrief:

    if not message or len(message.strip()) < 10:
        raise LocalBriefExtractionError(
            "Message is too short or empty."
        )

    try:
        response = await client.chat(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": EXTRACTION_INSTRUCTIONS
                },
                {
                    "role": "user",
                    "content": (
                        f"Extract the client brief from this message:\n\n"
                        f"{message}"
                    )
                }
            ],
            format=ClientBrief.model_json_schema(),
            options={
                "temperature": 0
            }
        )

        result = ClientBrief.model_validate_json(
            response.message.content
        )

        return result

    except ValidationError as exc:
        raise LocalBriefExtractionError(
            "Local AI returned data that failed schema validation."
        ) from exc

    except Exception as exc:
        raise LocalBriefExtractionError(
            f"Local extraction failed: {str(exc)}"
        ) from exc
