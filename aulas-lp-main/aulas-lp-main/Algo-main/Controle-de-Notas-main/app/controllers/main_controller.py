from flask import Blueprint, current_app, make_response, render_template, redirect, url_for, session, request, flash
from app.models.trabalho_model import Trabalho
from app.models.user_model import User
from app.utils.auth_middleware import login_required, professor_required, admin_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return redirect(url_for('main.welcome'))

@main_bp.route('/welcome')
@login_required
def welcome():
    user_id = session.get('user_id')
    perfil = session.get('perfil')

    alertas_prazo = Trabalho.buscar_alertas_prazo(user_id, perfil)
    todos_trabalhos = Trabalho.listar_por_perfil(user_id, perfil)

    resumo = {
        'total': len(todos_trabalhos),
        'pendentes': sum(1 for t in todos_trabalhos if t.status == 'Pendente'),
        'concluidos': sum(1 for t in todos_trabalhos if t.status == 'Concluído')
    }

    return render_template('main/dashboard.html', alertas=alertas_prazo, resumo=resumo)

@main_bp.route('/admin/usuarios', methods=['GET'])
@login_required
@admin_required
def listar_usuarios():
    professores = User.listar_professores()
    alunos = User.listar_alunos()
    return render_template('main/admin_usuarios.html', professores=professores, alunos=alunos)

@main_bp.route('/alunos/novo', methods=['GET', 'POST'])
@login_required
@professor_required
def cadastrar_aluno():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password:
            flash('Preencha todos os campos obrigatórios.', 'error')
            return redirect(url_for('main.cadastrar_aluno'))

        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return redirect(url_for('main.cadastrar_aluno'))

        novo_aluno = User(username=username, password=password, perfil='aluno')
        if novo_aluno.salvar():
            flash(f'Aluno "{username}" cadastrado com sucesso!', 'success')
            return redirect(url_for('main.welcome'))
        else:
            flash('Este nome de usuário já está em uso.', 'error')

    return render_template('auth/register_aluno.html')

@main_bp.route('/alternar-tema')
def alternar_tema():
    tema_atual = request.cookies.get('tema', 'claro')
    novo_tema = 'escuro' if tema_atual == 'claro' else 'claro'
    
    # Redireciona de volta para a página anterior ou para o painel
    destino = request.referrer or url_for('main.welcome')
    resposta = make_response(redirect(destino))
    
    # Salva o cookie no navegador por 30 dias (60s * 60m * 24h * 30d)
    resposta.set_cookie('tema', novo_tema, max_age=60 * 60 * 24 * 30)
    return resposta

@main_bp.route('/admin/usuarios/<int:id>/excluir', methods=['POST'])
@login_required
@admin_required
def excluir_usuario(id):
    if id == session.get('user_id'):
        flash('Você não pode remover sua própria conta de administrador.', 'error')
        return redirect(url_for('main.listar_usuarios'))

    if User.excluir(id):
        current_app.logger.info(f"Usuário ID {id} removido pelo administrador ID {session.get('user_id')}.")
        flash('Usuário removido com sucesso!', 'success')
    else:
        current_app.logger.warning(f"Falha ao tentar remover usuário ID {id} pelo admin ID {session.get('user_id')}.")
        flash('Não foi possível remover o usuário.', 'error')

    return redirect(url_for('main.listar_usuarios'))