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
                response_mime_type="application/json",
                response_schema=ClientBrief,  # <-- Native schema binding
                temperature=0.1,             # Low temperature for precise, deterministic extraction
            ),
        )
        
        if not response.text:
            raise ValueError("Gemini returned a response, but it could not be parsed into the schema.")
        return response.parsed
        
    except Exception as e:
        # CRITICAL: This will dump the full, raw trace into your uvicorn window so you can read it.
        print("\n=== SYSTEM CRASH DETAILED TRACEBACK ===")
        traceback.print_exc()
        print("========================================\n")
        raise BriefExtractionError(f"Failed to extract client brief: {str(e)}")
