"""
server.py
---------
Flask backend for FitEvidence AI.

Serves the custom web frontend and exposes a single JSON API endpoint,
/api/ask, that runs the existing RAG pipeline (retriever.py + llm.py).

Run with:
    python web/server.py
Then open http://localhost:5000
"""

import os
import sys

from flask import Flask, jsonify, render_template, request

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(__file__)), "src"))

from retriever import retrieve_relevant_chunks  # noqa: E402
from llm import generate_answer  # noqa: E402

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/ask", methods=["POST"])
def ask():
    data = request.get_json(force=True, silent=True) or {}
    question = (data.get("question") or "").strip()

    if not question:
        return jsonify({"error": "Type a question before submitting."}), 400

    try:
        chunks = retrieve_relevant_chunks(question)
    except FileNotFoundError as e:
        return jsonify({"error": str(e)}), 500

    if not chunks:
        return jsonify({
            "answer": None,
            "sources": [],
            "message": "No relevant information found in the knowledge base for this question.",
        })

    try:
        result = generate_answer(question, chunks)
    except ValueError as e:
        return jsonify({"error": str(e)}), 500

    return jsonify(result)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, use_reloader=False, host="0.0.0.0", port=port)
