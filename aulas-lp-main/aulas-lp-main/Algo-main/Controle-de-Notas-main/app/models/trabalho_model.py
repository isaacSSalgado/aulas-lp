import sqlite3
from datetime import datetime, date
from app.utils.db import DBConnection

class Trabalho:
    def __init__(self, titulo, materia, data_limite, aluno_id, descricao=None, status='Pendente', arquivo_entrega=None, aluno_nome=None, id=None):
        self.id = id
        self.titulo = titulo
        self.materia = materia
        self.data_limite = data_limite
        self.aluno_id = aluno_id
        self.descricao = descricao or ''
        self.status = status
        self.arquivo_entrega = arquivo_entrega
        self.aluno_nome = aluno_nome

    def salvar(self):
        with DBConnection() as conn:
            cursor = conn.cursor()
            try:
                if self.id is None:
                    sql = """
                        INSERT INTO trabalhos (titulo, materia, data_limite, descricao, status, arquivo_entrega, aluno_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """
                    cursor.execute(sql, (self.titulo, self.materia, self.data_limite, self.descricao, self.status, self.arquivo_entrega, self.aluno_id))
                    self.id = cursor.lastrowid
                else:
                    sql = """
                        UPDATE trabalhos
                        SET titulo = ?, materia = ?, data_limite = ?, descricao = ?, status = ?, arquivo_entrega = ?, aluno_id = ?
                        WHERE id = ?
                    """
                    cursor.execute(sql, (self.titulo, self.materia, self.data_limite, self.descricao, self.status, self.arquivo_entrega, self.aluno_id, self.id))
                return True
            except sqlite3.Error as e:
                print(f"Erro ao salvar trabalho: {e}")
                return False

    @classmethod
    def registrar_entrega(cls, trabalho_id, nome_arquivo):
        """Salva o nome do arquivo enviado pelo aluno e marca como Concluído."""
        with DBConnection() as conn:
            cursor = conn.cursor()
            sql = "UPDATE trabalhos SET arquivo_entrega = ?, status = 'Concluído' WHERE id = ?"
            cursor.execute(sql, (nome_arquivo, trabalho_id))
            return cursor.rowcount > 0

    @classmethod
    def listar_por_perfil(cls, user_id, perfil):
        with DBConnection() as conn:
            cursor = conn.cursor()
            if perfil in ('professor', 'admin'):
                sql = """
                    SELECT t.*, u.username AS aluno_nome
                    FROM trabalhos t
                    JOIN users u ON t.aluno_id = u.id
                    ORDER BY t.status DESC, t.data_limite ASC
                """
                cursor.execute(sql)
            else:
                sql = """
                    SELECT t.*, u.username AS aluno_nome
                    FROM trabalhos t
                    JOIN users u ON t.aluno_id = u.id
                    WHERE t.aluno_id = ?
                    ORDER BY t.status DESC, t.data_limite ASC
                """
                cursor.execute(sql, (user_id,))

            rows = cursor.fetchall()
            return [
                cls(
                    id=row['id'],
                    titulo=row['titulo'],
                    materia=row['materia'],
                    data_limite=row['data_limite'],
                    aluno_id=row['aluno_id'],
                    descricao=row['descricao'],
                    status=row['status'],
                    arquivo_entrega=row['arquivo_entrega'],
                    aluno_nome=row['aluno_nome']
                )
                for row in rows
            ]

    @classmethod
    def buscar_por_id(cls, trabalho_id):
        with DBConnection() as conn:
            cursor = conn.cursor()
            sql = """
                SELECT t.*, u.username AS aluno_nome
                FROM trabalhos t
                LEFT JOIN users u ON t.aluno_id = u.id
                WHERE t.id = ?
            """
            cursor.execute(sql, (trabalho_id,))
            row = cursor.fetchone()
            if row:
                return cls(
                    id=row['id'],
                    titulo=row['titulo'],
                    materia=row['materia'],
                    data_limite=row['data_limite'],
                    aluno_id=row['aluno_id'],
                    descricao=row['descricao'],
                    status=row['status'],
                    arquivo_entrega=row['arquivo_entrega'],
                    aluno_nome=row['aluno_nome']
                )
            return None

    @classmethod
    def alterar_status(cls, trabalho_id, novo_status):
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE trabalhos SET status = ? WHERE id = ?", (novo_status, trabalho_id))
            return cursor.rowcount > 0

    @classmethod
    def excluir(cls, trabalho_id):
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM trabalhos WHERE id = ?", (trabalho_id,))
            return cursor.rowcount > 0

    @classmethod
    def listar_materias(cls):
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT DISTINCT materia FROM trabalhos ORDER BY materia ASC")
            return [row['materia'] for row in cursor.fetchall()]

    @classmethod
    def buscar_alertas_prazo(cls, user_id, perfil):
        trabalhos = cls.listar_por_perfil(user_id, perfil)
        hoje = date.today()
        alertas = []

        for t in trabalhos:
            if t.status == 'Pendente' and t.data_limite:
                try:
                    data_entrega = datetime.strptime(str(t.data_limite), '%Y-%m-%d').date()
                    dias_restantes = (data_entrega - hoje).days

                    if 0 <= dias_restantes <= 7:
                        nivel = 'urgente' if dias_restantes <= 1 else 'aviso'
                        alertas.append({
                            'trabalho': t,
                            'dias': dias_restantes,
                            'nivel': nivel
                        })
                except ValueError:
                    continue

        return alertas