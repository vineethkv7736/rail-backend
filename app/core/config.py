from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    PROJECT_NAME: str = "RailPro AI API"
    API_V1_STR: str = "/api/v1"
    
    # Gemini
    GEMINI_API_KEY: str

    # Google Cloud TTS
    GOOGLE_APPLICATION_CREDENTIALS: str = "" # Path to JSON key file

    # Legacy fallback key for older configs
    RAILWAY_API_KEY: str = ""
    RAILRADAR_API_KEY: str = ""
    INDIAN_RAIL_API_KEY: str = ""
    RAILWAY_API_BASE_URL: str = "https://indianrailapi.com/api/v2"
    RAILWAY_LIVE_STATUS_BASE_URL: str = "https://api.railradar.in/api/v1"
    
    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True)

settings = Settings()
