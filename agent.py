from dotenv import load_dotenv
from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions
from livekit.agents import llm
from livekit.plugins import google, silero, deepgram, openai
from prompts import AGENT_INSTRUCTION, SESSION_INSTRUCTION
from tools import get_weather, search_web, send_email, play_music, set_volume, control_media
from voice_auth import is_boss, record_snippet
import asyncio
import logging
import os

load_dotenv()

SLEEP_PHRASES = ["friday go offline", "go offline", "go to sleep", "friday sleep"]
WAKE_PHRASES  = ["hey friday", "friday wake up", "wake up friday", "friday online"]


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=AGENT_INSTRUCTION)
        self.is_awake = True

    async def on_user_turn_completed(
        self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage
    ) -> None:
        text = (new_message.text_content or "").lower().strip()
        logging.info(f"[FRIDAY] Heard: '{text}' | Awake: {self.is_awake}")

        if not self.is_awake:
            if any(p in text for p in WAKE_PHRASES):
                self.is_awake = True
                new_message.content = ["I am back online, how can I help?"]
                await super().on_user_turn_completed(turn_ctx, new_message)
            else:
                new_message.content = []
            return

        if any(p in text for p in SLEEP_PHRASES):
            self.is_awake = False
            new_message.content = ["Going offline. Say 'Hey Friday' to wake me up."]
            return

        await super().on_user_turn_completed(turn_ctx, new_message)

async def entrypoint(ctx: agents.JobContext):
    await ctx.connect()

    vad = silero.VAD.load()
    llm_model = openai.LLM(
        model="llama-3.3-70b-versatile",
        base_url="https://api.groq.com/openai/v1",
        api_key=os.getenv("GROQ_API_KEY"),
    )
    stt_model = deepgram.STT()
    tts_model = google.TTS(voice_name="en-US-Journey-F",model_name="chirp_3")

    session = AgentSession(
        llm=llm_model,
        stt=stt_model,
        tts=tts_model,
        vad=vad,
        tools=[get_weather, search_web, send_email, play_music, set_volume, control_media],
    )

    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_input_options=RoomInputOptions(
            video_enabled=False,
        ),
    )

    await session.generate_reply(instructions=SESSION_INSTRUCTION)


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))