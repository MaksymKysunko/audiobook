import pyttsx3

def synth_to_wav(text: str, out_wav: str, rate: int = 175, volume: float = 1.0, voice_id: str | None = None):
    # явний драйвер SAPI5 на Windows; на інших платформах init() без параметрів
    try:
        engine = pyttsx3.init('sapi5')
    except Exception:
        engine = pyttsx3.init()
    if voice_id:
        engine.setProperty("voice", voice_id)
    engine.setProperty("rate", rate)
    engine.setProperty("volume", volume)
    engine.save_to_file(text, out_wav)
    engine.runAndWait()
