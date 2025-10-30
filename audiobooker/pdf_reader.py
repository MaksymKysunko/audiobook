from PyPDF2 import PdfReader

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
        chunks.append(txt)
    return "\n".join(chunks)
