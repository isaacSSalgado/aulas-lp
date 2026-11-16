from flask import Blueprint, render_template, session, redirect, url_for
from ..utils import login_required
from ..models.user_model import User

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/welcome')
@login_required # <-- Middleware bloqueando acesso anônimo
def welcome():
    return render_template('main/dashboard.html', username=session.get('username'))

@main_bp.route('/usuarios') # Ou a URL que você definiu para listar usuários
@login_required
def list_users():
    usuarios = User.listar_todos()

    # 2. ATENÇÃO AQUI: O nome antes do '=' (users) deve ser igual ao do HTML ({% for user in users %})
    return render_template('main/list.html', users=usuarios)
