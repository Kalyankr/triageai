import base64
import re
from io import BytesIO
from PIL import Image


def preprocess_image(image_input, max_size: int = 512) -> Image.Image:
    """Load and resize an image for Gemma 4 vision input."""
    if isinstance(image_input, str):
        img = Image.open(image_input)
    elif isinstance(image_input, Image.Image):
        img = image_input
    elif isinstance(image_input, bytes):
        img = Image.open(BytesIO(image_input))
    else:
        raise ValueError(f"Unsupported image input type: {type(image_input)}")

    img = img.convert("RGB")

    w, h = img.size
    if max(w, h) > max_size:
        scale = max_size / max(w, h)
        img = img.resize((int(w * scale), int(h * scale)), Image.LANCZOS)

    return img


def image_to_base64(img: Image.Image, fmt: str = "JPEG") -> str:
    """Convert a PIL Image to a base64-encoded string."""
    buf = BytesIO()
    img.save(buf, format=fmt)
    return base64.b64encode(buf.getvalue()).decode("utf-8")


LANGUAGE_MAP = {
    "en": "English",
    "es": "Spanish",
    "hi": "Hindi",
    "ar": "Arabic",
    "fr": "French",
    "pt": "Portuguese",
    "zh": "Chinese",
    "de": "German",
    "ja": "Japanese",
    "ko": "Korean",
    "ru": "Russian",
    "tr": "Turkish",
    "ur": "Urdu",
}

EMERGENCY_NUMBERS = {
    "en": {"number": "911", "country": "United States / Canada"},
    "es": {"number": "112", "country": "Spain / Latin America"},
    "hi": {"number": "112", "country": "India"},
    "ar": {"number": "999", "country": "Middle East"},
    "fr": {"number": "15 / 112", "country": "France / Europe"},
    "pt": {"number": "192 / 112", "country": "Brazil / Portugal"},
    "zh": {"number": "120", "country": "China"},
    "de": {"number": "112", "country": "Germany"},
    "ja": {"number": "119", "country": "Japan"},
    "ko": {"number": "119", "country": "South Korea"},
    "ru": {"number": "103 / 112", "country": "Russia"},
    "tr": {"number": "112", "country": "Turkey"},
    "ur": {"number": "1122 / 115", "country": "Pakistan"},
}


def detect_language_simple(text: str) -> str:
    """Simple heuristic language detection based on character ranges and keywords."""
    if not text or not text.strip():
        return "en"

    arabic_chars = len(re.findall(r"[\u0600-\u06FF]", text))
    devanagari_chars = len(re.findall(r"[\u0900-\u097F]", text))
    cjk_chars = len(re.findall(r"[\u4E00-\u9FFF]", text))
    hangul_chars = len(re.findall(r"[\uAC00-\uD7AF]", text))
    cyrillic_chars = len(re.findall(r"[\u0400-\u04FF]", text))
    hiragana_katakana = len(re.findall(r"[\u3040-\u30FF]", text))

    if arabic_chars > 5:
        return "ar"
    if devanagari_chars > 5:
        return "hi"
    if hiragana_katakana > 3:
        return "ja"
    if hangul_chars > 3:
        return "ko"
    if cjk_chars > 3:
        return "zh"
    if cyrillic_chars > 5:
        return "ru"

    lower = text.lower()
    spanish_markers = ["ayuda", "emergencia", "herido", "sangre", "dolor", "accidente"]
    french_markers = ["aide", "urgence", "blessé", "sang", "douleur", "accident"]
    portuguese_markers = ["ajuda", "emergência", "ferido", "sangue", "dor"]
    turkish_markers = ["yardım", "acil", "yaralı", "kan", "ağrı"]
    german_markers = ["hilfe", "notfall", "verletzt", "blut", "schmerz"]

    for marker in spanish_markers:
        if marker in lower:
            return "es"
    for marker in french_markers:
        if marker in lower:
            return "fr"
    for marker in portuguese_markers:
        if marker in lower:
            return "pt"
    for marker in turkish_markers:
        if marker in lower:
            return "tr"
    for marker in german_markers:
        if marker in lower:
            return "de"

    return "en"


def get_emergency_info(lang_code: str) -> dict:
    """Get emergency number and country for a language code."""
    return EMERGENCY_NUMBERS.get(lang_code, EMERGENCY_NUMBERS["en"])
