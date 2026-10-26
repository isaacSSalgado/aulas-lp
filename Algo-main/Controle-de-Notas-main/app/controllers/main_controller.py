from flask import Blueprint, render_template, session
from ..utils import login_required
from ..models.user_model import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/welcome')
@login_required # <-- Middleware bloqueando acesso anônimo
def welcome():
    return render_template('main/dashboard.html', username=session.get('username'))

@main_bp.route('/usuarios')
def listar_usuarios():
    # 1. Busca a lista de objetos de usuários no banco
    usuarios = User.listar_todos()
    
    # 2. Renderiza o HTML passando a lista para a variável 'usuarios'
    return render_template('main/list.html', usuarios=usuarios)