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
    -   Add `RAILRADAR_API_KEY` for live train status and station search.
    -   Add `INDIAN_RAIL_API_KEY` for PNR and seat availability.
    -   `RAILWAY_API_KEY` is kept only as a legacy fallback for RailRadar.
    -   Optional overrides:
        -   `RAILWAY_API_BASE_URL=https://indianrailapi.com/api/v2`
        -   `RAILWAY_LIVE_STATUS_BASE_URL=https://api.railradar.in/api/v1`

## Running the Server
```bash
uvicorn app.main:app --reload
```

## API Endpoints
-   `POST /api/v1/chat/text`: Main chat interface.
    -   Body: `{"message": "Is train 12617 late?"}`
    -   Response: `{"response": "...", "audio_url": "..."}`
-   `GET /api/v1/trains/status?train_number=12627`
-   `GET /api/v1/trains/pnr?pnr=1234567890`
-   `GET /api/v1/trains/seat-availability?train_number=12627&from_station=SBC&to_station=NDLS&journey_date=20-03-2026&class_code=3A&quota=GN`
-   `POST /api/v1/trains/booking`
    -   Returns a clear message that booking is not supported through a free public API.

## Features
-   **Gemini 1.5 Flash**: Fast, consistently updated LLM.
-   **Auto-Tool Calling**: Can fetch live train status, PNR status, and seat availability.
-   **Region-First**: Detects language and responds in kind using TTS.
-   **JSON Output**: Structured responses for frontend parsing.
-   **Booking Guardrail**: Free/public booking is intentionally not faked because IRCTC booking requires an authorized partner integration.
-   **Explicit Provider Errors**: PNR and seat availability now return real provider/config errors instead of silently serving mock data.
