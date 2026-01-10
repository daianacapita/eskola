from flask import Flask, render_template, g, session, jsonify, request
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
    def index():
        db = get_db()
        anuncios = db.execute('SELECT titulo, conteudo, data_publicacao FROM Anuncios ORDER BY data_publicacao DESC LIMIT 5').fetchall()
        return render_template('index.html', anuncios=anuncios)
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)

    from . import student
    app.register_blueprint(student.bp)

    from . import admin
    app.register_blueprint(admin.bp)

    @app.route('/anuncios')
    def anuncios():
        db = get_db()
        anuncios = db.execute('SELECT titulo, conteudo, data_publicacao FROM Anuncios ORDER BY data_publicacao DESC').fetchall()
        return render_template('anuncios.html', anuncios=anuncios)

    @app.route('/api/anuncios')
    def api_anuncios():
        db = get_db()
        page = int(request.args.get('page', 1))
        search = request.args.get('search', '')
        limit = 10
        offset = (page - 1) * limit

        query = 'SELECT titulo, conteudo, data_publicacao FROM Anuncios'
        params = []
        if search:
            query += ' WHERE titulo LIKE ? OR conteudo LIKE ?'
            params.extend([f'%{search}%', f'%{search}%'])
        query += ' ORDER BY data_publicacao DESC LIMIT ? OFFSET ?'
        params.extend([limit, offset])

        anuncios = db.execute(query, params).fetchall()

        # Check if there are more
        next_offset = offset + limit
        next_params = params[:-2] if search else []
        next_params.extend([1, next_offset])
        next_query = 'SELECT titulo FROM Anuncios'
        if search:
            next_query += ' WHERE titulo LIKE ? OR conteudo LIKE ?'
        next_query += ' ORDER BY data_publicacao DESC LIMIT ? OFFSET ?'
        has_more = bool(db.execute(next_query, next_params).fetchone())

        return jsonify({
            'anuncios': [dict(anuncio) for anuncio in anuncios],
            'hasMore': has_more
        })
    
    return app
