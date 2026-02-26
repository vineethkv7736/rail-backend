# Frontend Execution Plan: RailPro Kiosk

This document outlines the plan to build the RailPro Kiosk Frontend using Next.js.
**Target Device**: Tablet (Kiosk Mode).
**Core Philosophy**: Touch-first, Voice-first, High Accessibility, "Wow" Aesthetics.

## Phase 1: Project Setup
1.  **Initialize Next.js App**:
    -   `npx create-next-app@latest frontend`
    -   TypeScript, Tailwind CSS, ESLint.
2.  **Install Dependencies**:
    -   `framer-motion`: For smooth, premium animations (User Story: "Wow" factor).
    -   `lucide-react`: For clear, high-contrast icons.
    -   `axios` or `ky`: For API requests.
    -   `zustand`: For simple state management (conversation history, audio state).
    -   `react-use-audio-player` or native Audio API: For playing TTS responses.

## Phase 2: Design System (Kiosk Focused)
1.  **Tailwind Configuration**:
    -   Define a "RailPro" color palette:
        -   Primary: Vibrant Railway Blue/Orange (High visibility).
        -   Background: Deep Dark Mode (OLED friendly, reduces eye strain).
        -   Text: Large, readable fonts (Inter or Outfit).
2.  **Global Styles**:
    -   Disable text selection (Kiosk mode).
    -   Hide scrollbars where possible.
    -   Enforce touch-action manipulation.

## Phase 3: Core Components
1.  **`VoiceOrb`**:
    -   The central interaction point.
    -   Animated, glowing orb that reacts to "Listening", "Processing", and "Speaking" states.
2.  **`ChatInterface`**:
    -   Large chat bubbles.
    -   Auto-scroll to bottom.
    -   "Quick Action" chips (e.g., "Is my train late?", "Where is the platform?").
3.  **`LiveStatusCard`**:
    -   A visually rich card to display train status (Delay, Location) when detected in the response.
    -   Big, bold numbers.
    -   Color-coded status (Green = On Time, Red = Late).

## Phase 4: Integration
1.  **Audio Recording**:
    -   Implement `MediaRecorder` API to capture voice.
    -   Send blob to Backend STT (or use browser SpeechRecognition as fallback/MVP).
2.  **Backend Connection**:
    -   Connect to `http://localhost:8000/api/v1/chat/text` (and voice endpoint later).
    -   Handle TTS audio playback automatically on response.

## Phase 5: Kiosk Specifics
1.  **Idle Reset**:
    -   If no interaction for 60s, reset conversation to "Welcome" screen.
2.  **Language Toggle**:
    -   Big, always-visible language switcher (Malayalam / English / Hindi).

## Execution Steps
1.  Scaffold Project.
2.  Setup Tailwind & Fonts.
3.  Build the "Welcome / Idle" Screen.
4.  Build the "Active Conversation" Screen.
5.  Integrate API.
