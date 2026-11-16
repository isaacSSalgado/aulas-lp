from app.utils.db import DBConnection
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

class User:
    def __init__(self, username, password=None, password_hash=None, is_active=1, id=None):
        self.id = id
        self.username = username
        self.is_active = is_active
        
        # Se a senha for passada em texto limpo (no registo), gera o hash.
        # Se o hash for passado diretamente (na busca da BD), guarda-o.
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = password_hash

    def salvar(self):
        """(Create/Update) Guarda a instância atual na base de dados."""
        with DBConnection() as conn:
            cursor = conn.cursor()
            
            if self.id is None:
                # Se não tem ID, é um utilizador novo (INSERT)
                try:
                    sql = "INSERT INTO users (username, password, is_active) VALUES (?, ?, ?)"
                    cursor.execute(sql, (self.username, self.password_hash, self.is_active))
                    # Atualiza a instância com o ID gerado pela base de dados
                    self.id = cursor.lastrowid
                    return True
                except sqlite3.IntegrityError:
                    return False  # O username já existe
            else:
                # Se já tem ID, atualiza o existente (UPDATE)
                sql = "UPDATE users SET username = ?, password = ?, is_active = ? WHERE id = ?"
                cursor.execute(sql, (self.username, self.password_hash, self.is_active, self.id))
                return True

    def verificar_password(self, password):
        """Valida a palavra-passe desta instância."""
        return check_password_hash(self.password_hash, password)

    @classmethod
    def buscar_por_username(cls, username):
        """(Read) Busca um utilizador pelo nome e devolve uma instância de User."""
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            
            if row:
                # Em vez de um dicionário, devolvemos um objeto User pronto a usar
                return cls(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password'],
                    is_active=row['is_active']
                )
            return None

    @classmethod
    def autenticar(cls, username, password):
        """Verifica as credenciais e devolve o objeto do utilizador logado."""
        user = cls.buscar_por_username(username)
        if user and user.is_active and user.verificar_password(password):
            return user
        return None


    @classmethod
    def listar_todos(cls):
        """(Read) Busca todos os usuários cadastrados e retorna uma lista de objetos User."""
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, username, is_active FROM users")
            rows = cursor.fetchall()
            
            # Converte cada linha do banco de dados em uma instância de User
            return [
                cls(id=row['id'], username=row['username'], is_active=row['is_active'])
                for row in rows
            ]