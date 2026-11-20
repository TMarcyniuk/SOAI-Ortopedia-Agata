"""Endpoints de la API: health, categorías y productos."""
import re
from decimal import Decimal

from flask import Blueprint, jsonify, request
from sqlalchemy import or_, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from models import Category, Product, db

api = Blueprint("api", __name__, url_prefix="/api")

MAX_PER_PAGE = 100
MAX_PRICE = Decimal("9999999999.99")  # tope de DECIMAL(12,2)
MAX_INT = 2_147_483_647  # tope de INT en MySQL


# ---------- Ayudas ----------
def error_response(message, status, fields=None):
    """Formato único de error: {"error": "...", "fields": {"campo": "detalle"}}"""
    return jsonify({"error": message, "fields": fields or {}}), status


def parse_price(value):
    """Acepta '1.234,56' y '1234.56'. Devuelve (Decimal, None) o (None, mensaje)."""
    s = "" if value is None or isinstance(value, bool) else str(value).strip().replace(" ", "")
    s = s.lstrip("$")
    if not s:
        return None, "Ingresá el precio."
    if "," in s:  # formato argentino: el punto separa miles y la coma los decimales
        s = s.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):  # "1.234" significa mil doscientos treinta y cuatro
        s = s.replace(".", "")
    if not re.fullmatch(r"-?\d+(\.\d+)?", s):
        return None, "El precio no es un número válido."
    price = Decimal(s)
    if price < 0:
        return None, "El precio no puede ser negativo."
    if price != price.quantize(Decimal("0.01")):
        return None, "El precio puede tener hasta 2 decimales."
    if price > MAX_PRICE:
        return None, "El precio es demasiado alto."
    return price.quantize(Decimal("0.01")), None


def parse_int(value, label):
    """Entero mayor o igual a 0. Devuelve (int, None) o (None, mensaje)."""
    if isinstance(value, bool):
        return None, f"{label} debe ser un número entero."
    text_value = str(value).strip()
    if not re.fullmatch(r"-?\d+", text_value):
        return None, f"{label} debe ser un número entero."
    number = int(text_value)
    if number < 0:
        return None, f"{label} no puede ser negativo."
    if number > MAX_INT:
        return None, f"{label} es demasiado alto."
    return number, None


def is_blank(value):
    return value is None or str(value).strip() == ""


def validate_product_data(data):
    """Valida los datos editables de un producto. Devuelve (datos_limpios, errores_por_campo)."""
    clean, fields = {}, {}

    name = str(data.get("name") or "").strip()
    if not name:
        fields["name"] = "Ingresá el nombre."
    elif len(name) > 200:
        fields["name"] = "El nombre puede tener hasta 200 caracteres."
    else:
        clean["name"] = name

    try:
        category = db.session.get(Category, int(data.get("category_id")))
    except (TypeError, ValueError):
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


# ---------- Endpoints ----------
@api.get("/health")
def health():
    """Chequea que el servidor y la base de datos respondan."""
    try:
        db.session.execute(text("SELECT 1"))
    except Exception:
        return jsonify({"error": "No se pudo conectar con la base de datos."}), 503
    return jsonify({"status": "ok", "database": "ok"})


@api.get("/categories")
def list_categories():
    categories = Category.query.filter_by(is_active=True).order_by(Category.id).all()
    return jsonify([{"id": c.id, "name": c.name} for c in categories])


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
