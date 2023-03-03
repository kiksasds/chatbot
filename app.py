from flask import Flask, render_template, request, jsonify
import random
from chat import get_response, intents, tags, get_fallback_subject_index

app = Flask(__name__)


@app.get("/")
def index_get():
    return render_template("base.html")

@app.post("/predict")
def predict():
    text = request.get_json().get("message")
    response = get_response(text)
    message = {"answer": response}
    return jsonify(message)


@app.post("/fallback")
def fallback():

    
    subject = tags[get_fallback_subject_index()]

    response = f"Do you mean '{subject}'? (yes or no)"

    user_response = input().lower()
    if user_response == "yes":
        for intent in intents["intents"]:
            if intent["tag"] == subject:
                response = random.choice(intent["responses"])
                break
    else:
        response = "Please rephrase your question."

    return jsonify({'answer': response})


if __name__ == "__main__":
    app.run(debug=True)
