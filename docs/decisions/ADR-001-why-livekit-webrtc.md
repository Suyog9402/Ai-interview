# ADR-001: Why LiveKit WebRTC Over Raw WebSockets

## Context
Building a conversational voice AI interviewer requires bidirectional audio streaming with minimal latency (<500ms), robust jitter buffering, natural user interruption support, and server-side voice activity detection (VAD).

## Options Considered
1. **Raw WebSockets (Custom Audio Streaming)**
   - *Pros*: Full protocol control, no third-party media server dependencies.
   - *Cons*: High development overhead for jitter buffer management, packet loss concealment, echo cancellation, and network degradation handling over TCP/WebSocket framing.
2. **LiveKit WebRTC Agent Framework (Chosen)**
   - *Pros*: Sub-200ms glass-to-glass latency over UDP/WebRTC, built-in Silero VAD, native interruption handling, automated room orchestration, and integration with Deepgram Nova-2 STT, Groq Qwen 2.5 LLM, and Deepgram Aura TTS.
   - *Cons*: Requires LiveKit server instance or cloud endpoint.

## Decision
We chose **LiveKit WebRTC**. Its native media transport, turn detection plugins, and noise cancellation allow us to deliver a natural, conversational interview experience while maintaining a clean, modular Python backend agent.
