from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from app.models.user_model import User
from app.utils.auth_middleware import login_required, admin_required, professor_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        flash('Você já está logado. Saia da conta atual para entrar com outro usuário.', 'info')
        return redirect(url_for('main.welcome'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.autenticar(username, password)
        if user:
            session['user_id'] = user.id
            session['username'] = user.username
            session['perfil'] = user.perfil  # Salva 'admin', 'professor' ou 'aluno'
            flash(f'Bem-vindo, {user.username}!', 'success')
            return redirect(url_for('main.welcome'))
        else:
            flash('Usuário ou senha inválidos.', 'error')

    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    session.clear()
    flash('Você saiu do sistema.', 'success')
    return redirect(url_for('auth.login'))


# =========================================================
# CADASTRO DE PROFESSORES (Exclusivo do Admin)
# =========================================================
@auth_bp.route('/professores/novo', methods=['GET', 'POST'])
@admin_required
def cadastrar_professor():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password:
            flash('Preencha todos os campos obrigatórios.', 'error')
            return redirect(url_for('auth.cadastrar_professor'))

        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return redirect(url_for('auth.cadastrar_professor'))

        novo_prof = User(username=username, password=password, perfil='professor')
        if novo_prof.salvar():
            flash(f'Professor "{username}" cadastrado com sucesso!', 'success')
            return redirect(url_for('main.welcome'))
        else:
            flash('Este nome de usuário já está em uso.', 'error')

    return render_template('auth/register_professor.html')


# =========================================================
# CADASTRO DE ALUNOS (Exclusivo de Professores e Admin)
# =========================================================
@auth_bp.route('/alunos/novo', methods=['GET', 'POST'])
@professor_required
def cadastrar_aluno():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if not username or not password:
            flash('Preencha todos os campos obrigatórios.', 'error')
            return redirect(url_for('auth.cadastrar_aluno'))

        if password != confirm_password:
            flash('As senhas não coincidem.', 'error')
            return redirect(url_for('auth.cadastrar_aluno'))

        novo_aluno = User(username=username, password=password, perfil='aluno')
        if novo_aluno.salvar():
            flash(f'Aluno "{username}" cadastrado com sucesso!', 'success')
            return redirect(url_for('main.welcome'))
        else:
            flash('Este nome de usuário já está em uso.', 'error')

    return render_template('auth/register_aluno.html')