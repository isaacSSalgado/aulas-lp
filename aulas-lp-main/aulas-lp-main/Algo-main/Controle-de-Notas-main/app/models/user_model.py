import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from app.utils.db import DBConnection

class User:
    def __init__(self, username, password=None, password_hash=None, perfil='aluno', is_active=1, id=None):
        self.id = id
        self.username = username
        self.perfil = perfil
        self.is_active = is_active
        
        if password:
            self.password_hash = generate_password_hash(password)
        else:
            self.password_hash = password_hash

    def verificar_senha(self, password):
        return check_password_hash(self.password_hash, password)

    @classmethod
    def autenticar(cls, username, password):
        """Busca o usuário pelo username e valida a senha."""
        user = cls.buscar_por_username(username)
        if user and user.is_active and user.verificar_senha(password):
            return user
        return None

    def salvar(self):
        with DBConnection() as conn:
            cursor = conn.cursor()
            try:
                if self.id is None:
                    sql = "INSERT INTO users (username, password_hash, perfil, is_active) VALUES (?, ?, ?, ?)"
                    cursor.execute(sql, (self.username, self.password_hash, self.perfil, self.is_active))
                    self.id = cursor.lastrowid
                else:
                    sql = "UPDATE users SET username = ?, password_hash = ?, perfil = ?, is_active = ? WHERE id = ?"
                    cursor.execute(sql, (self.username, self.password_hash, self.perfil, self.is_active, self.id))
                return True
            except sqlite3.IntegrityError:
                return False

    @classmethod
    def buscar_por_username(cls, username):
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    perfil=row['perfil'],
                    is_active=row['is_active']
                )
            return None

    @classmethod
    def buscar_por_id(cls, user_id):
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    perfil=row['perfil'],
                    is_active=row['is_active']
                )
            return None

    @classmethod
    def listar_por_perfil(cls, perfil):
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE perfil = ? ORDER BY username ASC", (perfil,))
            rows = cursor.fetchall()
            return [
                cls(
                    id=row['id'],
                    username=row['username'],
                    password_hash=row['password_hash'],
                    perfil=row['perfil'],
                    is_active=row['is_active']
                )
                for row in rows
            ]

    @classmethod
    def listar_alunos(cls):
        return cls.listar_por_perfil('aluno')