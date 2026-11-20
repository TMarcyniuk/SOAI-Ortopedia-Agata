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

DEFAULT_CATEGORIES = [
    "Muletas",
    "Bastones",
    "Andadores",
    "Sillas de ruedas",
    "Rodilleras",
    "Tobilleras",
    "Fajas",
    "Plantillas",
    "Otros",
]

# Productos de ejemplo para probar: (código, nombre, categoría, precio, stock, mínimo, activo)
DEMO_PRODUCTS = [
    ("MUL-001", "Muleta axilar de aluminio regulable", "Muletas", "28500.00", 12, 4, True),
    ("MUL-002", "Muleta canadiense con apoyo de antebrazo", "Muletas", "34900.00", 3, 5, True),
    ("MUL-003", "Par de gomas para muleta", "Muletas", "3200.00", 40, 10, True),
    ("BAS-001", "Bastón de aluminio regulable", "Bastones", "14500.00", 18, 5, True),
    ("BAS-002", "Bastón tetrápode", "Bastones", "22900.00", 0, 3, True),
    ("BAS-003", "Bastón plegable", "Bastones", "17800.00", 7, 4, True),
    ("AND-001", "Andador fijo de aluminio", "Andadores", "49500.00", 6, 2, True),
    ("AND-002", "Andador con ruedas delanteras", "Andadores", "58900.00", 2, 3, True),
    ("AND-003", "Andador rollator de cuatro ruedas", "Andadores", "129000.00", 4, 2, True),
    ("SIL-001", "Silla de ruedas plegable estándar", "Sillas de ruedas", "215000.00", 3, 1, True),
    ("SIL-002", "Silla de ruedas liviana de aluminio", "Sillas de ruedas", "289000.00", 1, 2, True),
    ("SIL-003", "Silla de baño con respaldo", "Sillas de ruedas", "68500.00", 5, None, True),
    ("ROD-001", "Rodillera elástica talle M", "Rodilleras", "19800.00", 15, 5, True),
    ("ROD-002", "Rodillera elástica talle L", "Rodilleras", "19800.00", 4, 5, True),
    ("ROD-003", "Rodillera con ortesis de rótula", "Rodilleras", "38500.00", 8, 3, True),
    ("ROD-004", "Rodillera articulada con barras laterales", "Rodilleras", "72000.00", 0, 2, True),
    ("TOB-001", "Tobillera elástica talle M", "Tobilleras", "12500.00", 20, 6, True),
    ("TOB-002", "Tobillera con ajuste de velcro", "Tobilleras", "18900.00", 9, 4, True),
    ("TOB-003", "Tobillera estabilizadora rígida", "Tobilleras", "31500.00", 5, None, True),
    ("FAJ-001", "Faja lumbar elástica talle M", "Fajas", "26500.00", 10, 4, True),
    ("FAJ-002", "Faja lumbar con varillas talle L", "Fajas", "39800.00", 3, 4, True),
    ("FAJ-003", "Faja postural para espalda", "Fajas", "33900.00", 7, 3, True),
    ("PLA-001", "Plantillas ortopédicas de silicona", "Plantillas", "9800.00", 25, 8, True),
    ("PLA-002", "Plantillas para pie plano", "Plantillas", "15500.00", 14, 5, True),
    ("PLA-003", "Taloneras de gel", "Plantillas", "6900.00", 30, 10, True),
    ("OTR-001", "Cuello ortopédico blando", "Otros", "11900.00", 11, 4, True),
    ("OTR-002", "Cabestrillo para brazo", "Otros", "13400.00", 9, 3, True),
    ("OTR-003", "Almohadón antiescaras", "Otros", "42500.00", 4, 2, True),
    ("OTR-004", "Collar cervical rígido (discontinuado)", "Otros", "28700.00", 0, None, False),
    ("OTR-005", "Bolsa de gel frío/calor", "Otros", "8700.00", 16, 5, True),
]


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

    @app.cli.command("seed-categories")
    def seed_categories():
        """Carga las categorías iniciales (se puede correr más de una vez sin duplicar)."""
        created = 0
        for name in DEFAULT_CATEGORIES:
            if not Category.query.filter_by(name=name).first():
                db.session.add(Category(name=name))
                created += 1
        db.session.commit()
        click.echo(f"Categorías creadas: {created}. Ya existían: {len(DEFAULT_CATEGORIES) - created}.")

    @app.cli.command("seed-demo")
    def seed_demo():
        """Carga productos de ejemplo para probar (no duplica los que ya existen)."""
        categories = {c.name: c for c in Category.query.all()}
        if not categories:
            click.echo("Primero corré: flask seed-categories")
            return
        created = 0
        for code, name, category, price, stock, min_stock, is_active in DEMO_PRODUCTS:
            if Product.query.filter_by(code=code).first():
                continue
            db.session.add(
                Product(
                    code=code,
                    name=name,
                    category_id=categories[category].id,
                    price=Decimal(price),
                    stock=stock,
                    min_stock=min_stock,
                    is_active=is_active,
                )
            )
            created += 1
        db.session.commit()
        click.echo(f"Productos de ejemplo creados: {created}. Ya existían: {len(DEMO_PRODUCTS) - created}.")

    return app


app = create_app()
