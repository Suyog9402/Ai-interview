from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
import logging
import asyncio
from backend.main import Assistant, AgentSession, RoomInputOptions, RoomOutputOptions, noise_cancellation, openai, TurnDetection, metrics
import os

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store
sessions = {}

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

class VoiceAgentSession:
    def __init__(self):
        self.session = AgentSession(
            llm=openai.realtime.RealtimeModel(
                model="gpt-4o-realtime-preview",
                api_key=os.getenv("OPENAI_API_KEY"),
                turn_detection=TurnDetection(
                    type="server_vad",
                    threshold=0.5,
                    prefix_padding_ms=300,
                    silence_duration_ms=500,
                    create_response=True,
                    interrupt_response=True,
                )
            ),
        )
        self.assistant = Assistant()
        self.room = type("DummyRoom", (), {"name": f"api-room-{uuid.uuid4()}"})()
        self.usage_collector = metrics.UsageCollector()
        self.session.on("metrics_collected")(self._on_metrics_collected)
        self.session_started = False

    def _on_metrics_collected(self, ev):
        metrics.log_metrics(ev.metrics)
        self.usage_collector.collect(ev.metrics)

    async def start(self):
        if not self.session_started:
            await self.session.start(
                agent=self.assistant,
                room=self.room,
                room_input_options=RoomInputOptions(
                    noise_cancellation=noise_cancellation.BVC(),
                ),
                room_output_options=RoomOutputOptions(transcription_enabled=True),
            )
            self.session_started = True

    async def send_message(self, message: str) -> str:
        await self.start()
        handle = self.session.generate_reply(user_input=message)
        await handle
        assistant_messages = [item for item in handle.chat_items if getattr(item, 'type', None) == 'message' and getattr(item, 'role', None) == 'assistant']
        if assistant_messages:
            return assistant_messages[-1].text_content or ""
        return "[No response]"

    def close(self):
        pass

@app.post("/session/start")
async def start_session():
    session_id = str(uuid.uuid4())
    sessions[session_id] = VoiceAgentSession()
    return {"session_id": session_id}

@app.post("/session/{session_id}/chat", response_model=ChatResponse)
async def chat(session_id: str, request: ChatRequest):
    session = sessions.get(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    response = await session.send_message(request.message)
    return ChatResponse(response=response)

@app.post("/session/{session_id}/end")
async def end_session(session_id: str):
    session = sessions.pop(session_id, None)
    if session:
        session.close()
    return {"status": "ended"} 