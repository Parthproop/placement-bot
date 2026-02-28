from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# ==============================
# CONFIG
# ==============================
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "phi3:mini"   # change if needed
TIMEOUT = 120


# ==============================
# LOAD KNOWLEDGE BASE
# ==============================
KNOWLEDGE_BASE = ""

def load_documents():
    global KNOWLEDGE_BASE

    if KNOWLEDGE_BASE:
        return KNOWLEDGE_BASE

    files = ["faq.txt", "policy.txt", "rulebook.txt", "edge_cases.txt"]

    combined = ""
    for file in files:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                combined += f.read() + "\n\n"

    KNOWLEDGE_BASE = combined
    return KNOWLEDGE_BASE

    combined = ""

    for file in files:
        try:
            if os.path.exists(file):
                with open(file, "r", encoding="utf-8") as f:
                    combined += f"\n\n===== {file.upper()} =====\n"
                    combined += f.read()
            else:
                print(f"[WARNING] {file} not found.")
        except Exception as e:
            print(f"[ERROR] Loading {file} failed:", e)

    return combined


# ==============================
# AI RESPONSE
# ==============================
def generate_response(question):

    context = load_documents()

    prompt = f"""
You are the Official University Placement Cell Assistant.

IMPORTANT RULES:
1. Answer ONLY using the provided context.
2. Do NOT hallucinate.
3. If the answer is not in context, say:
   "This case needs to be reviewed by the placement team."

CONTEXT:
{context}

STUDENT QUESTION:
{question}

FINAL ANSWER:
"""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={
                "model": MODEL_NAME,
                "prompt": prompt,
                "stream": False
            },
            timeout=TIMEOUT
        )

        if response.status_code != 200:
            return "Error: AI model is not responding properly."

        data = response.json()

        return data.get("response", "No response received.").strip()

    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Is 'ollama serve' running?"

    except requests.exceptions.Timeout:
        return "Error: AI response timed out."

    except Exception as e:
        return f"Server Error: {str(e)}"


# ==============================
# ROUTES
# ==============================
@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    question = data.get("message", "").strip()

    if not question:
        return jsonify({"response": "Please enter a valid question."})

    reply = generate_response(question)

    return jsonify({"response": reply})


if __name__ == "__main__":
    print("Starting Placement Bot...")
    app.run(debug=True)