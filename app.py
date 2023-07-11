from flask import Flask, render_template, request, jsonify, redirect, url_for
import random
import json
from database import cadastrar_usuario, exibir_usuarios
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

@app.route("/cadastro", methods=["GET", "POST"])
def cadastro():
    if request.method == "POST":
        # Obter os dados do formulário
        username = request.form.get("username")
        registration = request.form.get("registration")
        password = request.form.get("password")

        # Salvar os dados no banco de dadosap
        cadastrar_usuario(username, registration, password)
        exibir_usuarios()
        # Redirecionar para a página de cadastro com a mensagem de sucesso na URL
        return redirect(url_for("cadastro", sucesso=True))
    else:
        # Exibir o formulário de cadastro
        return render_template("cadastro.html")



if __name__ == "__main__":
    app.run(debug=True)
