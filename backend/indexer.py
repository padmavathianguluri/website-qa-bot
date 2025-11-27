import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss

DATA_DIR = os.path.join("backend", "data")
PAGES_FILE = os.path.join(DATA_DIR, "pages.json")
INDEX_FILE = os.path.join(DATA_DIR, "index.faiss")
META_FILE = os.path.join(DATA_DIR, "meta.json")

# Sentence Transformer Model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []
    i = 0

    while i < len(words):
        chunk = words[i:i + chunk_size]
        chunks.append(" ".join(chunk))
        i += (chunk_size - overlap)

    return chunks


def build_index():
    if not os.path.exists(PAGES_FILE):
        raise Exception("Crawl data not found! Run /api/crawl first.")

    with open(PAGES_FILE, "r", encoding="utf-8") as f:
        pages = json.load(f)

    all_chunks = []
    metadata = []

    for page in pages:
        url = page["url"]
        text = page["text"]

        chunks = chunk_text(text)

        for chunk in chunks:
            all_chunks.append(chunk)
            metadata.append({"url": url, "text": chunk})

    print(f"Total chunks: {len(all_chunks)}")

    embeddings = model.encode(all_chunks, convert_to_numpy=True)

    # Create FAISS index
    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)

    # Save FAISS index
    faiss.write_index(index, INDEX_FILE)

    # Save metadata
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)

    print("Index successfully built.")
    return True
