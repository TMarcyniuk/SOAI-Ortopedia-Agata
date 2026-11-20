"""Validaciones sin base de datos. Las usan el alta manual, la edición y la importación."""
import re
import unicodedata
from decimal import Decimal, InvalidOperation

MAX_PRICE = Decimal("9999999999.99")  # tope de DECIMAL(12,2)
MAX_INT = 2_147_483_647  # tope de INT en MySQL
MAX_CODE = 50
MAX_NAME = 200
MAX_CATEGORY = 80


def is_blank(value):
    return value is None or str(value).strip() == ""


def normalize_key(text):
    """Clave para comparar textos sin importar mayúsculas, tildes ni espacios sobrantes."""
    text = " ".join(str(text).split()).casefold()
    return "".join(c for c in unicodedata.normalize("NFKD", text) if not unicodedata.combining(c))


def parse_price(value):
    """Acepta '1.234,56', '1234.56' y números. Devuelve (Decimal, None) o (None, mensaje)."""
    if value is None or isinstance(value, bool):
        return None, "Ingresá el precio."
    if isinstance(value, (int, float, Decimal)):
        # Un número ya es un número: no hay que interpretar puntos ni comas
        try:
            price = Decimal(str(value))
        except InvalidOperation:
            return None, "El precio no es un número válido."
    else:
        s = str(value).strip().replace(" ", "").lstrip("$")
        if not s:
            return None, "Ingresá el precio."
        if "," in s:  # formato argentino: el punto separa miles y la coma los decimales
            s = s.replace(".", "").replace(",", ".")
        elif re.fullmatch(r"-?\d{1,3}(\.\d{3})+", s):  # "1.234" significa mil doscientos treinta y cuatro
            s = s.replace(".", "")
        if not re.fullmatch(r"-?\d+(\.\d+)?", s):
            return None, "El precio no es un número válido."
        price = Decimal(s)
    if not price.is_finite():
        return None, "El precio no es un número válido."
    if price < 0:
        return None, "El precio no puede ser negativo."
    if price > MAX_PRICE:  # antes de redondear: así un número enorme no rompe la cuenta
        return None, "El precio es demasiado alto."
    if price != price.quantize(Decimal("0.01")):
        return None, "El precio puede tener hasta 2 decimales."
    return price.quantize(Decimal("0.01")), None


def parse_int(value, label):
    """Entero mayor o igual a 0. Devuelve (int, None) o (None, mensaje)."""
    if isinstance(value, bool):
        return None, f"{label} debe ser un número entero."
    if isinstance(value, float):
        # Los números de Excel pueden llegar como 12.0
        if not value.is_integer():
            return None, f"{label} debe ser un número entero."
        value = int(value)
    text_value = str(value).strip()
    if not re.fullmatch(r"-?\d+", text_value):
        return None, f"{label} debe ser un número entero."
    number = int(text_value)
    if number < 0:
        return None, f"{label} no puede ser negativo."
    if number > MAX_INT:
        return None, f"{label} es demasiado alto."
    return number, None


def parse_code(value):
    """Código: se limpia (trim) y se pasa a mayúsculas. Devuelve (código, None) o (None, mensaje)."""
    code = "" if value is None else str(value).strip().upper()
    if not code:
        return None, "Ingresá el código."
    if len(code) > MAX_CODE:
        return None, f"El código puede tener hasta {MAX_CODE} caracteres."
    return code, None


def parse_name(value):
    name = "" if value is None else str(value).strip()
    if not name:
        return None, "Ingresá el nombre."
    if len(name) > MAX_NAME:
        return None, f"El nombre puede tener hasta {MAX_NAME} caracteres."
    return name, None


def parse_category_name(value):
    """Nombre de categoría: sin espacios de más. Devuelve (nombre, None) o (None, mensaje)."""
    name = "" if value is None else " ".join(str(value).split())
    if not name:
        return None, "Ingresá el nombre de la categoría."
    if len(name) > MAX_CATEGORY:
        return None, f"El nombre de la categoría puede tener hasta {MAX_CATEGORY} caracteres."
    return name, None
