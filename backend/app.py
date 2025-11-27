from flask import Flask, request, jsonify
from flask_cors import CORS
import os
from crawl import crawl_website
from indexer import build_index
from query import answer_query

app = Flask(__name__)
CORS(app)

# Load env variables
from dotenv import load_dotenv
load_dotenv()

@app.route("/")
def home():
    return {"message": "Backend running successfully!"}

@app.route("/api/crawl", methods=["POST"])
def crawl():
    data = request.get_json()
    url = data.get("url")

    if not url:
        return jsonify({"error": "URL is required"}), 400

    pages = crawl_website(url)
    return jsonify({"message": "Crawling complete", "pages": len(pages)})

@app.route("/api/index", methods=["POST"])
def index():
    build_index()
    return jsonify({"message": "Index built successfully"})

@app.route("/api/query", methods=["POST"])
def query():
    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "Question is required"}), 400

    response = answer_query(question)
    return jsonify({"answer": response})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
