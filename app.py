from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# ======================================
# CONFIGURATION
# ======================================
OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "phi3:mini"   # Faster than mistral
TIMEOUT = 60


# ======================================
# LOAD KNOWLEDGE BASE ONCE (FAST)
# ======================================
def load_knowledge():
    files = [
        "faq.txt",
        "policy.txt",
        "rulebook.txt",
        "edge_cases.txt"
    ]

    combined_text = ""

    print("[INFO] Loading knowledge base...")

    for file in files:
        if os.path.exists(file):
            with open(file, "r", encoding="utf-8") as f:
                combined_text += f"\n\n===== {file.upper()} =====\n"
                combined_text += f.read()
        else:
            print(f"[WARNING] {file} not found.")

    print("[INFO] Knowledge base loaded successfully.")
    return combined_text


# Load once at startup
KNOWLEDGE_BASE = load_knowledge()


# ======================================
# SIMPLE CONTEXT FILTERING (FASTER)
# ======================================
def get_relevant_context(question):
    question_words = question.lower().split()
    lines = KNOWLEDGE_BASE.split("\n")

    relevant_lines = []

    for line in lines:
        line_lower = line.lower()
        if any(word in line_lower for word in question_words):
            relevant_lines.append(line)

    # Limit size to avoid huge prompt
    return "\n".join(relevant_lines[:40])


# ======================================
# GENERATE RESPONSE
# ======================================
def generate_response(question):

    context = get_relevant_context(question)

    if not context.strip():
        context = "No exact match found in rulebook."

    prompt = f"""
You are the Official University Placement and Internship Assistant.

Rules:
- Answer ONLY using the context provided.
- If answer not found, say:
"This case needs to be reviewed by the placement team."

Context:
{context}

Student Question:
{question}

Answer:
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
            return "Error: AI model not responding properly."

        data = response.json()

        return data.get("response", "No response from model.").strip()

    except requests.exceptions.ConnectionError:
        return "Error: Cannot connect to Ollama. Make sure 'ollama serve' is running."

    except requests.exceptions.Timeout:
        return "Error: AI response timed out."

    except Exception as e:
        return f"Server Error: {str(e)}"


# ======================================
# ROUTES
# ======================================
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


# ======================================
# RUN SERVER
# ======================================
if __name__ == "__main__":
    print("=================================")
    print(" Placement Bot Running...")
    print(" Using Model:", MODEL_NAME)
    print("=================================")
    app.run(debug=True)