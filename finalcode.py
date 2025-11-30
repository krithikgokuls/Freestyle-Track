import os
from flask import Flask, request, jsonify
from openai import OpenAI

# Load API Keys
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "AIzaSyBckiukwiOlm35jP0n4Xfl_DVi32Q2vKk4")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "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")

client = OpenAI(api_key=OPENAI_API_KEY)

app = Flask(__name__)

# Simple in-memory docs for RAG
RAG_DOCS = [
    {"id": "immig_rules_us", "text": "US immigration checklist: passport, visa, I-94 form."},
    {"id": "baggage_rules", "text": "Airline baggage rules differ by carrier."},
]

def simple_retrieve(query, k=2):
    """Very small placeholder RAG system"""
    q = query.lower().split()
    results = []
    for doc in RAG_DOCS:
        if any(word in doc["text"].lower() for word in q):
            results.append(doc)
    return results[:k]

def call_llm(prompt):
    """Updated OpenAI chat API call"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI for flight booking & immigration support."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.3,
        max_tokens=400
    )
    return response.choices[0].message.content


@app.route("/chat", methods=["POST"])
def chat():
    if not request.is_json:
        return jsonify({"error": "Send JSON only"}), 400

    data = request.get_json()
    user_msg = data.get("message", "")

    if user_msg == "":
        return jsonify({"error": "Message is required"}), 400

    # Step 1: Retrieve RAG Docs
    docs = simple_retrieve(user_msg)
    context = "\n".join([doc["text"] for doc in docs])

    # Step 2: Build final prompt
    final_prompt = f"""
Relevant Information:
{context}

User Query:
{user_msg}

Answer concisely with correct steps.
"""

    # Step 3: Call LLM
    answer = call_llm(final_prompt)

    return jsonify({
        "answer": answer,
        "retrieved_docs": [doc["id"] for doc in docs]
    })


# ---- FIXED SERVER STARTUP ----
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=False)
