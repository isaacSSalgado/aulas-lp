from app.utils.db import DBConnection
from app.models.user_model import User

def init_db():
    with DBConnection() as conn:
        cursor = conn.cursor()
    # Cria a tabela ajustada para o SQLite
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_active INTEGER DEFAULT 1
            )
        ''')

        cursor.execute('''
        CREATE TABLE IF NOT EXISTS trabalhos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            materia TEXT NOT NULL,
            data_limite DATE,
            descricao TEXT NOT NULL 
        )
    ''')



if __name__ == '__main__':
    # 1. Cria o arquivo database.db e a tabela users
    init_db()
    
    admin_user = User(username="admin", password="senha123")
    
    # O método salvar() devolve True se criou, e False se o username já existir
    sucesso = admin_user.salvar()
    
    if sucesso:
        print("Banco SQLite inicializado e usuário 'admin' criado com sucesso!")
    else:
        print("O banco está pronto, mas o usuário 'admin' já existe.")