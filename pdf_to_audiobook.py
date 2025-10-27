import argparse
import os
import re

import pyttsx3
from PyPDF2 import PdfReader
import subprocess
import shutil

voices = {
    "david": r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_DAVID_11.0",
    "zira":  r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_EN-US_ZIRA_11.0",
    "irina": r"HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\TTS_MS_RU-RU_IRINA_11.0",
}



def wav_to_mp3_ffmpeg(wav_path: str, mp3_path: str, bitrate: str = "192k"):
    ffmpeg_path = shutil.which("ffmpeg")
    if not ffmpeg_path:
        raise RuntimeError("ffmpeg не знайдено у PATH")
    print(f"Конвертація через ffmpeg: {wav_path} → {mp3_path}")
    subprocess.run([
        ffmpeg_path,
        "-y",  # перезаписати, якщо існує
        "-i", wav_path,
        "-vn",
        "-ar", "44100",
        "-ac", "2",
        "-b:a", bitrate,
        mp3_path
    ], check=True)

def normalize_pdf_text(raw: str) -> str:
    s = raw
    # склеїти перенос на дефісі: "сло-\nво" -> "слово"
    s = re.sub(r"-\s*\n\s*", "", s)
    # перенести абзаци в пробіли
    s = s.replace("\r", "\n")
    s = re.sub(r"\n+", "\n", s)      # звести кілька \n до одного
    s = s.replace("\n", " ")
    # прибрати зайві пробіли
    s = re.sub(r"[ \t]+", " ", s).strip()
    return s

def read_pdf_text(pdf_path: str, start: int = 1, end: int | None = None) -> str:
    reader = PdfReader(pdf_path)
    total = len(reader.pages)
    if end is None or end > total:
        end = total
    if start < 1 or start > end:
        raise ValueError("Невірний діапазон сторінок.")

    chunks = []
    for i in range(start - 1, end):
        page = reader.pages[i]
        txt = page.extract_text() or ""
        txt = normalize_pdf_text(txt)
        chunks.append(txt.strip())

    return "\n\n".join(filter(None, chunks))

def synth_to_wav(text, out_wav, rate=None, volume=None, voice=None):
    try:
        engine = pyttsx3.init('sapi5')
    except Exception:
        engine = pyttsx3.init()    
    vid = voices[voice]
    if vid:
        engine.setProperty("voice", vid)
    if rate is not None:
        engine.setProperty("rate", rate)
    if volume is not None:
        engine.setProperty("volume", volume)
    engine.save_to_file(text, out_wav)
    engine.runAndWait()


def main():
    ap = argparse.ArgumentParser(description="Convert PDF to audiobook (WAV) using PyPDF2 + pyttsx3.")
    ap.add_argument("pdf", help="Шлях до PDF")
    ap.add_argument("-o", "--out", help="Вихідний файл (WAV). За замовчуванням як у PDF, але .wav", default=None)
    ap.add_argument("--start", type=int, default=1, help="Початкова сторінка (1-індекс).")
    ap.add_argument("--end", type=int, default=None, help="Кінцева сторінка (включно).")
    ap.add_argument("--rate", type=int, default=None, help="Швидкість голосу (прибл. 150–220).")
    ap.add_argument("--volume", type=float, default=None, help="Гучність 0.0–1.0.")
    ap.add_argument("--mp3", action="store_true", help="Після створення WAV конвертувати в MP3 (потрібні pydub + ffmpeg).")
    ap.add_argument("--voice", choices=voices.keys(), help="Оберіть голос: " + ", ".join(voices.keys()))

    args = ap.parse_args()

    out_wav = args.out or os.path.splitext(args.pdf)[0] + ".wav"

    print("Читаю PDF…")
    text = read_pdf_text(args.pdf, start=args.start, end=args.end)
    if not text.strip():
        raise SystemExit("У PDF не знайдено текст (можливо, це скани — потрібен OCR).")

    print(f"Синтез у {out_wav}…")
    synth_to_wav(text, out_wav, rate=args.rate, volume=args.volume, voice=args.voice)
    print("Готово: ", out_wav)

    if args.mp3:
        try:
            mp3_path = os.path.splitext(out_wav)[0] + ".mp3"
            wav_to_mp3_ffmpeg(out_wav, mp3_path)
            print("Готово:", mp3_path)
        except Exception as e:
            print("Помилка під час конвертації у MP3:", e)

if __name__ == "__main__":
    main()
