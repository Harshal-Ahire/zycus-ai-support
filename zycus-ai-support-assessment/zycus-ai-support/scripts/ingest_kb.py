from app.rag import get_kb
kb = get_kb()
print(f"Loaded {len(kb.chunks)} knowledge-base sections.")
