from flask import request, render_template, redirect, url_for, session, flash, Blueprint
from app.models.user_model import User


auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Usando o método da classe para autenticar
        user = User.autenticar(username, password)

        if user:
            # Acesso direto aos atributos do objeto (user.id em vez de user['id'])
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for('main.welcome'))
        else:
            flash('Utilizador ou palavra-passe inválidos.', 'error')

    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('auth.login'))

@auth_bp.route('/cadastro', methods=['GET', 'POST']) 
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('As palavras-passe não coincidem.', 'error')
            return redirect(url_for('auth.register'))

        # Criamos a instância e depois mandamos salvar (Active Record)
        novo_utilizador = User(username=username, password=password)
        sucesso = novo_utilizador.salvar()

        if sucesso:
            flash('Conta criada com sucesso!', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('Este nome de utilizador já está em uso.', 'error')

    return render_template('auth/register.html')

