import shutil, subprocess

def wav_to_mp3_ffmpeg(wav_path: str, mp3_path: str, bitrate: str = "48k", ar: int = 22050, mono: bool = True):
    ff = shutil.which("ffmpeg")
    if not ff:
        raise RuntimeError("ffmpeg не знайдено у PATH")
    cmd = [
        ff, "-y", "-i", wav_path, "-vn",
        "-ar", str(ar),
        "-ac", "1" if mono else "2",
        "-b:a", bitrate,
        mp3_path
    ]
    subprocess.run(cmd, check=True)
