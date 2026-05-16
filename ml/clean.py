import re

def clean_text(text):
    """Lowercase, remove special characters, and extra spaces"""
    text = text.lower()
    text = ' '.join(text.split())
    text = re.sub(r'[^a-z0-9\s,.\-!?]', '', text)
    return text
