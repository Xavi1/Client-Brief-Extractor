# app/services/brief_extractor.py
import traceback
from google import genai
from google.genai import types
from app.schemas import ClientBrief
from app.settings import settings

class BriefExtractionError(Exception):
    """Raised when the model cannot produce a valid client brief."""

# Initialize the Gemini Client
client = genai.Client(api_key=settings.MODEL_API_KEY)

async def extract_client_brief(message: str) -> ClientBrief:
    try:
        prompt = (
            "You are an expert system analyst. Analyze the following raw client message, email, "
            f"or brief and extract all relevant details accurately.\n\nClient Message:\n{message}"
        )
        
        # Enforce JSON output mode explicitly
        response = await client.aio.models.generate_content(
            model=settings.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json"
            ),
        )
        
        if not response.text:
            raise ValueError("Gemini returned an empty response.")

        # Clean markdown wrappers if Gemini returned them (e.g., ```json ... ```)
        clean_text = response.text.strip()
        if clean_text.startswith("```"):
            lines = clean_text.splitlines()
            if lines[0].startswith("```json") or lines[0].startswith("```"):
                clean_text = "\n".join(lines[1:-1])

        # Validate the JSON data cleanly against your Pydantic schema
        return ClientBrief.model_validate_json(clean_text)
        
    except Exception as e:
        # CRITICAL: This will dump the full, raw trace into your uvicorn window so you can read it.
        print("\n=== SYSTEM CRASH DETAILED TRACEBACK ===")
        traceback.print_exc()
        print("========================================\n")
        raise BriefExtractionError(f"Failed to extract client brief: {str(e)}")
