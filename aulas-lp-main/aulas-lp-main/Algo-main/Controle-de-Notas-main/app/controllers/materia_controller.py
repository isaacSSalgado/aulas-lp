from flask import Blueprint, render_template, request, redirect, url_for, flash, session, current_app
from app.models.materia_model import Materia
from app.utils.auth_middleware import login_required, professor_required

materia_bp = Blueprint('materia', __name__)

@materia_bp.route('/materias', methods=['GET'])
@login_required
@professor_required
def listar():
    materias = Materia.listar_todas()
    return render_template('main/materia_list.html', materias=materias)


@materia_bp.route('/materias/nova', methods=['POST'])
@login_required
@professor_required
def cadastrar():
    nome = request.form.get('nome', '').strip()
    codigo = request.form.get('codigo', '').strip().upper()
    user_id = session.get('user_id')

    if not nome or not codigo:
        flash('Preencha o nome e a sigla/código da matéria.', 'error')
        return redirect(url_for('materia.listar'))

    if len(nome) < 3:
        flash('O nome da matéria deve ter pelo menos 3 caracteres.', 'error')
        return redirect(url_for('materia.listar'))

    nova_materia = Materia(nome=nome, codigo=codigo, usuario_id=user_id)
    if nova_materia.salvar():
        current_app.logger.info(f"Matéria '{nome} ({codigo})' cadastrada pelo usuário ID {user_id}.")
        flash('Matéria cadastrada com sucesso!', 'success')
    else:
        current_app.logger.error(f"Falha ao cadastrar matéria '{nome}' pelo usuário ID {user_id}.")
        flash('Erro ao cadastrar matéria.', 'error')

    return redirect(url_for('materia.listar'))


@materia_bp.route('/materias/<int:id>/excluir', methods=['POST'])
@login_required
@professor_required
def excluir(id):
    user_id = session.get('user_id')

    if Materia.possui_trabalhos_pendentes(id):
        flash('Não é possível excluir esta matéria pois existem trabalhos pendentes vinculados a ela.', 'error')
        return redirect(url_for('materia.listar'))

    if Materia.excluir(id):
        current_app.logger.info(f"Matéria ID {id} excluída pelo usuário ID {user_id}.")
        flash('Matéria excluída com sucesso!', 'success')
    else:
        current_app.logger.warning(f"Falha ao excluir matéria ID {id} pelo usuário ID {user_id}.")
        flash('Não foi possível excluir a matéria.', 'error')

    return redirect(url_for('materia.listar'))