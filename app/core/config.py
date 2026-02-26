from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "RailPro AI API"
    API_V1_STR: str = "/api/v1"
    
    # Gemini
    GEMINI_API_KEY: str

    # Google Cloud TTS
    GOOGLE_APPLICATION_CREDENTIALS: str = "" # Path to JSON key file

    # Railway API (Placeholder)
    RAILWAY_API_KEY: str = ""
    
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()
