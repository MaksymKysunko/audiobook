import argparse
from .paths import out_paths_for_pdf
from .pdf_reader import read_pdf_text
from .text_clean import normalize_text
from .markup import load_markup, save_markup_draft, make_markup_draft
from .encode import wav_to_mp3_ffmpeg
from .tts.pyttsx_engine import synth_to_wav
from .tts.voices import VOICES

def main():
    ap = argparse.ArgumentParser(prog="audiobooker")
    ap.add_argument("pdf", nargs="?", help="Шлях до PDF. Не потрібен для --encode-only.")
    ap.add_argument("--voice", choices=VOICES.keys(), help=f"Голос: {', '.join(VOICES.keys())}")
    ap.add_argument("--rate", type=int, default=175)
    ap.add_argument("--volume", type=float, default=1.0)
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=None)
    ap.add_argument("--mp3", action="store_true", help="Одразу стискати WAV у MP3")
    ap.add_argument("--bitrate", type=str, default="48k")
    ap.add_argument("--ar", type=int, default=22050)
    ap.add_argument("--stereo", action="store_true")
    ap.add_argument("--make-markup", action="store_true", help="Згенерувати чернетку *.chapters.txt")
    ap.add_argument("--encode-only", action="store_true", help="Стиснути існуючий WAV у MP3")
    ap.add_argument("--in-wav", type=str, default=None, help="Вхідний WAV для --encode-only")

    args = ap.parse_args()

    # Швидкий шлях: лише стискати WAV → MP3
    if args.encode_only:
        if not args.in_wav:
            raise SystemExit("--encode-only потребує --in-wav")
        mp3_out = args.in_wav.rsplit(".", 1)[0] + ".mp3"
        wav_to_mp3_ffmpeg(args.in_wav, mp3_out, bitrate=args.bitrate, ar=args.ar, mono=not args.stereo)
        print("MP3:", mp3_out)
        return

    if not args.pdf:
        ap.error("Потрібен шлях до PDF")

    # Чернетка розмітки
    if args.make_markup:
        draft = make_markup_draft(args.pdf)
        mp = save_markup_draft(args.pdf, draft)
        print("Draft written:", mp)
        return

    voice_id = VOICES.get(args.voice) if args.voice else None
    outs = out_paths_for_pdf(args.pdf)

    chapters = load_markup(args.pdf)
    if chapters:
        print(f"Using markup: {outs['chapters_txt']}")
        for idx, (s, e, title) in enumerate(chapters, 1):
            raw = read_pdf_text(args.pdf, s, e)
            text = normalize_text(raw)
            if not text:
                print(f"[skip] chapter {idx} is empty")
                continue
            wav_path = f"{outs['base']}_ch{idx:02d}.wav"
            print(f"Synth ch{idx}: pages {s}-{e} → {wav_path}")
            synth_to_wav(text, wav_path, rate=args.rate, volume=args.volume, voice_id=voice_id)
            if args.mp3:
                mp3_out = wav_path.rsplit(".", 1)[0] + ".mp3"
                wav_to_mp3_ffmpeg(wav_path, mp3_out, bitrate=args.bitrate, ar=args.ar, mono=not args.stereo)
                print("MP3:", mp3_out)
    else:
        raw = read_pdf_text(args.pdf, args.start, args.end)
        text = normalize_text(raw)
        if not text:
            raise SystemExit("Порожній текст (скани без OCR?)")
        wav_path = outs["wav"]
        print("Synth →", wav_path)
        synth_to_wav(text, wav_path, rate=args.rate, volume=args.volume, voice_id=voice_id)
        if args.mp3:
            mp3_out = outs["mp3"]
            wav_to_mp3_ffmpeg(wav_path, mp3_out, bitrate=args.bitrate, ar=args.ar, mono=not args.stereo)
            print("MP3:", mp3_out)
