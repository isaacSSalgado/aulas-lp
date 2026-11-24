import sqlite3
from app.utils.db import DBConnection

class Materia:
    def __init__(self, nome, codigo, usuario_id, id=None):
        self.id = id
        self.nome = nome
        self.codigo = codigo
        self.usuario_id = usuario_id

    def salvar(self):
        with DBConnection() as conn:
            cursor = conn.cursor()
            try:
                sql = "INSERT INTO materias (nome, codigo, usuario_id) VALUES (?, ?, ?)"
                cursor.execute(sql, (self.nome, self.codigo, self.usuario_id))
                self.id = cursor.lastrowid
                return True
            except sqlite3.Error as e:
                print(f"Erro ao salvar matéria: {e}")
                return False

    @classmethod
    def listar_por_usuario(cls, usuario_id, perfil):
        with DBConnection() as conn:
            cursor = conn.cursor()
            if perfil == 'admin':
                cursor.execute("SELECT * FROM materias ORDER BY nome ASC")
            else:
                cursor.execute("SELECT * FROM materias WHERE usuario_id = ? ORDER BY nome ASC", (usuario_id,))
            
            rows = cursor.fetchall()
            return [
                cls(id=row['id'], nome=row['nome'], codigo=row['codigo'], usuario_id=row['usuario_id'])
                for row in rows
            ]

    @classmethod
    def listar_todas(cls):
        """Retorna todas as matérias cadastradas para preencher o formulário de trabalhos."""
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM materias ORDER BY nome ASC")
            rows = cursor.fetchall()
            return [
                cls(id=row['id'], nome=row['nome'], codigo=row['codigo'], usuario_id=row['usuario_id'])
                for row in rows
            ]

    @classmethod
    def buscar_por_id(cls, materia_id):
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM materias WHERE id = ?", (materia_id,))
            row = cursor.fetchone()
            if row:
                return cls(id=row['id'], nome=row['nome'], codigo=row['codigo'], usuario_id=row['usuario_id'])
            return None

    @classmethod
    def excluir(cls, materia_id, usuario_id, perfil):
        """Exclui validando o dono do registro (ou permitindo se for admin)."""
        with DBConnection() as conn:
            cursor = conn.cursor()
            if perfil == 'admin':
                cursor.execute("DELETE FROM materias WHERE id = ?", (materia_id,))
            else:
                cursor.execute("DELETE FROM materias WHERE id = ? AND usuario_id = ?", (materia_id, usuario_id))
            return cursor.rowcount > 0