import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import requests
from dotenv import load_dotenv

load_dotenv()

DATA_DIR = os.path.join("backend", "data")
INDEX_FILE = os.path.join(DATA_DIR, "index.faiss")
META_FILE = os.path.join(DATA_DIR, "meta.json")

# embedding model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def load_faiss():
    if not os.path.exists(INDEX_FILE):
        raise Exception("Index not found. Build index first.")
    return faiss.read_index(INDEX_FILE)


def load_meta():
    with open(META_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def search_index(query, top_k=3):
    index = load_faiss()
    meta = load_meta()

    query_emb = model.encode([query], convert_to_numpy=True)
    distances, results = index.search(query_emb, top_k)

    chunks = []
    for idx in results[0]:
        chunks.append(meta[idx])

    return chunks


def call_openai(question, context):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None  # no key → fallback

    url = "https://api.openai.com/v1/chat/completions"

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    prompt = f"""
You are an AI assistant. Use the website context below to answer the question.

Context:
{context}

Question:
{question}

Answer clearly in natural language.
"""

    body = {
        "model": "gpt-4o-mini",
        "messages": [{"role": "user", "content": prompt}]
    }

    response = requests.post(url, headers=headers, json=body)
    data = response.json()

    try:
        return data["choices"][0]["message"]["content"]
    except:
        return "OpenAI failed to generate response."


def call_gemini(question, context):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return None  # no key → fallback

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"

    prompt = f"""
You are a helpful assistant. Use the website data to answer.

Context:
{context}

Question: {question}
"""

    body = {
        "contents": [{"parts": [{"text": prompt}]}]
    }

    response = requests.post(url, json=body)
    data = response.json()

    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except:
        return "Gemini failed to generate response."


def answer_query(question):
    chunks = search_index(question)
    context = "\n\n".join([f"({c['url']}) {c['text']}" for c in chunks])

    # 1. Try OpenAI
    resp = call_openai(question, context)
    if resp:
        return resp

    # 2. Try Gemini
    resp = call_gemini(question, context)
    if resp:
        return resp

    # 3. Fallback
    return "Please set either OPENAI_API_KEY or GEMINI_API_KEY in .env"
