# нейронний онлайн-TTS (без ключа): edge-tts
import asyncio
import edge_tts

async def _speak_to_mp3_async(text: str, mp3_out: str, voice: str = "en-US-AriaNeural", rate: str = "+0%", volume: str = "+0%"):
    tts = edge_tts.Communicate(text, voice=voice, rate=rate, volume=volume)
    with open(mp3_out, "wb") as f:
        async for chunk in tts.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])

def speak_to_mp3(text: str, mp3_out: str, voice: str = "en-US-AriaNeural", rate: str = "+0%", volume: str = "+0%"):
    asyncio.run(_speak_to_mp3_async(text, mp3_out, voice=voice, rate=rate, volume=volume))
