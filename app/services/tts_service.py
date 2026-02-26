from google.cloud import texttospeech
from app.core.config import settings
import base64
import os

class TTSService:
    def __init__(self):
        # Explicitly set the env var for the Google Client Library
        if settings.GOOGLE_APPLICATION_CREDENTIALS:
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = settings.GOOGLE_APPLICATION_CREDENTIALS
            
        self.enabled = False
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
             try:
                self.client = texttospeech.TextToSpeechClient()
                self.enabled = True
             except Exception as e:
                print(f"Warning: TTS Client init failed: {e}")
        else:
             print("Warning: GOOGLE_APPLICATION_CREDENTIALS not set. TTS disabled.")

    async def synthesize(self, text: str, language_code: str = "en-IN") -> str:
        """
        Synthesizes text to speech and returns base64 encoded MP3 string.
        """
        if not self.enabled:
            return ""

        # Clean Markdown characters for TTS
        import re
        clean_text = re.sub(r'[*_`~|]', '', text) # Remove bold/italic/code/table markers
        clean_text = re.sub(r'#{1,6}\s?', '', clean_text) # Remove headers
        clean_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', clean_text) # Remove links but keep text
        clean_text = re.sub(r'[-]{3,}', '', clean_text) # Remove horizontal rules

        input_text = texttospeech.SynthesisInput(text=clean_text)

        # Basic voice selection - can be enhanced to map input language to specific voice
        # Mappings: ml-IN (Malayalam), en-IN (English), hi-IN (Hindi)
        voice_params = texttospeech.VoiceSelectionParams(
            language_code=language_code,
            ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
        )

        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.MP3
        )

        try:
            response = self.client.synthesize_speech(
                request={"input": input_text, "voice": voice_params, "audio_config": audio_config}
            )
            return base64.b64encode(response.audio_content).decode("utf-8")
        except Exception as e:
            print(f"TTS Error: {e}")
            return ""

tts_service = TTSService()
