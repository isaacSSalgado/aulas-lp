from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from app.models.trabalho_model import Trabalho
from app.utils.auth_middleware import login_required

trabalho_bp = Blueprint('trabalho', __name__)

@trabalho_bp.route('/trabalhos/novo', methods=['GET', 'POST'])
@login_required
def cadastrar():

    if request.method == 'POST':
        titulo = request.form.get('titulo')
        materia = request.form.get('materia')
        data_limite = request.form.get('data_limite')
        descricao = request.form.get('descricao')

        # Validação simples de campos obrigatórios
        if not titulo or not materia or not data_limite:
            flash('Preencha todos os campos obrigatórios (*).', 'error')
            return redirect(url_for('trabalho.cadastrar'))

        # Criando objeto e salvando via Active Record
        novo_trabalho = Trabalho(
            titulo=titulo,
            materia=materia,
            data_limite=data_limite,
            descricao=descricao
        )

        if novo_trabalho.salvar():
            flash('Trabalho cadastrado com sucesso!', 'success')
            return redirect(url_for('main.welcome'))
        else:
            flash('Erro ao salvar o trabalho no banco de dados.', 'error')

    return render_template('main/trabalho_register.html')

@trabalho_bp.route('/trabalhos', methods=['GET'])
@login_required
def listar():
   
    todos_trabalhos = Trabalho.listar_todos()

    # Renderiza o HTML passando a lista de objetos Trabalho
    return render_template('main/trabalho_list.html', trabalhos=todos_trabalhos)
    
