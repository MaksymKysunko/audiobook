# hello_one_voice_exact.py
import pyttsx3, sys
VOICE_ID = r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0"
e = pyttsx3.init('sapi5')
e.setProperty("voice", VOICE_ID)
print("Selected:", e.getProperty("voice"))
e.say("Hello world with Zira.")
e.runAndWait()