# Controle de Trabalhos

Sistema web desenvolvido em **Python** com o microframework **Flask** e banco de dados **SQLite** para gerenciamento acadêmico de disciplinas, atribuição de trabalhos com prazos e envio de entregas por alunos.

---

## Funcionalidades e Controle de Acesso (RBAC)

O sistema implementa controle de acesso hierárquico baseado em perfis de usuário (`admin`, `professor` e `aluno`) por meio de *middlewares* (`@login_required`, `@admin_required`, `@professor_required` e `@logout_required`):

* **Administrador (`admin`):**
  * Cadastra novos professores no sistema.
  * Visualiza e gerencia (exclui) contas de professores e alunos cadastrados.
* **Professor (`professor`):**
  * **Gestão de Matérias:** Cadastra, lista e exclui disciplinas do catálogo (com trava de integridade que impede excluir matérias que possuam trabalhos pendentes).
  * **Gestão de Trabalhos:** Cria, edita e exclui atividades vinculadas às matérias cadastradas, com suporte a atribuição individual ou em lote (*Todos os Alunos*) e atalhos rápidos de prazo.
  * **Gestão de Alunos:** Cadastra novos alunos e acompanha o status e os arquivos entregues em cada atividade.
* **Aluno (`aluno`):**
  * Visualiza o painel com indicadores de atividades pendentes/concluídas e alertas de prazos próximos.
  * Realiza o envio (upload) e o download de arquivos das suas entregas.
* **Recursos Gerais:**
  * Alternância de **Tema Claro / Tema Escuro** com persistência via **Cookies**.
  * Páginas personalizadas para erros HTTP (`403`, `404` e `500`) e auditoria de eventos críticos via `app.logger`.

---

## Arquitetura do Projeto (MVC)

O projeto segue o padrão arquitetural **Model-View-Controller (MVC)** utilizando **Blueprints** do Flask:

```text
Controle-de-Notas-main/
├── app/
│   ├── controllers/          # Rotas e regras de controle HTTP (Blueprints)
│   │   ├── auth_controller.py
│   │   ├── main_controller.py
│   │   ├── materia_controller.py
│   │   └── trabalho_controller.py
│   ├── models/               # Classes POO e acesso encapsulado ao SQLite
│   │   ├── materia_model.py
│   │   ├── trabalho_model.py
│   │   └── user_model.py
│   ├── static/               # Arquivos CSS e diretório de uploads
│   │   ├── css/
│   │   └── uploads/
│   ├── utils/                # Utilitários de conexão e segurança
│   │   ├── auth_middleware.py
│   │   └── db.py             # Classe DatabaseConnection (__enter__ / __exit__)
│   ├── views/                # Templates HTML com herança Jinja2
│   │   ├── auth/
│   │   ├── errors/
│   │   ├── main/
│   │   └── base.html
│   └── __init__.py           # Application Factory, registro de Blueprints e Error Handlers
├── iniciar_bd.py             # Script de criação das tabelas e usuário admin inicial
├── requirements.txt          # Dependências do projeto
└── run.py                    # Ponto de entrada da aplicação