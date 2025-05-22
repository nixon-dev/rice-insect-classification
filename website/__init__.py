from flask import Flask
import os

def create_app():
    app = Flask(__name__)


    from .views import views
    from .auth import auth
    from .ai import ai
    from database import MySQL

    app.register_blueprint(views, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(ai, url_prefix="/")
    mysql = MySQL(app)

    app.config['UPLOAD_FOLDER'] = 'website/static/upload'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    return app
