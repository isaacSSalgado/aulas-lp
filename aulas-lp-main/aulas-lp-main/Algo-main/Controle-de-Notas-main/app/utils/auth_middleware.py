from functools import wraps
from flask import session, redirect, url_for, flash, g, abort

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models.user_model import User
        user_id = session.get('user_id')
        
        if not user_id:
            flash('Faça login para acessar esta página.', 'warning')
            return redirect(url_for('auth.login'))

        usuario = User.buscar_por_id(user_id)
        if not usuario:
            session.clear()
            flash('Sessão inválida ou usuário removido. Faça login novamente.', 'error')
            return redirect(url_for('auth.login'))

        g.usuario = usuario
        return f(*args, **kwargs)
    return decorated_function


def professor_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models.user_model import User
        usuario = getattr(g, 'usuario', None) or User.buscar_por_id(session.get('user_id'))
        
        if not usuario or usuario.perfil != 'professor':
            abort(403)

        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app.models.user_model import User
        usuario = getattr(g, 'usuario', None) or User.buscar_por_id(session.get('user_id'))
        
        if not usuario or usuario.perfil != 'admin':
            abort(403)

        return f(*args, **kwargs)
    return decorated_function