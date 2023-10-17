import sqlite3

# Conexão com o banco de dados
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

# Criação da tabela de usuários
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  registration TEXT NOT NULL,
                  password TEXT NOT NULL,
                  tutor BOOLEAN DEFAULT FALSE)''')
conn.commit()


# Função para cadastrar um novo usuário
def cadastrar_usuario(username, registration, password, tutor):
    cursor.execute("INSERT INTO users (username, registration, password, tutor) VALUES (?, ?, ?, ?)",
                   (username, registration, password, tutor))
    conn.commit()
    print("Usuário cadastrado com sucesso.")


def exibir_usuarios():
    # Conexão com o banco de dados
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Executa a consulta SQL para recuperar os usuários
    cursor.execute("SELECT * FROM users")
    usuarios = cursor.fetchall()

    # Fecha a conexão com o banco de dados
    conn.close()

    # Imprime os usuários
    for usuario in usuarios:
        print(f"ID: {usuario[0]}")
        print(f"Usuário: {usuario[1]}")
        print(f"Matrícula: {usuario[2]}")
        print(f"Senha: {usuario[3]}")
        print(f"Tutor: {usuario[4]}")
        print()


def entar_usuario(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password,))
    usuario = cursor.fetchone()

    conn.close()

    if usuario is None:
        return False
    else:
        return True


def is_tutor(username):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT tutor FROM users WHERE username=?", (username,))

    bol = cursor.fetchone()[0]

    conn.close()

    return bol


def get_registration(username):
    cursor.execute("SELECT registration FROM users WHERE username=?", (username,))
    registration = cursor.fetchone()[0]
    return registration


# Criação da tabela de perguntas não respondidas
cursor.execute('''CREATE TABLE IF NOT EXISTS unanswered_questions
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  question TEXT NOT NULL,
                  username TEXT NOT NULL,
                  registration TEXT NOT NULL)''')
conn.commit()


def save_unanswered_question(question, username, registration):
    cursor.execute("INSERT INTO unanswered_questions (question, username, registration) VALUES (?, ?, ?)",
                   (question, username, registration))
    conn.commit()
    print("Pergunta não respondida salva com sucesso.")


def exibir_perguntas_nao_respondidas():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM unanswered_questions")
    perguntas = cursor.fetchall()

    conn.close()

    return perguntas


cursor.execute('''CREATE TABLE IF NOT EXISTS feedback
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  question TEXT NOT NULL,
                  answer TEXT NOT NULL,
                  tag TEXT NOT NULL,
                  rating TEXT NOT NULL)''')
conn.commit()


def save_feedback(username, question, answer, tag, rating):
    cursor.execute("INSERT INTO feedback (username, question, answer, tag, rating) VALUES (?, ?, ?, ?, ?)",
                   (username, question, answer, tag, rating))
    conn.commit()
    print("Feedback salvo com sucesso.")


def get_feedback():
    cursor.execute("SELECT tag, rating, MAX(count) FROM (SELECT tag, rating, COUNT(*) as count FROM feedback GROUP BY "
                   "tag, rating) AS subquery GROUP BY tag;")
    feedback = cursor.fetchall()
    return feedback


def get_feedback_by_tag(tag):

    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM feedback WHERE tag = ?", (tag,))
    feedback = cursor.fetchall()

    conn.close()

    return feedback


def get_all_feedback():
    cursor.execute("SELECT * FROM feedback")
    all_feedback = cursor.fetchall()
    return all_feedback
