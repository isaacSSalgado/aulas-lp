from flask import Flask, render_template, request

app = Flask(__name__, template_folder='views', static_folder='static')
app.secret_key = 'sua_chave_secreta_aqui'

from app.controllers.auth_controller import auth_bp
from app.controllers.main_controller import main_bp
from app.controllers.trabalho_controller import trabalho_bp
from app.controllers.materia_controller import materia_bp

app.register_blueprint(auth_bp)
app.register_blueprint(main_bp)
app.register_blueprint(trabalho_bp)
app.register_blueprint(materia_bp)

@app.errorhandler(404)
def pagina_nao_encontrada(e):
    app.logger.warning(f"Erro 404 - Rota inexistente acessada: {request.path}")
    return render_template('errors/404.html'), 404

@app.errorhandler(403)
def acesso_negado(e):
    app.logger.warning(f"Erro 403 - Acesso proibido em: {request.path}")
    return render_template('errors/403.html'), 403

@app.errorhandler(500)
def erro_interno(e):
    app.logger.error(f"Erro 500 - Falha interna do servidor: {e}")
    return render_template('errors/500.html'), 500