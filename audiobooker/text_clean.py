import re

def normalize_text(s: str) -> str:
    if not s:
        return ""
    # "сло-\nво" → "слово"
    s = re.sub(r"-\s*\n\s*", "", s)
    # \r\n → \n; кілька \n → один; \n → пробіл
    s = s.replace("\r", "\n")
    s = re.sub(r"\n+", "\n", s)
    s = s.replace("\n", " ")
    # зжати пробіли
    s = re.sub(r"[ \t]+", " ", s).strip()
    return s
