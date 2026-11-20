"""Lee y valida un archivo Excel (.xlsx) o CSV con productos. No toca la base de datos."""
import csv
import io

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font

from validation import (
    is_blank,
    normalize_key,
    parse_category_name,
    parse_code,
    parse_int,
    parse_name,
    parse_price,
)

MAX_ROWS = 5000
REQUIRED_COLUMNS = ["codigo", "nombre", "categoria", "precio"]
OPTIONAL_COLUMNS = ["stock", "stock_minimo", "descripcion"]
COLUMNS = REQUIRED_COLUMNS + OPTIONAL_COLUMNS


class ImportFileError(Exception):
    """Problema con el archivo en sí (formato, columnas, tamaño). El mensaje se muestra tal cual."""


# ---------- Lectura ----------
def read_xlsx(data):
    """Devuelve [(número_de_fila, celdas)] de la primera hoja, sin las filas vacías."""
    try:
        workbook = load_workbook(io.BytesIO(data), read_only=True, data_only=True)
    except Exception:
        raise ImportFileError("No se pudo leer el archivo. Verificá que sea un Excel (.xlsx) válido.")
    try:
        sheet = workbook.worksheets[0]
        sheet.reset_dimensions()  # algunos programas guardan mal el tamaño de la hoja
        return [
            (number, list(cells))
            for number, cells in enumerate(sheet.iter_rows(values_only=True), start=1)
            if any(not is_blank(c) for c in cells)
        ]
    except Exception:
        raise ImportFileError("No se pudo leer el archivo. Verificá que sea un Excel (.xlsx) válido.")
    finally:
        workbook.close()


def read_csv(data):
    """Igual que read_xlsx pero para CSV. Acepta , o ; y UTF-8 o Windows-1252."""
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise ImportFileError("No se pudo leer el archivo. Guardalo como CSV UTF-8 desde Excel.")

    # Excel en Argentina separa con ";" y otros programas con ","
    first_line = next((line for line in text.splitlines() if line.strip()), "")
    delimiter = ";" if first_line.count(";") > first_line.count(",") else ","
    try:
        reader = csv.reader(io.StringIO(text, newline=""), delimiter=delimiter)
        return [
            (number, cells)
            for number, cells in enumerate(reader, start=1)
            if any(not is_blank(c) for c in cells)
        ]
    except csv.Error:
        raise ImportFileError("No se pudo leer el archivo. Verificá que sea un CSV válido.")


def header_key(cell):
    """'Stock Mínimo' -> 'stock_minimo' (sin mayúsculas, tildes ni espacios)."""
    if cell is None:
        return ""
    return normalize_key(cell).replace(" ", "_").replace("-", "_")


def map_header(cells):
    """Devuelve {columna: posición}. Las columnas que no conocemos se ignoran."""
    mapping = {}
    for position, cell in enumerate(cells):
        name = header_key(cell)
        if name in COLUMNS:
            if name in mapping:
                raise ImportFileError(f'La columna "{name}" está repetida.')
            mapping[name] = position
    missing = [name for name in REQUIRED_COLUMNS if name not in mapping]
    if missing:
        raise ImportFileError(
            "Faltan columnas obligatorias: " + ", ".join(missing) + ". Descargá la plantilla para ver el formato."
        )
    return mapping


def cell_at(cells, position):
    return cells[position] if position is not None and position < len(cells) else None


def cell_text(value):
    """Texto de una celda. Un código numérico como 1001.0 se muestra como 1001."""
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


# ---------- Validación ----------
def validate_row(number, cells, seen_codes):
    """Valida una fila. Devuelve (fila_limpia, errores); si hay errores, fila_limpia es None.

    `cells` es {columna: valor}. `seen_codes` guarda los códigos ya vistos en el archivo.
    """
    errors = []

    def fail(field, message):
        errors.append({"row": number, "field": field, "message": message})

    code = name = category = price = None
    stock = min_stock = None

    if is_blank(cells["codigo"]):
        fail("codigo", "Falta el código.")
    else:
        code, error = parse_code(cell_text(cells["codigo"]))
        if error:
            fail("codigo", error)
        else:
            key = normalize_key(code)
            if key in seen_codes:
                fail("codigo", f"El código ya aparece en la fila {seen_codes[key]}.")
            else:
                seen_codes[key] = number

    if is_blank(cells["nombre"]):
        fail("nombre", "Falta el nombre.")
    else:
        name, error = parse_name(cell_text(cells["nombre"]))
        if error:
            fail("nombre", error)

    if is_blank(cells["categoria"]):
        fail("categoria", "Falta la categoría.")
    else:
        category, error = parse_category_name(cell_text(cells["categoria"]))
        if error:
            fail("categoria", error)

    if is_blank(cells["precio"]):
        fail("precio", "Falta el precio.")
    else:
        price, error = parse_price(cells["precio"])
        if error:
            fail("precio", error)

    # Stock y mínimo vacíos quedan en None: al crear valen 0 y sin mínimo,
    # y al actualizar no pisan el valor que ya tiene el producto.
    if not is_blank(cells["stock"]):
        stock, error = parse_int(cells["stock"], "El stock")
        if error:
            fail("stock", error)
    if not is_blank(cells["stock_minimo"]):
        min_stock, error = parse_int(cells["stock_minimo"], "El stock mínimo")
        if error:
            fail("stock_minimo", error)

    if errors:
        return None, errors
    row = {
        "row": number,
        "code": code,
        "name": name,
        "category": category,
        "price": price,
        "stock": stock,
        "min_stock": min_stock,
        "description": cell_text(cells["descripcion"]) or None,
    }
    return row, []


def analyze_file(filename, data):
    """Lee y valida el archivo completo, sin guardar nada.

    Devuelve {"rows": filas válidas, "errors": errores, "total_rows": filas con datos}.
    Si el archivo no se puede usar, lanza ImportFileError.
    """
    name = (filename or "").lower()
    if name.endswith(".xlsx"):
        rows = read_xlsx(data)
    elif name.endswith(".csv"):
        rows = read_csv(data)
    else:
        raise ImportFileError("Formato no soportado. Subí un archivo .xlsx o .csv.")

    if not rows:
        raise ImportFileError("El archivo está vacío.")
    mapping = map_header(rows[0][1])
    data_rows = rows[1:]
    if not data_rows:
        raise ImportFileError("El archivo no tiene filas con datos debajo de los encabezados.")
    if len(data_rows) > MAX_ROWS:
        raise ImportFileError(f"El archivo tiene más de {MAX_ROWS} filas. Dividilo en partes más chicas.")

    valid_rows, errors, seen_codes = [], [], {}
    for number, cells in data_rows:
        values = {column: cell_at(cells, mapping.get(column)) for column in COLUMNS}
        row, row_errors = validate_row(number, values, seen_codes)
        if row is not None:
            valid_rows.append(row)
        errors.extend(row_errors)
    return {"rows": valid_rows, "errors": errors, "total_rows": len(data_rows)}


# ---------- Plantilla ----------
def build_template():
    """Excel de ejemplo con las columnas y 2 filas de muestra. Devuelve un BytesIO."""
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Productos"
    sheet.append(COLUMNS)
    sheet.append(["EJEMPLO-1", "Bastón de aluminio regulable", "Bastones", 14500.5, 10, 3, "Descripción opcional"])
    sheet.append(["EJEMPLO-2", "Rodillera elástica talle M", "Rodilleras", 19800, 15, None, None])
    for cell in sheet[1]:
        cell.font = Font(bold=True)
    for letter, width in zip("ABCDEFG", (16, 40, 20, 14, 10, 14, 36)):
        sheet.column_dimensions[letter].width = width
    for cell in sheet["D"][1:]:
        cell.number_format = "#,##0.00"
    sheet.freeze_panes = "A2"

    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)
    return output
