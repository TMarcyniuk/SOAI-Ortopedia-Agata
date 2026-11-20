"""Endpoints de categorías: listar y crear."""
from flask import jsonify, request
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from models import Category, Product, db
from routes import api
from routes.helpers import error_response
from validation import normalize_key, parse_category_name


@api.get("/categories")
def list_categories():
    """Categorías activas, cada una con su cantidad de productos (activos e inactivos)."""
    rows = (
        db.session.query(Category, func.count(Product.id))
        .outerjoin(Product, Product.category_id == Category.id)
        .filter(Category.is_active.is_(True))
        .group_by(Category.id)
        .order_by(Category.id)
        .all()
    )
    return jsonify([{"id": c.id, "name": c.name, "product_count": count} for c, count in rows])


@api.post("/categories")
def create_category():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("Los datos enviados no son válidos.", 400)

    name, error = parse_category_name(data.get("name"))
    if error:
        return error_response("Revisá los datos ingresados.", 400, {"name": error})

    # Se compara sin importar mayúsculas, tildes ni espacios (como lo hace MySQL con su colación).
    # También cuentan las categorías desactivadas: no se reactivan solas.
    key = normalize_key(name)
    for existing in Category.query.all():
        if normalize_key(existing.name) == key:
            message = "Ya existe una categoría con ese nombre."
            if not existing.is_active:
                message = "Ya existe una categoría con ese nombre, pero está desactivada."
            return error_response("Revisá los datos ingresados.", 409, {"name": message})

    category = Category(name=name)
    db.session.add(category)
    try:
        db.session.commit()
    except IntegrityError:  # otra persona la creó justo en este momento
        db.session.rollback()
        return error_response(
            "Revisá los datos ingresados.", 409, {"name": "Ya existe una categoría con ese nombre."}
        )
    except SQLAlchemyError:
        db.session.rollback()
        return error_response("No se pudo crear la categoría. Probá de nuevo.", 500)
    return jsonify({"id": category.id, "name": category.name}), 201


@api.delete("/categories/<int:category_id>")
def delete_category(category_id):
    """Elimina una categoría, solo si no tiene productos (ni siquiera inactivos)."""
    category = db.session.get(Category, category_id)
    if category is None:
        return error_response("No encontramos esa categoría.", 404)

    count = Product.query.filter_by(category_id=category.id).count()
    if count > 0:
        noun = "1 producto asociado" if count == 1 else f"{count} productos asociados"
        return error_response(
            f'No se puede eliminar "{category.name}": tiene {noun}. Pasalos a otra categoría primero.', 409
        )

    db.session.delete(category)
    try:
        db.session.commit()
    except IntegrityError:  # alguien le asignó un producto justo en este momento
        db.session.rollback()
        return error_response(f'No se puede eliminar "{category.name}": tiene productos asociados.', 409)
    except SQLAlchemyError:
        db.session.rollback()
        return error_response("No se pudo eliminar la categoría. Probá de nuevo.", 500)
    return jsonify({"id": category_id})
