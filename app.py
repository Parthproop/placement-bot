from flask import Flask, render_template, request, jsonify
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# Load knowledge files
def load_knowledge():
    texts = []
    for file in ["rulebook.txt", "faq.txt", "edge_cases.txt"]:
        try:
            with open(file, "r", encoding="utf-8") as f:
                texts.extend(f.readlines())
        except:
            pass
    return texts

knowledge_base = load_knowledge()

vectorizer = TfidfVectorizer()
vectors = vectorizer.fit_transform(knowledge_base)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_input = request.json["message"]

    user_vector = vectorizer.transform([user_input])
    similarities = cosine_similarity(user_vector, vectors)
    best_match_index = similarities.argmax()

    if similarities[0][best_match_index] < 0.2:
        return jsonify({"response": "I am not sure about that. Please contact the placement office."})

    return jsonify({"response": knowledge_base[best_match_index]})

if __name__ == "__main__":
    app.run(debug=True)