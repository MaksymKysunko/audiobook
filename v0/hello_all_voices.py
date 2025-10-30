# hello_all_voices_reinit.py
import time
import pyttsx3

# ВАЖЛИВО: на Windows краще явно вказати драйвер SAPI5
def speak_with_voice(voice_id: str, text: str, rate: int = 175, volume: float = 1.0):
    e = pyttsx3.init(driverName='sapi5')
    e.setProperty("voice", voice_id)
    e.setProperty("rate", rate)
    e.setProperty("volume", volume)
    # діагностика: переконаємось, що справді встановився потрібний ID
    current = e.getProperty("voice")
    print(f"→ Using voice: {current}")
    e.say(text)
    e.runAndWait()
    e.stop()
    del e  # звільняємо COM-ресурси
    time.sleep(0.2)

if __name__ == "__main__":
    # спочатку читаємо всі доступні
    probe = pyttsx3.init(driverName='sapi5')
    voices = probe.getProperty("voices")
    print("Found voices:")
    for i, v in enumerate(voices, 1):
        print(f"  [{i}] {getattr(v, 'name', '')}  |  {v.id}")
    probe.stop()

    print("\nSpeaking with each voice:")
    for v in voices:
        speak_with_voice(v.id, "Hello world. This is a voice test.", rate=100, volume=1.0)
