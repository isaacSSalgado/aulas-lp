from app.utils.db import DBConnection
from app.models.user_model import User

def init_db():
    with DBConnection() as conn:
        cursor = conn.cursor()
    # 1. Tabela de Usuários com perfis ('admin', 'professor' ou 'aluno')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                perfil TEXT NOT NULL DEFAULT 'aluno',
                is_active INTEGER DEFAULT 1
            )
        ''')

        # 2. Tabela de Trabalhos vinculada ao ID do aluno
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trabalhos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                titulo TEXT NOT NULL,
                materia TEXT NOT NULL,
                data_limite DATE,
                descricao TEXT NOT NULL,
                status TEXT DEFAULT 'Pendente',
                arquivo_entrega TEXT,
                aluno_id INTEGER NOT NULL,
                FOREIGN KEY (aluno_id) REFERENCES users (id)
            )
        ''')

        # Tabela de Matérias / Disciplinas (2ª Entidade de Negócio)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS materias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                codigo TEXT NOT NULL,
                usuario_id INTEGER NOT NULL,
                FOREIGN KEY (usuario_id) REFERENCES users (id) ON DELETE CASCADE
            )
        ''')


if __name__ == '__main__':
    # 1. Cria o arquivo database.db e a tabela users
    init_db()
    
    admin_user = User(username="admin", password="senha123", perfil="admin")
    
    # O método salvar() devolve True se criou, e False se o username já existir
    sucesso = admin_user.salvar()
    
    if sucesso:
        print("Banco SQLite inicializado e usuário 'admin' criado com sucesso!")
    else:
        print("O banco está pronto, mas o usuário 'admin' já existe.")

