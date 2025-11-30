"""
Automated Flight & Immigration Assistant (minimal example)
Includes: GOOGLE_API_KEY placeholder, LLM (OpenAI) + simple RAG sketch.
Save as agent_code.py
"""
import os
from flask import Flask, request, jsonify
import openai

# Put your keys here (or export as environment variables)
GOOGLE_API_KEY = "YOUR_GOOGLE_API_KEY"   # <--- include GOOGLE_API_KEY as requested
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

app = Flask(__name__)

# Simple in-memory 'vector store' stub for RAG (replace with FAISS/Chroma in prod)
RAG_DOCS = [
    {"id":"immig_rules_us","text":"US immigration checklist: passport, visa, I-94, ..."},
    {"id":"baggage_rules","text":"Baggage limits differ by airline..."},
]

def simple_retrieve(query, k=2):
    # naive RAG: return docs whose text contains tokens from query (placeholder)
    q = query.lower()
    res = [d for d in RAG_DOCS if any(tok in d["text"].lower() for tok in q.split()[:3])]
    return res[:k]

def call_llm(prompt, temperature=0.2):
    resp = openai.ChatCompletion.create(
        model="gpt-4o-mini",  # replace with available model
        messages=[{"role":"system","content":"You are an assistant for flight bookings and immigration notifications."},
                  {"role":"user","content":prompt}],
        temperature=temperature,
        max_tokens=400
    )
    return resp["choices"][0]["message"]["content"]

@app.route("/chat", methods=["POST"])
def chat():
    data = request.json or {}
    user_msg = data.get("message","")
    # Step 1: retrieve related docs (RAG)
    docs = simple_retrieve(user_msg)
    context = "\n\n".join([d["text"] for d in docs])
    prompt = f"Context: {context}\nUser: {user_msg}\nProvide concise actionable steps."
    answer = call_llm(prompt)
    return jsonify({"answer": answer, "retrieved": [d["id"] for d in docs]})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=7860, debug=True)
