"""Chequeo de que el servidor y la base de datos respondan."""
from flask import jsonify
from sqlalchemy import text

from models import db
from routes import api


@api.get("/health")
def health():
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        return jsonify({"error": "No se pudo conectar con la base de datos."}), 503
    return jsonify({"status": "ok", "database": "ok"})
