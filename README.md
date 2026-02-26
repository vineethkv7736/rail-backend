# RailPro AI Backend

## Overview
This is the FastAPI backend for RailPro AI, a region-first Indian Railway assistant.

## Setup
1.  **Install Python 3.10+**.
2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Environment Variables**:
    -   Copy `.env.example` to `.env`.
    -   Add your `GEMINI_API_KEY`.
    -   Add path to `GOOGLE_APPLICATION_CREDENTIALS` json file (for TTS).
    -   (Optional) `RAILWAY_API_KEY` calls.

## Running the Server
```bash
uvicorn app.main:app --reload
```

## API Endpoints
-   `POST /api/v1/chat/text`: Main chat interface.
    -   Body: `{"message": "Is train 12617 late?"}`
    -   Response: `{"response": "...", "audio_url": "..."}`

## Features
-   **Gemini 1.5 Flash**: Fast, consistently updated LLM.
-   **Auto-Tool Calling**: Can fetch (mock) live train status.
-   **Region-First**: Detects language and responds in kind using TTS.
-   **JSON Output**: Structured responses for frontend parsing.
