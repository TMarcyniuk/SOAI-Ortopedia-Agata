import { useRef, useState } from "react";
import { Link } from "react-router-dom";

import { IMPORT_TEMPLATE_URL, confirmImport, previewImport } from "../api.js";
import { integer, money } from "../format.js";
import { ErrorMessage } from "./ProductForm.jsx";

const MAX_FILE_BYTES = 5 * 1024 * 1024; // el backend también lo controla

// "Se crearon 3 productos, se actualizó 1, se omitieron 0." (con singular y plural)
function resultText({ created, updated, skipped, categories_created }) {
  const parts = [
    created === 1 ? "Se creó 1 producto" : `Se crearon ${integer.format(created)} productos`,
    updated === 1 ? "se actualizó 1" : `se actualizaron ${integer.format(updated)}`,
    skipped === 1 ? "se omitió 1" : `se omitieron ${integer.format(skipped)}`,
  ];
  let text = `${parts.join(", ")}.`;
  if (categories_created > 0) {
    text += categories_created === 1 ? " También se creó 1 categoría nueva." : ` También se crearon ${categories_created} categorías nuevas.`;
  }
  return text;
}

function Stat({ label, value, danger = false }) {
  return (
    <div className={danger ? "stat stat-danger" : "stat"}>
      <dt>{label}</dt>
      <dd>{integer.format(value)}</dd>
    </div>
  );
}

function ErrorsTable({ errors, total }) {
  return (
    <>
      <h2 className="section-title">Errores para corregir</h2>
      <p className="muted">El número de fila es el de la planilla (la fila 1 son los encabezados).</p>
      <div className="table-wrap">
        <table>
          <caption className="sr-only">Errores encontrados en el archivo</caption>
          <thead>
            <tr>
              <th>Fila</th>
              <th>Columna</th>
              <th>Motivo</th>
            </tr>
          </thead>
          <tbody>
            {errors.map((e, index) => (
              <tr key={`${e.row}-${e.field}-${index}`}>
                <td>{e.row}</td>
                <td>{e.field}</td>
                <td>{e.message}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {total > errors.length && (
        <p className="muted">Se muestran los primeros {errors.length} de {integer.format(total)} errores.</p>
      )}
    </>
  );
}

function PreviewTable({ items }) {
  return (
    <>
      <h2 className="section-title">Primeras filas del archivo</h2>
      <div className="table-wrap">
        <table>
          <caption className="sr-only">Vista previa de los productos del archivo</caption>
          <thead>
            <tr>
              <th>Fila</th>
              <th>Código</th>
              <th>Nombre</th>
              <th>Categoría</th>
              <th className="num">Precio</th>
              <th className="num">Stock</th>
              <th className="num">Mínimo</th>
              <th>Estado</th>
            </tr>
          </thead>
          <tbody>
            {items.map((p) => (
              <tr key={p.row}>
                <td>{p.row}</td>
                <td>{p.code}</td>
                <td>{p.name}</td>
                <td>{p.category}</td>
                <td className="num">{money.format(Number(p.price))}</td>
                <td className="num">{p.stock === null ? "—" : integer.format(p.stock)}</td>
                <td className="num">{p.min_stock === null ? "—" : integer.format(p.min_stock)}</td>
                <td>
                  <span className={p.exists ? "badge badge-muted" : "badge badge-ok"}>{p.exists ? "Ya existe" : "Nuevo"}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </>
  );
}

// Pestaña "Desde Excel": 1) se sube el archivo y se ve una vista previa sin guardar nada, 2) se confirma.
export default function ImportTab() {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [mode, setMode] = useState("skip"); // skip = omitir, update = actualizar
  const [analyzing, setAnalyzing] = useState(false);
  const [importing, setImporting] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);
  const lastRequest = useRef(0); // evita que la respuesta de un archivo viejo pise a la del nuevo

  async function handleFile(event) {
    const chosen = event.target.files[0];
    event.target.value = ""; // así se puede volver a elegir el mismo archivo después de corregirlo
    if (!chosen) return;

    setFile(chosen);
    setPreview(null);
    setResult(null);
    setError("");
    setMode("skip");
    if (chosen.size > MAX_FILE_BYTES) {
      setError("El archivo es demasiado grande. El máximo es 5 MB.");
      return;
    }

    const id = ++lastRequest.current;
    setAnalyzing(true);
    try {
      const data = await previewImport(chosen);
      if (id === lastRequest.current) setPreview(data);
    } catch (err) {
      if (id === lastRequest.current) setError(err.message);
    } finally {
      if (id === lastRequest.current) setAnalyzing(false);
    }
  }

  async function handleImport() {
    setImporting(true);
    setError("");
    try {
      const data = await confirmImport(file, mode);
      setResult(data);
      setPreview(null);
      setFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setImporting(false);
    }
  }

  const hasErrors = preview && preview.error_rows > 0;
  // Con "Omitir" solo hay algo para guardar si hay filas nuevas
  const nothingToDo = preview && mode === "skip" && preview.new_count === 0;
  const canImport = preview && !hasErrors && !nothingToDo;

  return (
    <div>
      <div className="import-intro">
        <p>
          Cargá muchos productos de una vez. Descargá la plantilla, completala (borrá las filas de ejemplo) y subila.
          Antes de guardar nada vas a ver una vista previa.
        </p>
        <p className="muted">
          Columnas obligatorias: <strong>codigo</strong>, <strong>nombre</strong>, <strong>categoria</strong> y{" "}
          <strong>precio</strong>. Opcionales: stock, stock_minimo y descripcion. Se lee la primera hoja. Aceptamos .xlsx y
          .csv, hasta 5 MB y 5000 filas. Las categorías que no existan se crean solas.
        </p>
      </div>

      <div className="import-actions">
        <a className="btn btn-secondary" href={IMPORT_TEMPLATE_URL}>Descargar plantilla</a>
        <label className="btn btn-primary file-picker">
          Elegir archivo
          <input type="file" className="sr-only" accept=".xlsx,.csv" onChange={handleFile} />
        </label>
        {file && <span className="file-name">{file.name}</span>}
      </div>

      {analyzing && <p className="muted" role="status">Analizando el archivo…</p>}
      {error && <ErrorMessage banner>{error}</ErrorMessage>}
      {result && (
        <p className="notice" role="status">
          {resultText(result)} <Link to="/products">Ver productos</Link>
        </p>
      )}

      {preview && (
        <>
          <dl className="stats">
            <Stat label="Filas leídas" value={preview.total_rows} />
            <Stat label="Productos nuevos" value={preview.new_count} />
            <Stat label="Ya existen" value={preview.existing_count} />
            <Stat label="Filas con errores" value={preview.error_rows} danger={hasErrors} />
          </dl>

          {preview.new_categories.length > 0 && (
            <p className="notice notice-warn" role="status">
              {preview.new_categories.length === 1 ? "Se va a crear esta categoría nueva" : "Se van a crear estas categorías nuevas"}:{" "}
              <strong>{preview.new_categories.join(", ")}</strong>. Si alguna es un error de tipeo, corregí el archivo y volvé a subirlo.
            </p>
          )}

          {hasErrors && <ErrorsTable errors={preview.errors} total={preview.errors_total} />}
          {preview.preview.length > 0 && <PreviewTable items={preview.preview} />}

          {hasErrors ? (
            <p className="muted">Corregí los errores en el archivo y volvé a subirlo para poder importar.</p>
          ) : (
            <>
              {preview.existing_count > 0 && (
                <fieldset className="mode">
                  <legend>Si el código ya existe</legend>
                  <label className="radio">
                    <input type="radio" name="mode" value="skip" checked={mode === "skip"} onChange={() => setMode("skip")} />
                    Omitir (no se toca el producto)
                  </label>
                  <label className="radio">
                    <input type="radio" name="mode" value="update" checked={mode === "update"} onChange={() => setMode("update")} />
                    Actualizar precio, stock y stock mínimo
                  </label>
                  {mode === "update" && (
                    <p className="hint">
                      Las celdas vacías no cambian el valor actual. El nombre, la categoría y la descripción no se modifican.
                    </p>
                  )}
                </fieldset>
              )}

              <div className="import-submit">
                <button type="button" className="btn btn-primary" onClick={handleImport} disabled={!canImport || importing}>
                  {importing ? "Importando…" : "Importar"}
                </button>
                {nothingToDo && (
                  <span className="muted">No hay productos nuevos. Elegí «Actualizar» si querés modificar los que ya existen.</span>
                )}
              </div>
            </>
          )}
        </>
      )}
    </div>
  );
}
