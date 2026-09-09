# app/services/brief_extractor.py
import traceback
from google import genai
from google.genai import types
from app.schemas import ClientBrief
from app.settings import settings

class BriefExtractionError(Exception):
    """Raised when the model cannot produce a valid client brief."""

client = genai.Client(api_key=settings.MODEL_API_KEY)

async def extract_client_brief(message: str) -> ClientBrief:
    try:
        # Guard clause for short/invalid messages
        if not message or len(message.strip()) < 10:
            raise BriefExtractionError("Message is too short or empty to extract a valid client brief.")

        prompt = (
            "You are an expert system analyst. Analyze the following raw client message, email, "
            f"or brief and extract all relevant details accurately.\n\nClient Message:\n{message}"
        )
        
        response = await client.aio.models.generate_content(
            model=settings.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ClientBrief,
                temperature=0.1,
            ),
        )
        
        if not response.parsed:
            raise ValueError("Gemini returned a response, but it could not be parsed into the schema.")

        return response.parsed
        
    except Exception as e:
        if not isinstance(e, BriefExtractionError):
            print("\n=== SYSTEM CRASH DETAILED TRACEBACK ===")
            traceback.print_exc()
            print("========================================\n")
        raise BriefExtractionError(f"Failed to extract client brief: {str(e)}")