"""Configuración: lee las variables desde el archivo .env"""
import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Se pueden poner varios orígenes separados por coma
    CORS_ORIGINS = [
        o.strip()
        for o in os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173").split(",")
        if o.strip()
    ]
    # Tope de subida para la importación de Excel (5 MB)
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
