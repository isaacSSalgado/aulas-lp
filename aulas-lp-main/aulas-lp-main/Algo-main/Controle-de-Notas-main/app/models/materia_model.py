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
    def possui_trabalhos_pendentes(cls, materia_id):
        with DBConnection() as conn:
            cursor = conn.cursor()
            materia = cls.buscar_por_id(materia_id)
            if not materia:
                return False
            
            nome_completo = f"{materia.codigo} - {materia.nome}"
            cursor.execute(
                "SELECT COUNT(*) AS total FROM trabalhos WHERE materia = ? AND status = 'Pendente'",
                (nome_completo,)
            )
            row = cursor.fetchone()
            return row['total'] > 0

    @classmethod
    def excluir(cls, materia_id):
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM materias WHERE id = ?", (materia_id,))
            return cursor.rowcount > 0