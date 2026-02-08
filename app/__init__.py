from flask import Flask, render_template, g, session, request, redirect, url_for
import os
from .db import get_db

def create_app(test_config=None):
    # Vamos criar a configuracao do app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="a-longer-secret-key-for-dev",
        DATABASE=os.path.join(app.instance_path, "app.sqlite")
    )

    if test_config is None:
        # Carregar a configuracao do arquivo instance, se existir
        app.config.from_pyfile("config.py", silent=True)
    else:
        # Carregar a configuracao de teste
        app.config.from_mapping(test_config)

    # Garantir que o diretório instance existe
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.before_request
    def load_logged_in_user():
        user_id = session.get('user_id')

        if user_id is None:
            g.user = None
        else:
            g.user = get_db().execute(
                'SELECT * FROM Usuarios WHERE id = ?', (user_id,)
            ).fetchone()

    @app.route("/")
    @app.route('/anuncios')
    def index():
        """Rota unificada: Início = Notícias/Anúncios"""
        db = get_db()
        anuncios = db.execute('SELECT titulo, conteudo, data_publicacao FROM Anuncios ORDER BY data_publicacao DESC').fetchall()
        return render_template('anuncios.html', anuncios=anuncios)
    
    # Alias para compatibilidade
    app.add_url_rule('/inicio', 'inicio', index)
    
    @app.route('/verificar_boletim')
    def verificar_boletim():
        """Página pública para verificar boletim inserindo token"""
        token = request.args.get('token')
        if token:
            # Redirecionar para a rota do blueprint student que valida o token
            return redirect(url_for('student.verificar_boletim', token=token))
        return render_template('verificar_boletim.html', valido=None)
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import student
    app.register_blueprint(student.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    from . import professor
    app.register_blueprint(professor.bp)

    from . import perfil
    app.register_blueprint(perfil.bp)
    
    return app
