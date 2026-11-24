import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database.db')

class DBConnection:
    """Gestor de contexto para a ligação ao SQLite."""
    def __enter__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        return self.conn

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Se não ocorreu nenhuma exceção durante o uso, faz commit
        if exc_type is None:
            self.conn.commit()
        else:
            # Se algo falhou, reverte as alterações para não corromper dados
            self.conn.rollback()
        
        # Fecha sempre a ligação
        self.conn.close()
