import re
from dataclasses import dataclass
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import KB_DIR, KB_TOP_K


@dataclass
class Chunk:
    document: str
    section: str
    text: str


class KnowledgeBase:
    def __init__(self):
        self.chunks = self._load()
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform([x.text for x in self.chunks])

    def _load(self):
        chunks = []
        for path in sorted(KB_DIR.rglob("*.md")):
            if path.name == "DATA_SCHEMA.md":
                continue
            text = path.read_text(encoding="utf-8")
            parts = re.split(r"(?m)^#{1,3}\s+", text)
            for part in parts:
                lines = [x.rstrip() for x in part.strip().splitlines()]
                if not lines:
                    continue
                section = lines[0].strip()
                body = "\n".join(lines[1:]).strip() or section
                chunks.append(Chunk(path.name, section, body))
        return chunks

    def search(self, query, top_k=KB_TOP_K):
        if not query.strip():
            return []
        scores = cosine_similarity(self.vectorizer.transform([query]), self.matrix)[0]
        indexes = scores.argsort()[::-1][:top_k]
        return [
            {"document": self.chunks[i].document, "section": self.chunks[i].section,
             "relevance": round(float(scores[i]), 3), "excerpt": self.chunks[i].text[:900]}
            for i in indexes if scores[i] > 0
        ]


_kb = None


def get_kb():
    global _kb
    if _kb is None:
        _kb = KnowledgeBase()
    return _kb
