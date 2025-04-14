from flask import Flask

# Création de l'application Flask
def create_app():
    app = Flask(__name__, instance_relative_config=True)

    # Pour éviter les import circulaires
    from . import routes
    app.register_blueprint(routes.bp)

    return app