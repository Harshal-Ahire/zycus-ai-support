import json
from app.config import GEMINI_API_KEY, GEMINI_MODEL, CATEGORIES, URGENCY

try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None
    types = None


class GeminiClient:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY) if GEMINI_API_KEY and genai else None

    @property
    def available(self):
        return self.client is not None

    def json(self, prompt):
        response = self.client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(temperature=0.0, response_mime_type="application/json"),
        )
        return json.loads(response.text)


llm = GeminiClient()


def normalize_category(value):
    for item in CATEGORIES:
        if str(value).lower() == item.lower():
            return item
    return "Bug"


def normalize_urgency(value):
    value = str(value).upper()
    return value if value in URGENCY else "P3"
