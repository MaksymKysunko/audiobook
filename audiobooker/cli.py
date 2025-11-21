import argparse
from .paths import out_paths_for_pdf
from .pdf_reader import read_pdf_text
from .text_clean import normalize_text
from .markup import load_markup, save_markup_draft, make_markup_draft
from .encode import wav_to_mp3_ffmpeg
from .tts.voices import VOICES
from .tts.pyttsx_engine import synth_to_wav as pyttsx_to_wav
from .tts.edge_tts_engine import speak_to_mp3 as edge_to_mp3
from .tts.piper_engine import synth_to_wav_piper

def synth_block(text, base_out_no_ext, args):
    if args.tts == "pyttsx":
        # як і було: генеруємо WAV → (за потреби) ffmpeg у MP3
        wav_path = base_out_no_ext + ".wav"
        pyttsx_to_wav(text, wav_path, rate=args.rate, volume=args.volume,
                      voice_id=VOICES.get(args.voice) if args.voice else None)
        if args.mp3:
            mp3_out = base_out_no_ext + ".mp3"
            wav_to_mp3_ffmpeg(wav_path, mp3_out, bitrate=args.bitrate, ar=args.ar, mono=not args.stereo)
            print("MP3:", mp3_out)
        return

    if args.tts == "edge":
        # одразу MP3: швидко і якісно (потрібен інтернет)
        mp3_out = base_out_no_ext + ".mp3"
        edge_to_mp3(text, mp3_out, voice=args.edge_voice)
        print("MP3:", mp3_out)
        return

    if args.tts == "piper":
        # офлайн нейронний голос: WAV → (опційно) MP3
        if not args.piper_bin or not args.piper_voice:
            raise SystemExit("--piper requires --piper-bin and --piper-voice")
        wav_path = base_out_no_ext + ".wav"
        synth_to_wav_piper(text, wav_path, piper_bin=args.piper_bin, voice_model=args.piper_voice)
        if args.mp3:
            mp3_out = base_out_no_ext + ".mp3"
            wav_to_mp3_ffmpeg(wav_path, mp3_out, bitrate=args.bitrate, ar=args.ar, mono=not args.stereo)
            print("MP3:", mp3_out)
        return


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
    ap.add_argument("--tts", choices=["pyttsx", "edge", "piper"], default="pyttsx",
                help="Оберіть рушій озвучки")
    ap.add_argument("--edge-voice", default="en-US-AriaNeural", help="Edge TTS voice id")
    ap.add_argument("--piper-bin", type=str, help="Шлях до piper.exe")
    ap.add_argument("--piper-voice", type=str, help="Шлях до моделі .onnx для Piper")


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
            synth_block(text, wav_path, args)
            #synth_to_wav(text, wav_path, rate=args.rate, volume=args.volume, voice_id=voice_id)
    else:
        raw = read_pdf_text(args.pdf, args.start, args.end)
        text = normalize_text(raw)
        if not text:
            raise SystemExit("Порожній текст (скани без OCR?)")
        wav_path = outs["wav"]
        print("Synth →", wav_path)
        synth_block(text, wav_path, args)
