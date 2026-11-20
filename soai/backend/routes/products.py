"""Endpoints de productos: listar, crear, editar y baja lógica."""
from flask import jsonify, request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import joinedload

from models import Product, db
from routes import api
from routes.helpers import error_response, get_product_or_404, serialize_product, validate_product_data

MAX_PER_PAGE = 100
DUPLICATE_CODE = "Ya existe un producto con ese código."


@api.get("/products")
def list_products():
    q = request.args.get("q", "").strip()
    category_id = request.args.get("category_id", type=int)
    stock = request.args.get("stock", "all")
    active = request.args.get("active", "1")
    page = max(request.args.get("page", 1, type=int), 1)
    per_page = min(max(request.args.get("per_page", 25, type=int), 1), MAX_PER_PAGE)

    if stock not in ("all", "low", "out"):
        return error_response("Filtro de stock inválido.", 400, {"stock": "Usá all, low u out."})
    if active not in ("1", "0", "all"):
        return error_response("Filtro de estado inválido.", 400, {"active": "Usá 1, 0 o all."})

    query = Product.query.options(joinedload(Product.category))
    if q:
        # autoescape: si escriben % o _ se buscan como texto común
        query = query.filter(
            or_(Product.code.contains(q, autoescape=True), Product.name.contains(q, autoescape=True))
        )
    if category_id:
        query = query.filter(Product.category_id == category_id)
    if active == "1":
        query = query.filter(Product.is_active.is_(True))
    elif active == "0":
        query = query.filter(Product.is_active.is_(False))
    if stock == "low":  # stock bajo: activo, con mínimo definido y stock <= mínimo
        query = query.filter(
            Product.is_active.is_(True), Product.min_stock.isnot(None), Product.stock <= Product.min_stock
        )
    elif stock == "out":
        query = query.filter(Product.is_active.is_(True), Product.stock == 0)

    result = query.order_by(Product.name, Product.id).paginate(
        page=page, per_page=per_page, error_out=False
    )
    return jsonify(
        {
            "items": [serialize_product(p) for p in result.items],
            "page": result.page,
            "per_page": per_page,
            "total": result.total,
            "pages": result.pages,
        }
    )


@api.post("/products")
def create_product():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("Los datos enviados no son válidos.", 400)

    clean, fields = validate_product_data(data, creating=True)
    if fields:
        return error_response("Revisá los datos ingresados.", 400, fields)

    # El código es único: si ya existe, 409 con el error en ese campo
    if Product.query.filter_by(code=clean["code"]).first() is not None:
        return error_response("Revisá los datos ingresados.", 409, {"code": DUPLICATE_CODE})

    product = Product(**clean)
    db.session.add(product)
    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        # Si dos personas guardan el mismo código a la vez, gana la primera
        if Product.query.filter_by(code=clean["code"]).first() is not None:
            return error_response("Revisá los datos ingresados.", 409, {"code": DUPLICATE_CODE})
        return error_response("No se pudo guardar el producto. Probá de nuevo.", 500)
    except SQLAlchemyError:
        db.session.rollback()
        return error_response("No se pudo guardar el producto. Probá de nuevo.", 500)
    return jsonify(serialize_product(product)), 201


@api.put("/products/<int:product_id>")
def update_product(product_id):
    product = get_product_or_404(product_id)
    if product is None:
        return error_response("No encontramos ese producto.", 404)

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return error_response("Los datos enviados no son válidos.", 400)

    # El código es la clave única y no se modifica después de creado
    if "code" in data and str(data["code"]).strip().upper() != product.code:
        return error_response(
            "Revisá los datos ingresados.", 400, {"code": "El código no se puede modificar."}
        )

    clean, fields = validate_product_data(data)
    if fields:
        return error_response("Revisá los datos ingresados.", 400, fields)

    for key, value in clean.items():
        setattr(product, key, value)
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return error_response("No se pudo guardar el producto. Probá de nuevo.", 500)
    return jsonify(serialize_product(product))


@api.post("/products/<int:product_id>/toggle-active")
def toggle_product_active(product_id):
    """Baja lógica: desactiva o reactiva. No borra nada."""
    product = get_product_or_404(product_id)
    if product is None:
        return error_response("No encontramos ese producto.", 404)

    product.is_active = not product.is_active
    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return error_response("No se pudo cambiar el estado del producto. Probá de nuevo.", 500)
    return jsonify(serialize_product(product))
