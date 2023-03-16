from flask import Flask, render_template, request, jsonify
import random
import json
from chat import get_response

app = Flask(__name__)

with open('intents.json', 'r', encoding='utf-8') as json_data:
    intents = json.load(json_data)

tag = None

@app.get("/")
def index_get():
    return render_template("base.html")

@app.get("/form")
def form_get():
    return render_template("form.html")

@app.post("/predict")
def predict():
    global tag
    text = request.get_json().get("message")
    response, predicted_tag = get_response(text)
    tag = predicted_tag
    message = {"answer": response}
    return jsonify(message)


@app.post("/fallback")
def fallback():
    global tag
    text = request.get_json().get("message")
    if text == 'sim' or text == 'Sim':
        for intent in intents['intents']:
            if tag == intent["tag"]:
                response = random.choice(intent['responses'])
                message = {"answer": response}
                return jsonify(message)
    else:
        response = "Reescreva a pergunta..."
        message = {"answer": response}
        return jsonify(message)

@app.post("/form")
def form():
    text = request.get_json().get("message")
    with open('intents.json', 'r+', encoding='utf-8') as f:
        novo = json.load(f)
        novo['intents'].append(text)
        f.seek(0)
        f.write(json.dumps(novo, indent=2, ensure_ascii=False))
        f.truncate()
    return text


if __name__ == "__main__":
    app.run(debug=True)
