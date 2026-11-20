"""Ayudas que comparten los endpoints."""
from flask import jsonify

from models import Category, Product, db
from validation import MAX_INT, is_blank, parse_code, parse_int, parse_name, parse_price


def error_response(message, status, fields=None):
    """Formato único de error: {"error": "...", "fields": {"campo": "detalle"}}"""
    return jsonify({"error": message, "fields": fields or {}}), status


def validate_product_data(data, creating=False):
    """Valida los datos de un producto. Devuelve (datos_limpios, errores_por_campo).

    Con creating=True también valida el código (que no se puede editar después)
    y un stock vacío vale 0.
    """
    clean, fields = {}, {}

    if creating:
        code, error = parse_code(data.get("code"))
        if error:
            fields["code"] = error
        else:
            clean["code"] = code

    name, error = parse_name(data.get("name"))
    if error:
        fields["name"] = error
    else:
        clean["name"] = name

    try:
        category_id = int(data.get("category_id"))
        category = db.session.get(Category, category_id) if 0 < category_id <= MAX_INT else None
    except (TypeError, ValueError, OverflowError):
        category = None
    if category is None:
        fields["category_id"] = "Elegí una categoría."
    else:
        clean["category_id"] = category.id

    price, error = parse_price(data.get("price"))
    if error:
        fields["price"] = error
    else:
        clean["price"] = price

    if is_blank(data.get("stock")):
        if creating:
            clean["stock"] = 0
        else:
            fields["stock"] = "Ingresá el stock."
    else:
        stock, error = parse_int(data.get("stock"), "El stock")
        if error:
            fields["stock"] = error
        else:
            clean["stock"] = stock

    if is_blank(data.get("min_stock")):
        clean["min_stock"] = None  # opcional: sin mínimo no se evalúa el stock bajo
    else:
        min_stock, error = parse_int(data.get("min_stock"), "El stock mínimo")
        if error:
            fields["min_stock"] = error
        else:
            clean["min_stock"] = min_stock

    clean["description"] = str(data.get("description") or "").strip() or None
    return clean, fields


def product_status(product):
    """normal | low | out | inactive"""
    if not product.is_active:
        return "inactive"
    if product.stock == 0:
        return "out"
    if product.min_stock is not None and product.stock <= product.min_stock:
        return "low"
    return "normal"


def serialize_product(product):
    return {
        "id": product.id,
        "code": product.code,
        "name": product.name,
        "category_id": product.category_id,
        "category_name": product.category.name,
        "description": product.description,
        "price": str(product.price),  # texto, para no perder decimales
        "stock": product.stock,
        "min_stock": product.min_stock,
        "is_active": product.is_active,
        "status": product_status(product),
    }


def get_product_or_404(product_id):
    return db.session.get(Product, product_id)
