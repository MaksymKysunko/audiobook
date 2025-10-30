import os

def out_paths_for_pdf(pdf_path: str):
    base, _ = os.path.splitext(pdf_path)
    return {
        "base": base,
        "wav": base + ".wav",
        "mp3": base + ".mp3",
        "chapters_txt": base + ".chapters.txt",
    }
