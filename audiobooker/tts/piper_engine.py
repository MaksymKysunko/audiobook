import os, shutil, subprocess, tempfile, textwrap

def synth_to_wav_piper(text: str, wav_out: str, piper_bin: str, voice_model: str, length_scale: float = 1.0, noise: float = 0.667, noise_w: float = 0.8):
    ff = shutil.which("ffmpeg")
    if not os.path.exists(piper_bin):
        raise RuntimeError("piper binary not found: " + piper_bin)
    if not os.path.exists(voice_model):
        raise RuntimeError("voice model not found: " + voice_model)

    # Piper краще даєш текст без надто довгих рядків:
    text = textwrap.fill(text, width=200)

    with tempfile.NamedTemporaryFile("w", delete=False, encoding="utf-8") as tmp_in:
        tmp_in.write(text)
        tmp_in_path = tmp_in.name

    try:
        # piper виводить 16kHz/mono WAV, можемо одразу піджати через ffmpeg якщо треба
        cmd = [
            piper_bin, "--model", voice_model, "--output_file", wav_out,
            "--length_scale", str(length_scale), "--noise_scale", str(noise), "--noise_w", str(noise_w),
            "--sentence_silence", "0.2"  # трошки пауз між реченнями
        ]
        with open(tmp_in_path, "r", encoding="utf-8") as f_in:
            subprocess.run(cmd, stdin=f_in, check=True)
    finally:
        try: os.remove(tmp_in_path)
        except: pass
