import os
from fastapi import APIRouter, HTTPException
from typing import List
from google import genai
from google.genai import types

from app.schemas.gemini import GeminiChatRequest, GeminiChatResponse
from app.config import settings

router = APIRouter()


@router.post("/chat", response_model=GeminiChatResponse)
def chat_with_gemini(req: GeminiChatRequest):
    """
    Send a message to Google Gemini. 
    Tries GEMINI_API_KEY first (Google AI Studio).
    Falls back to Vertex AI if an API key is not present.
    """
    try:
        # 1. Initialize Client
        if settings.GEMINI_API_KEY:
            # Use Standard Gemini Developer API
            client = genai.Client(api_key=settings.GEMINI_API_KEY)
        else:
            # Use Vertex AI
            project_id = settings.GOOGLE_CLOUD_PROJECT
            if not project_id:
                raise HTTPException(status_code=500, detail="GOOGLE_CLOUD_PROJECT not configured in .env")
            client = genai.Client(vertexai=True, project=project_id, location="us-central1")
        
        # 2. Build Chat History
        contents = []
        for msg in req.history:
            contents.append(
                types.Content(
                    role=msg.role, 
                    parts=[types.Part.from_text(msg.text)]
                )
            )
        
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part.from_text(req.message)]
            )
        )
        
        # 3. Generate Content
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction="You are a helpful AI Assistant for a cybersecurity and IT incident management dashboard at Deutsche Bank.",
                temperature=0.7,
            )
        )
        
        return GeminiChatResponse(response=response.text)

    except Exception as e:
        print(f"[Gemini Error] {e}")
        # Return a cleaner error message to the frontend if ADC fails
        error_msg = str(e)
        if "default credentials were not found" in error_msg or "metadata server" in error_msg:
            raise HTTPException(
                status_code=500, 
                detail="Vertex AI ADC missing. Please add GEMINI_API_KEY to your .env file or configure GOOGLE_APPLICATION_CREDENTIALS."
            )
        raise HTTPException(status_code=500, detail=error_msg)

