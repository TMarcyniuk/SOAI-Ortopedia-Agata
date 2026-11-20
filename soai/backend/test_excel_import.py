"""Tests de la lectura y validación del Excel/CSV (lo más fácil de romper). Se corren con: pytest"""
import io
from decimal import Decimal

import pytest
from openpyxl import Workbook

from excel_import import MAX_ROWS, ImportFileError, analyze_file, build_template

HEADER = ["codigo", "nombre", "categoria", "precio", "stock", "stock_minimo", "descripcion"]


def make_xlsx(rows):
    """Arma un .xlsx en memoria con las filas dadas (la primera es el encabezado)."""
    workbook = Workbook()
    sheet = workbook.active
    for row in rows:
        sheet.append(row)
    output = io.BytesIO()
    workbook.save(output)
    return output.getvalue()


def errors_of(result, field=None):
    return [e for e in result["errors"] if field is None or e["field"] == field]


def test_encabezados_con_tildes_y_mayusculas():
    data = make_xlsx(
        [
            ["Código", "NOMBRE", "Categoría", "Precio", "Stock", "Stock Mínimo", "Descripción"],
            ["bas-001", "Bastón", "Bastones", 14500, 10, 3, "Liviano"],
        ]
    )
    result = analyze_file("productos.xlsx", data)
    assert result["errors"] == []
    row = result["rows"][0]
    assert row["code"] == "BAS-001"  # se limpia y pasa a mayúsculas
    assert (row["stock"], row["min_stock"], row["description"]) == (10, 3, "Liviano")


@pytest.mark.parametrize(
    "price", ["1.234,56", "1234.56", "$ 1.234,56", 1234.56, Decimal("1234.56")]
)
def test_precio_en_distintos_formatos(price):
    data = make_xlsx([HEADER, ["A-1", "Producto", "Otros", price, None, None, None]])
    result = analyze_file("p.xlsx", data)
    assert result["errors"] == []
    assert result["rows"][0]["price"] == Decimal("1234.56")


def test_precio_con_miles_sin_decimales():
    data = make_xlsx([HEADER, ["A-1", "Producto", "Otros", "1.234", None, None, None]])
    assert analyze_file("p.xlsx", data)["rows"][0]["price"] == Decimal("1234.00")


def test_numero_con_tres_decimales_no_se_confunde_con_miles():
    # Una celda numérica 1.234 es un precio con 3 decimales, no "mil doscientos treinta y cuatro"
    data = make_xlsx([HEADER, ["A-1", "Producto", "Otros", 1.234, None, None, None]])
    result = analyze_file("p.xlsx", data)
    assert result["rows"] == []
    assert errors_of(result, "precio")[0]["message"] == "El precio puede tener hasta 2 decimales."


@pytest.mark.parametrize("price", ["abc", "-5", "10,999", "1e30", "99999999999999"])
def test_precio_invalido(price):
    data = make_xlsx([HEADER, ["A-1", "Producto", "Otros", price, None, None, None]])
    result = analyze_file("p.xlsx", data)
    assert result["rows"] == []
    assert len(errors_of(result, "precio")) == 1


def test_codigo_repetido_dentro_del_archivo():
    data = make_xlsx(
        [
            HEADER,
            ["A-1", "Uno", "Otros", 10, None, None, None],
            ["a-1 ", "Dos", "Otros", 20, None, None, None],  # mismo código con otro formato
        ]
    )
    result = analyze_file("p.xlsx", data)
    assert len(result["rows"]) == 1
    error = errors_of(result, "codigo")[0]
    assert error["row"] == 3
    assert "fila 2" in error["message"]


@pytest.mark.parametrize("stock", [-3, "-3", "2,5", "abc", 2.5])
def test_stock_negativo_o_no_entero(stock):
    data = make_xlsx([HEADER, ["A-1", "Producto", "Otros", 10, stock, None, None]])
    result = analyze_file("p.xlsx", data)
    assert result["rows"] == []
    assert len(errors_of(result, "stock")) == 1


def test_stock_entero_escrito_como_decimal_de_excel():
    data = make_xlsx([HEADER, ["A-1", "Producto", "Otros", 10, 12.0, 4.0, None]])
    row = analyze_file("p.xlsx", data)["rows"][0]
    assert (row["stock"], row["min_stock"]) == (12, 4)


def test_stock_y_minimo_vacios_quedan_en_none():
    data = make_xlsx([HEADER, ["A-1", "Producto", "Otros", 10, None, None, None]])
    row = analyze_file("p.xlsx", data)["rows"][0]
    assert row["stock"] is None and row["min_stock"] is None and row["description"] is None


def test_filas_vacias_se_saltean_y_mantienen_el_numero_de_fila():
    data = make_xlsx(
        [
            HEADER,
            ["A-1", "Uno", "Otros", 10, None, None, None],
            [None] * 7,
            ["   ", None, "", None, None, None, None],
            ["A-2", "", "Otros", 20, None, None, None],  # el error está en la fila 5 de la planilla
        ]
    )
    result = analyze_file("p.xlsx", data)
    assert result["total_rows"] == 2
    assert [e["row"] for e in result["errors"]] == [5]
    assert errors_of(result)[0]["field"] == "nombre"


def test_campos_obligatorios_vacios():
    data = make_xlsx([HEADER, [None, "Producto", "Otros", 10, None, None, None], ["A-1", "Producto", None, None, None, None, None]])
    result = analyze_file("p.xlsx", data)
    assert result["rows"] == []
    assert {(e["row"], e["field"]) for e in result["errors"]} == {(2, "codigo"), (3, "categoria"), (3, "precio")}


def test_codigo_numerico_de_excel():
    data = make_xlsx([HEADER, [1001.0, "Producto", "Otros", 10, None, None, None]])
    assert analyze_file("p.xlsx", data)["rows"][0]["code"] == "1001"


def test_archivo_sin_columnas_obligatorias():
    data = make_xlsx([["codigo", "nombre", "stock"], ["A-1", "Producto", 3]])
    with pytest.raises(ImportFileError) as info:
        analyze_file("p.xlsx", data)
    assert "categoria" in str(info.value) and "precio" in str(info.value)


def test_archivo_vacio_o_solo_encabezados():
    with pytest.raises(ImportFileError):
        analyze_file("p.xlsx", make_xlsx([]))
    with pytest.raises(ImportFileError):
        analyze_file("p.xlsx", make_xlsx([HEADER]))


def test_formato_no_soportado_o_archivo_roto():
    with pytest.raises(ImportFileError):
        analyze_file("productos.xls", b"cualquier cosa")
    with pytest.raises(ImportFileError):
        analyze_file("productos.xlsx", b"esto no es un excel")


def test_csv_de_excel_argentino_con_punto_y_coma_y_windows_1252():
    text = "Código;Nombre;Categoría;Precio;Stock\nbas-001;Bastón;Bastones;1.234,56;7\n"
    result = analyze_file("p.csv", text.encode("cp1252"))
    assert result["errors"] == []
    row = result["rows"][0]
    assert (row["name"], row["category"], row["price"], row["stock"]) == ("Bastón", "Bastones", Decimal("1234.56"), 7)


def test_csv_utf8_con_bom_y_comas():
    text = 'codigo,nombre,categoria,precio\nA-1,"Faja, lumbar",Fajas,"1234.5"\n'
    result = analyze_file("p.csv", text.encode("utf-8-sig"))
    assert result["errors"] == []
    assert result["rows"][0]["name"] == "Faja, lumbar"
    assert result["rows"][0]["price"] == Decimal("1234.50")


def test_demasiadas_filas():
    lines = ["codigo,nombre,categoria,precio"] + [f"C-{i},P,Otros,1" for i in range(MAX_ROWS + 1)]
    with pytest.raises(ImportFileError):
        analyze_file("p.csv", "\n".join(lines).encode())
    ok = lines[:-1]  # justo 5000 filas: se acepta
    assert len(analyze_file("p.csv", "\n".join(ok).encode())["rows"]) == MAX_ROWS


def test_la_plantilla_se_puede_importar():
    result = analyze_file("plantilla_productos.xlsx", build_template().getvalue())
    assert result["errors"] == []
    assert [r["code"] for r in result["rows"]] == ["EJEMPLO-1", "EJEMPLO-2"]
