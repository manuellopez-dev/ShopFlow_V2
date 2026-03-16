import bleach

# Tags HTML permitidos (ninguno para inputs de texto)
ALLOWED_TAGS = []
ALLOWED_ATTRIBUTES = {}

def sanitize(text: str) -> str:
    """Elimina todo HTML y scripts maliciosos."""
    if not text:
        return text
    return bleach.clean(text, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

def sanitize_html(text: str) -> str:
    """Permite solo tags seguros para descripciones."""
    allowed = ["b", "i", "u", "em", "strong", "p", "br", "ul", "li", "ol"]
    return bleach.clean(text, tags=allowed, attributes={}, strip=True)