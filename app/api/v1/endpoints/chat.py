from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services.llm_service import llm_service
from app.core.prompts import SYSTEM_PERSONA

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    language: str | None = None # Explicit language override

class ChatResponse(BaseModel):
    response: str
    audio_url: str | None = None
    debug_info: dict | None = None

@router.post("/text", response_model=ChatResponse)
async def chat_text(request: ChatRequest):
    """
    Main chat endpoint.
    Passes text to LLM, parses JSON response, and generates TTS audio.
    """
    try:
        # 1. Get LLM Response
        llm_result = await llm_service.generate_response(
            request.message, 
            system_instruction=SYSTEM_PERSONA,
            session_id=request.session_id
        )
        
        # 2. Extract Data
        response_text = llm_result.get("text", "I'm sorry, I couldn't process that.")
        language_code = llm_result.get("language_code", "en-IN")
        debug_info = llm_result.get("debug_info", {})
        
        # 3. Generate Audio (Async)
        audio_b64 = ""
        from app.services.tts_service import tts_service
        if tts_service.enabled:
             audio_b64 = await tts_service.synthesize(response_text, language_code=language_code)

        return ChatResponse(
            response=response_text,
            audio_url=f"data:audio/mp3;base64,{audio_b64}" if audio_b64 else None,
            debug_info=debug_info
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
