# app/services/brief_extractor.py
from google import genai
from google.genai import types
from app.schemas import ClientBrief
from app.settings import settings

class BriefExtractionError(Exception):
    """Raised when the model cannot produce a valid client brief."""

# Initialize the Gemini Client using your settings layer
client = genai.Client(api_key=settings.MODEL_API_KEY)

async def extract_client_brief(message: str) -> ClientBrief:
    try:
        prompt = (
            "You are an expert system analyst. Analyze the following raw client message, email, "
            "or brief. Extract all relevant details into the structured format provided. "
            "If any crucial details like budget, deadline, or required features are vague or missing, "
            "list exactly what information is missing so we can ask the client for clarification.\n\n"
            f"Client Message:\n{message}"
        )
        
        # Use Gemini's structured output capability
        response = client.models.generate_content(
            model=settings.MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ClientBrief,
            ),
        )
        
        # response.text is guaranteed to be a valid JSON matching ClientBrief
        return ClientBrief.model_validate_json(response.text)
        
    except Exception as e:
        # Catch connection errors, API errors, or validation issues
        raise BriefExtractionError(f"Failed to extract client brief: {str(e)}")
