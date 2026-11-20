"""Crea la app Flask, conecta la base de datos y registra las rutas."""
from decimal import Decimal

import click
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate

from config import Config
from models import Category, Product, db
from routes import api

migrate = Migrate()

def create_app():
    if not Config.SQLALCHEMY_DATABASE_URI:
        raise RuntimeError(
            "Falta DATABASE_URL. Copiá .env.example como .env y completá los datos de MySQL."
        )

    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app, resources={r"/api/*": {"origins": Config.CORS_ORIGINS}})

    app.register_blueprint(api)

    return app


app = create_app()
