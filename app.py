from builtins import enumerate

from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import random
import json
from database import cadastrar_usuario, exibir_usuarios, entar_usuario, is_tutor, get_registration, exibir_perguntas_nao_respondidas
from chat import get_response, reload_model
import os

app = Flask(__name__)
app.secret_key = 'ChaveSecreta'

with open('intents.json', 'r', encoding='utf-8') as json_data:
    intents = json.load(json_data)

tag = None


@app.route("/")
def root():
    if 'username' in session:
        return redirect('/base')
    return redirect('/login')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        # Obter os dados do formulário
        username = request.form['username']
        password = request.form.get("password")

        if entar_usuario(username, password):
            session['username'] = username
            session['registration'] = get_registration(username)
            return redirect('/base')
        else:
            return redirect(url_for('login', erro=True))

    # Verificar se a mensagem de sucesso está presente na URL
    sucesso = request.args.get("sucesso")

    return render_template('login.html', sucesso=sucesso)

@app.route("/logout")
def logout():
    # remove the username from the session if it is there
    session.pop('username', None)
    return redirect('/')



@app.route('/cadastro', methods=['POST'])
def cadastro():
    # Obter os dados do formulário
    username = request.form.get("username")
    registration = request.form.get("registration")
    password = request.form.get("password")
    tutor = request.form.get("tutor") == "on"

    # Cadastrar o usuário no banco de dados
    cadastrar_usuario(username, registration, password, tutor)
    exibir_usuarios()

    # Redirecionar para a página de login com uma mensagem de sucesso
    return redirect(url_for('login', sucesso=True))

@app.route('/base')
def base():
    # Obter o nome de usuário e a matrícula da sessão
    username = session.get('username')
    registration = session.get('registration')

    # Passar o nome de usuário e a matrícula para o template
    return render_template('base.html', username=username, registration=registration)


@app.route('/form', methods=['POST', 'PUT', 'GET', 'DELETE'])
def form():
    if not is_tutor(session['username']):
        return 'you :'+session['username']+' does not have permission '+"<a href='/'>Home</a>"
    if request.method == 'POST':
        text = request.get_json().get("message")
        with open('intents.json', 'r+', encoding='utf-8') as f:
            novo = json.load(f)
            novo['intents'].append(text)
            f.seek(0)
            f.write(json.dumps(novo, indent=2, ensure_ascii=False))
            f.truncate()
        return text
    if request.method == 'PUT' and request.args.get('tag'):
        tag = request.args.get('tag')
        with open('intents.json', 'r+', encoding='utf-8') as f:
            jsonArr = json.load(f)
            intents = jsonArr['intents']
            for i, intent in enumerate(intents):
                if intent['tag'] == tag:
                    intents.pop(i)
                    text = request.get_json().get("message")
                    intents.append(text)
                    break
            f.seek(0)
            f.write(json.dumps(jsonArr, indent=2, ensure_ascii=False))
            f.truncate()
        return json.loads('{"tag":"","patterns":[],"responses":[]}')
    if request.method == 'GET' and request.args.get('tag'):
        tag = request.args.get('tag')
        with open('intents.json', 'r+', encoding='utf-8') as f:
            jsonArr = json.load(f)
            intents = jsonArr['intents']
            for intent in intents:
                if intent['tag'] == tag:
                    return intent
            return json.loads('{"tag":"","patterns":[],"responses":[]}')
    if request.method == 'DELETE' and request.args.get('tag'):
        tag = request.args.get('tag')
        with open('intents.json', 'r+', encoding='utf-8') as f:
            jsonArr = json.load(f)
            intents = jsonArr['intents']
            for i, intent in enumerate(intents):
                if intent['tag'] == tag:
                    intents.pop(i)
                    break
            f.seek(0)
            f.write(json.dumps(jsonArr, indent=2, ensure_ascii=False))
            f.truncate()

        return json.loads('{"tag":"","patterns":[],"responses":[]}')

    return render_template('form.html')


@app.post("/predict")
def predict():
    global tag
    text = request.get_json().get("message")
    username = session.get('username')
    registration = session.get('registration')

    response_and_tag = get_response(text, username, registration)

    if response_and_tag is not None:
        response, predicted_tag = response_and_tag
        tag = predicted_tag
        message = {"answer": response}
        return jsonify(message)
    else:
        # Lógica para tratar o caso em que get_response() retorna None
        # Por exemplo, você pode retornar uma resposta padrão ou uma mensagem de erro.
        message = {"answer": "Desculpe, ocorreu um erro ao processar a pergunta."}
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

@app.route('/sair', methods=['POST'])
def sair():
    # Limpar a sessão
    session.clear()

    # Redirecionar para a página de login
    return redirect(url_for('login'))

@app.route('/check_tutor')
def check_tutor():
    if 'username' in session:
        username = session['username']
        e_tutor = is_tutor(username)
        return jsonify({'is_tutor': e_tutor})
    else:
        return jsonify({'is_tutor': False})


@app.route('/unanswered_questions')
def unanswered_questions():
    perguntas = exibir_perguntas_nao_respondidas()

    # Converter as perguntas em um objeto JSON
    result = []
    for pergunta in perguntas:
        result.append({
            "id": pergunta[0],
            "question": pergunta[1],
            "username": pergunta[2],
            "registration": pergunta[3]
        })

    return jsonify(result)

@app.route('/train', methods=['POST'])
def treino():
    # Executar o script de treinamento do chatbot
    os.system("python train.py")
    # Recarregar o modelo do chatbot
    reload_model()

    return "", 204

if __name__ == "__main__":
    app.run(debug=True)
