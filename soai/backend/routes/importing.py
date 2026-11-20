"""Importación desde Excel/CSV: plantilla, vista previa y confirmación."""
from flask import jsonify, request, send_file
from sqlalchemy.exc import SQLAlchemyError

from excel_import import ImportFileError, analyze_file, build_template
from models import Category, Product, db
from routes import api
from routes.helpers import error_response
from validation import normalize_key

PREVIEW_ROWS = 10  # filas que se muestran en la vista previa
MAX_ERRORS_SHOWN = 200  # errores que se devuelven (el total se informa aparte)
XLSX_MIMETYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@api.app_errorhandler(413)
def file_too_large(_error):
    """Archivo de más de 5 MB (MAX_CONTENT_LENGTH): respondemos con el mismo formato de error."""
    return error_response("El archivo es demasiado grande. El máximo es 5 MB.", 413)


def read_upload():
    """Lee y valida el archivo subido. Devuelve (análisis, None) o (None, respuesta_de_error)."""
    file = request.files.get("file")
    if file is None or not file.filename:
        return None, error_response("Elegí un archivo para subir.", 400)
    try:
        return analyze_file(file.filename, file.read()), None
    except ImportFileError as exc:
        return None, error_response(str(exc), 400)


def find_existing_products(rows):
    """Productos ya cargados cuyo código está en el archivo: {clave_del_código: producto}."""
    codes = [row["code"] for row in rows]
    if not codes:
        return {}
    products = Product.query.filter(Product.code.in_(codes)).all()
    return {normalize_key(p.code): p for p in products}


def load_categories():
    """Todas las categorías por nombre normalizado: {clave: categoría}."""
    return {normalize_key(c.name): c for c in Category.query.all()}


@api.get("/import/template")
def import_template():
    return send_file(
        build_template(),
        mimetype=XLSX_MIMETYPE,
        as_attachment=True,
        download_name="plantilla_productos.xlsx",
    )


@api.post("/import/preview")
def import_preview():
    """Analiza el archivo SIN guardar nada."""
    analysis, failure = read_upload()
    if failure:
        return failure
    rows, errors = analysis["rows"], analysis["errors"]

    existing = find_existing_products(rows)
    categories = load_categories()

    new_categories, seen = [], set()
    for row in rows:
        key = normalize_key(row["category"])
        if key not in categories and key not in seen:
            seen.add(key)
            new_categories.append(row["category"])

    existing_count = sum(1 for row in rows if normalize_key(row["code"]) in existing)
    preview = [
        {
            "row": row["row"],
            "code": row["code"],
            "name": row["name"],
            "category": row["category"],
            "price": str(row["price"]),
            "stock": row["stock"],
            "min_stock": row["min_stock"],
            "exists": normalize_key(row["code"]) in existing,
        }
        for row in rows[:PREVIEW_ROWS]
    ]
    return jsonify(
        {
            "total_rows": analysis["total_rows"],
            "new_count": len(rows) - existing_count,
            "existing_count": existing_count,
            "error_rows": len({e["row"] for e in errors}),
            "errors_total": len(errors),
            "errors": errors[:MAX_ERRORS_SHOWN],
            "new_categories": new_categories,
            "preview": preview,
        }
    )


@api.post("/import/confirm")
def import_confirm():
    """Vuelve a validar el archivo y guarda todo en UNA transacción (todo o nada)."""
    mode = request.form.get("mode", "skip")
    if mode not in ("skip", "update"):
        return error_response("Opción inválida para los códigos que ya existen.", 400, {"mode": "Usá skip o update."})

    analysis, failure = read_upload()
    if failure:
        return failure
    if analysis["errors"]:
        return error_response("El archivo tiene errores. Corregilo y volvé a subirlo.", 400)

    rows = analysis["rows"]
    existing = find_existing_products(rows)
    categories = load_categories()
    created = updated = skipped = categories_created = 0

    try:
        for row in rows:
            product = existing.get(normalize_key(row["code"]))
            if product is not None:
                if mode == "update":
                    # Solo precio, stock y mínimo; una celda vacía no pisa el valor actual
                    product.price = row["price"]
                    if row["stock"] is not None:
                        product.stock = row["stock"]
                    if row["min_stock"] is not None:
                        product.min_stock = row["min_stock"]
                    updated += 1
                else:
                    skipped += 1
                continue

            key = normalize_key(row["category"])
            category = categories.get(key)
            if category is None:  # categoría nueva: se crea automáticamente
                category = Category(name=row["category"])
                db.session.add(category)
                categories[key] = category
                categories_created += 1
            db.session.add(
                Product(
                    code=row["code"],
                    name=row["name"],
                    category=category,
                    price=row["price"],
                    stock=row["stock"] if row["stock"] is not None else 0,
                    min_stock=row["min_stock"],
                    description=row["description"],
                )
            )
            created += 1
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return error_response("No se pudo importar el archivo. No se guardó nada. Probá de nuevo.", 500)

    return jsonify(
        {"created": created, "updated": updated, "skipped": skipped, "categories_created": categories_created}
    )
