"""Endpoints de la API, un archivo por tema. Todos cuelgan del mismo blueprint `api`."""
from flask import Blueprint

api = Blueprint("api", __name__, url_prefix="/api")

# Cada módulo registra sus rutas en `api` al importarse (por eso va después de crearlo)
from routes import categories, health, importing, products  # noqa: E402,F401
