import os
from datetime import date
from flask import Blueprint, request, render_template, redirect, url_for, flash, session, current_app, send_from_directory
from werkzeug.utils import secure_filename
from app.models.trabalho_model import Trabalho
from app.models.user_model import User
from app.utils.auth_middleware import login_required, professor_required
from app.models.materia_model import Materia

trabalho_bp = Blueprint('trabalho', __name__)

EXTENSOES_PERMITIDAS = {'pdf', 'doc', 'docx', 'txt', 'zip', 'rar', 'py', 'java', 'c', 'cpp', 'html', 'css', 'js', 'png', 'jpg', 'jpeg'}

def arquivo_permitido(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in EXTENSOES_PERMITIDAS

def get_upload_folder():
    pasta = os.path.join(current_app.root_path, 'static', 'uploads')
    os.makedirs(pasta, exist_ok=True)
    return pasta


@trabalho_bp.route('/trabalhos', methods=['GET'])
@login_required
def listar():
    user_id = session.get('user_id')
    perfil = session.get('perfil')
    todos_trabalhos = Trabalho.listar_por_perfil(user_id, perfil)
    return render_template('main/trabalho_list.html', trabalhos=todos_trabalhos)


@trabalho_bp.route('/trabalhos/novo', methods=['GET', 'POST'])
@login_required
@professor_required
def cadastrar():
    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        materia = request.form.get('materia', '').strip()
        data_limite = request.form.get('data_limite')
        descricao = request.form.get('descricao', '').strip()
        aluno_id = request.form.get('aluno_id')

        if not titulo or not materia or not data_limite or not aluno_id:
            flash('Preencha todos os campos obrigatórios (*).', 'error')
            return redirect(url_for('trabalho.cadastrar'))

        if aluno_id == 'todos':
            todos_alunos = User.listar_alunos()
            if not todos_alunos:
                flash('Nenhum aluno cadastrado para receber o trabalho.', 'error')
                return redirect(url_for('trabalho.cadastrar'))

            enviados = 0
            for aluno in todos_alunos:
                novo_trabalho = Trabalho(
                    titulo=titulo,
                    materia=materia,
                    data_limite=data_limite,
                    aluno_id=aluno.id,
                    descricao=descricao
                )
                if novo_trabalho.salvar():
                    enviados += 1

            current_app.logger.info(f"Trabalho '{titulo}' ({materia}) enviado em lote para {enviados} aluno(s) pelo usuário ID {session.get('user_id')}.")
            flash(f'Trabalho enviado com sucesso para {enviados} aluno(s)!', 'success')
            return redirect(url_for('trabalho.listar'))
        else:
            novo_trabalho = Trabalho(
                titulo=titulo,
                materia=materia,
                data_limite=data_limite,
                aluno_id=aluno_id,
                descricao=descricao
            )
            if novo_trabalho.salvar():
                current_app.logger.info(f"Trabalho '{titulo}' ({materia}) atribuído ao aluno ID {aluno_id} pelo usuário ID {session.get('user_id')}.")
                flash('Trabalho cadastrado com sucesso!', 'success')
                return redirect(url_for('trabalho.listar'))
            else:
                flash('Erro ao salvar o trabalho no banco de dados.', 'error')

    materias_cadastradas = Materia.listar_todas()
    alunos_cadastrados = User.listar_alunos()
    hoje = date.today().isoformat()
    return render_template(
        'main/trabalho_register.html',
        materias=materias_cadastradas,
        alunos=alunos_cadastrados,
        hoje=hoje
    )

    materias_existentes = Trabalho.listar_materias()
    alunos_cadastrados = User.listar_alunos()
    hoje = date.today().isoformat()
    return render_template('main/trabalho_register.html', materias=materias_existentes, alunos=alunos_cadastrados, hoje=hoje)


@trabalho_bp.route('/trabalhos/<int:id>/entregar', methods=['POST'])
@login_required
def entregar(id):
    trabalho = Trabalho.buscar_por_id(id)
    if not trabalho:
        flash('Trabalho não encontrado.', 'error')
        return redirect(url_for('trabalho.listar'))

    if session.get('perfil') != 'aluno' or trabalho.aluno_id != session.get('user_id'):
        flash('Apenas o aluno responsável pode enviar este trabalho.', 'error')
        return redirect(url_for('trabalho.listar'))

    if 'arquivo' not in request.files or request.files['arquivo'].filename == '':
        flash('Selecione um arquivo antes de enviar.', 'error')
        return redirect(url_for('trabalho.listar'))

    arquivo = request.files['arquivo']
    if not arquivo_permitido(arquivo.filename):
        flash('Formato de arquivo não permitido. Envie PDF, DOCX, ZIP, código ou imagem.', 'error')
        return redirect(url_for('trabalho.listar'))

    # Prefixa com o ID do trabalho e do aluno para evitar sobrescrever arquivos com mesmo nome
    nome_seguro = secure_filename(arquivo.filename)
    nome_final = f"trab_{id}_aluno_{session.get('user_id')}_{nome_seguro}"
    caminho_salvar = os.path.join(get_upload_folder(), nome_final)

    arquivo.save(caminho_salvar)
    Trabalho.registrar_entrega(id, nome_final)

    flash('Trabalho enviado e marcado como Concluído com sucesso!', 'success')
    return redirect(url_for('trabalho.listar'))


@trabalho_bp.route('/trabalhos/<int:id>/download', methods=['GET'])
@login_required
def baixar_entrega(id):
    trabalho = Trabalho.buscar_por_id(id)
    if not trabalho or not trabalho.arquivo_entrega:
        flash('Nenhum arquivo encontrado para este trabalho.', 'error')
        return redirect(url_for('trabalho.listar'))

    # Permite download apenas para professores/admin ou para o próprio aluno que enviou
    if session.get('perfil') in ('professor', 'admin') or trabalho.aluno_id == session.get('user_id'):
        return send_from_directory(get_upload_folder(), trabalho.arquivo_entrega, as_attachment=True)

    flash('Você não tem permissão para baixar este arquivo.', 'error')
    return redirect(url_for('trabalho.listar'))


@trabalho_bp.route('/trabalhos/<int:id>/editar', methods=['GET', 'POST'])
@login_required
@professor_required
def editar(id):
    trabalho = Trabalho.buscar_por_id(id)
    if not trabalho:
        flash('Trabalho não encontrado.', 'error')
        return redirect(url_for('trabalho.listar'))

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        materia = request.form.get('materia', '').strip()
        data_limite = request.form.get('data_limite')
        descricao = request.form.get('descricao', '').strip()
        status = request.form.get('status')
        aluno_id = request.form.get('aluno_id')

        if not titulo or not materia or not data_limite or not aluno_id:
            flash('Preencha todos os campos obrigatórios (*).', 'error')
            return redirect(url_for('trabalho.editar', id=id))

        trabalho.titulo = titulo
        trabalho.materia = materia
        trabalho.data_limite = data_limite
        trabalho.descricao = descricao
        trabalho.status = status
        trabalho.aluno_id = aluno_id

        if trabalho.salvar():
            current_app.logger.info(f"Trabalho ID {id} atualizado pelo usuário ID {session.get('user_id')}.")
            flash('Trabalho atualizado com sucesso!', 'success')
            return redirect(url_for('trabalho.listar'))
        flash('Erro ao atualizar o trabalho.', 'error')

    materias_cadastradas = Materia.listar_todas()
    alunos_cadastrados = User.listar_alunos()
    return render_template(
        'main/trabalho_edit.html',
        trabalho=trabalho,
        materias=materias_cadastradas,
        alunos=alunos_cadastrados
    )


@trabalho_bp.route('/trabalhos/<int:id>/excluir', methods=['POST'])
@login_required
@professor_required
def excluir(id):
    trabalho = Trabalho.buscar_por_id(id)
    # Remove o arquivo físico do disco caso exista antes de excluir do banco
    if trabalho and trabalho.arquivo_entrega:
        caminho = os.path.join(get_upload_folder(), trabalho.arquivo_entrega)
        if os.path.exists(caminho):
            os.remove(caminho)

    if Trabalho.excluir(id):
        flash('Trabalho excluído com sucesso!', 'success')
    else:
        flash('Erro ao excluir o trabalho.', 'error')

    return redirect(url_for('trabalho.listar'))