import sqlite3

# Conexão com o banco de dados
conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

# Criação da tabela de usuários
cursor.execute('''CREATE TABLE IF NOT EXISTS users
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT NOT NULL,
                  registration TEXT NOT NULL,
                  password TEXT NOT NULL)''')
conn.commit()

# Função para cadastrar um novo usuário
def cadastrar_usuario(username, registration, password):
    cursor.execute("INSERT INTO users (username, registration, password) VALUES (?, ?, ?)",
                   (username, registration, password))
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
        print()

