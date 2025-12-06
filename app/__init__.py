from flask import Flask
import os

def create_app(test_config=None):
    # Vamos criar a configuracao do app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY="dev",
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

    @app.route("/")
    def pagina_inicial():
        return "Bem-vindo ao aplicativo Flask!"
    
    from . import db
    db.init_app(app)

    from . import auth
    app.register_blueprint(auth.bp)
    
    return app
