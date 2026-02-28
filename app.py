from flask import Flask, render_template, request
import requests

app = Flask(__name__)

OLLAMA_URL = "http://127.0.0.1:11434/api/generate"
MODEL_NAME = "mistral"


def load_documents():
    files = ["faq.txt", "policy.txt", "edge_cases.txt"]
    combined_text = ""

    for file in files:
        try:
            with open(file, "r", encoding="utf-8") as f:
                combined_text += f.read() + "\n"
        except:
            pass

    return combined_text


def generate_ai_response(user_question):

    context = load_documents()

    prompt = f"""
You are an official Placement Cell Assistant.

Answer ONLY using the provided context below.
If the answer is not found in context, say:
"This case needs to be reviewed by the placement team."

Context:
{context}

Question:
{user_question}
"""

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )

    return response.json()["response"]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    user_input = data.get("message")

    if not user_input:
        return {"response": "No message received."}

    try:
        ai_response = generate_ai_response(user_input)
        return {"response": ai_response}
    except Exception as e:
        return {"response": f"Error: {str(e)}"}


if __name__ == "__main__":
    app.run(debug=True)