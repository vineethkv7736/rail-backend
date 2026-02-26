# Backend Execution Plan: RailPro AI

This document outlines the step-by-step execution plan to build the FastAPI backend for the RailPro AI assistant, specifically tailored to the User Stories provided.

## Core Philosophy
- **Region-First**: The architecture transforms all inputs to English for processing and all outputs back to the user's regional language.
- **Agentic**: The system is not just a router; it is a conversational agent that manages state (missing information).
- **Human-Centric**: Responses are parsed to provide "Advice" rather than just "Data".

---

## Phase 1: Project Scaffolding & Configuration
**Goal**: Set up a robust, scalable FastAPI environment.

1.  **Initialize Project Structure**:
    -   Standard directory layout (`app/main, app/api, app/services, app/core`).
    -   Poetry or pip requirements management.
2.  **Environment Setup**:
    -   Configure `.env` for API Keys (OpenAI/Gemini, Railway API, STT/TTS services).
3.  **Database Integration** (Lightweight for MVP):
    -   SQLite/PostgreSQL to store *Conversation History* (essential for User Story 2 - Context).
    -   Redis (optional but recommended) for caching real-time train status to reduce API costs (User Story 7).

## Phase 2: The "Interpreter" Agent (LLM Integration)
**Goal**: Handle Region-First inputs and Fuzzy Intents (User Stories 1, 2, 6).

1.  **Service Layer - `LLMService`**:
    -   **Provider**: **Google Gemini** (via `google-generativeai`).
    -   **System Prompt Engineering**: Create the "Persona" that answers calmly, checks for missing info, and speaks simply.
2.  **Intent Classification Pipeline**:
    -   Incoming text (e.g., "എറണാകുളം ബാംഗ്ലൂർ") -> Detect Language -> Translate to English (using Gemini).
    -   Analyze Intent: `CHECK_STATUS`, `EXPLAIN_TERM`, `BOOKING_HELP`, `GENERAL_QUERY`.
3.  **Slot Filling Module (User Story 2)**:
    -   If Intent is `CHECK_STATUS` but variables (Source, Dest, or specific Train) are missing:
        -   Start `SlotFillingLoop`: Return a question "Which station are you starting from?" (translated back to user language).

## Phase 3: Railway Data Layer
**Goal**: Fetch accurate data to feed the Interpreter (User Stories 1, 7).

1.  **External API Integration**:
    -   Integrate with a Live Train Status API (e.g., IRCTC wrapper, RapidAPI, or similar).
    -   Implement `TrainService` with methods: `get_schedule`, `get_live_status`, `check_pnr`.
2.  **Data Humanizer Middleware (User Story 4)**:
    -   Raw API says: `{"delay": 47, "status": "ACT"}`
    -   Middleware logic:
        -   If `delay` < 15: "On time."
        -   If `delay` > 30: "Delayed, but safe to wait."
        -   Add Advice: "Boarding not started" based on status.

## Phase 4: Voice & Multi-Modal Support
**Goal**: "I can speak, but I don't want to type" (User Story 3).

1.  **Speech-to-Text (STT)**:
    -   Endpoint `/api/v1/chat/audio`.
    -   Receive `blob` -> Transcribe (using Whisper or Google Speech).
    -   Pass transcription to the **Interpreter Agent**.
2.  **Text-to-Speech (TTS)**:
    -   **Provider**: **Google Cloud TTS** (via `google-cloud-texttospeech`).
    -   Take the LLM's final regional response -> Generate Audio.
    -   Return audio to frontend for auto-play.

## Phase 5: Trust & Education Modules
**Goal**: Booking help and Terminology (User Stories 5, 6).

1.  **Deep Link Generator**:
    -   If Intent is `BOOK_TICKET`:
        -   Do NOT attempt to book.
        -   Generate dynamic link: `https://www.irctc.co.in/nget/booking/train-list?stnOrigin={src}&stnDest={dest}`.
        -   Response: "I cannot take money, but here is the official IRCTC link for [Source] to [Dest]."
2.  **Knowledge Base (RAG - Optional or Prompt-based)**:
    -   Embed definitions for RAC, WL, PNR, GNWL into the system prompt so it explains them simply (User Story 6).

## Phase 6: API Endpoint Definition
**Goal**: Clean interface for the frontend.

-   `POST /auth/guest`: Create a temporary session/user ID (so we can track conversation context).
-   `POST /chat/text`:
    -   Body: `{ "message": "...", "language": "ml", "session_id": "..." }`
    -   Response: `{ "text": "...", "audio_url": "...", "actions": [...] }`
-   `POST /chat/voice`:
    -   Multipart Form Data (Audio File).
    -   Returns same as text endpoint.

## Phase 7: Validation & "Freshness" Checks
**Goal**: User Story 7.

1.  **Timestamp injection**: Every response about time must include "Updated at [Time]" in the body.
2.  **Sanity Check**: If the External API is down or data is stale (>30 mins), the LLM must prefix: "I cannot get live data right now..."

## Execution Order
1.  **Setup**: FastAPI scaffold + Env variables.
2.  **Spike**: Verify External Railway API works.
3.  **Core**: Build the standard Chat endpoint with LLM (No voice yet).
4.  **Data**: Connect Chat endpoint to Railway API tools.
5.  **Voice**: Add STT/TTS wrappers.
6.  **Refine**: Add the "Humanizer" formatting logic.
