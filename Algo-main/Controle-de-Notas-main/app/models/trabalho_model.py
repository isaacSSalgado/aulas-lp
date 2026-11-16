from app.utils.db import DBConnection

class Trabalho:
    def __init__(self, titulo, materia, data_limite, descricao=None, id=None):
        self.id = id
        self.titulo = titulo
        self.materia = materia
        self.data_limite = data_limite
        self.descricao = descricao

    def salvar(self):
        """(Create/Update) Insere um novo trabalho ou atualiza um existente."""
        with DBConnection() as conn:
            cursor = conn.cursor()
            
            if self.id is None:
                sql = """
                    INSERT INTO trabalhos (titulo, materia, data_limite, descricao)
                    VALUES (?, ?, ?, ?)
                """
                cursor.execute(sql, (self.titulo, self.materia, self.data_limite, self.descricao))
                self.id = cursor.lastrowid
                return True
            else:
                sql = """
                    UPDATE trabalhos 
                    SET titulo = ?, materia = ?, data_limite = ?, descricao = ?
                    WHERE id = ?
                """
                cursor.execute(sql, (self.titulo, self.materia, self.data_limite, self.descricao, self.id))
                return True

    @classmethod
    def buscar_por_id(cls, trabalho_id):
        """(Read) Busca um trabalho específico pelo ID."""
        with DBConnection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM trabalhos WHERE id = ?", (trabalho_id,))
            row = cursor.fetchone()
            
            if row:
                return cls(
                    id=row['id'],
                    titulo=row['titulo'],
                    materia=row['materia'],
                    data_limite=row['data_limite'],
                    descricao=row['descricao']
                )
            return None
        
    @classmethod
    def listar_todos(cls):
        """(Read) Busca todos os trabalhos e retorna uma lista de objetos Trabalho."""
        with DBConnection() as conn:
            cursor = conn.cursor()
            # Ordena pela data limite para mostrar os mais urgentes primeiro
            cursor.execute("SELECT * FROM trabalhos ORDER BY data_limite ASC")
            rows = cursor.fetchall()
            
            # Converte cada linha do banco de dados em uma instância de Trabalho
            return [
                cls(
                    id=row['id'],
                    titulo=row['titulo'],
                    materia=row['materia'],
                    data_limite=row['data_limite'],
                    descricao=row['descricao']
                )
                for row in rows
            ]