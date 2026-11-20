import { useState } from "react";

// Mensaje de error: siempre con ícono + texto (no solo color)
export function ErrorMessage({ children, banner = false }) {
  return (
    <p className={banner ? "error-message banner" : "error-message"} role="alert">
      <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
        <circle cx="12" cy="12" r="9" />
        <path d="M12 7.5v5.5M12 16.5v.5" />
      </svg>
      <span>{children}</span>
    </p>
  );
}

function Field({ label, name, error, hint, className = "", children }) {
  return (
    <div className={`field ${error ? "has-error" : ""} ${className}`}>
      <label htmlFor={name}>{label}</label>
      {children}
      {hint && !error && <p className="hint">{hint}</p>}
      {error && <ErrorMessage>{error}</ErrorMessage>}
    </div>
  );
}

// Valores iniciales: vacíos para un producto nuevo, o los del producto a editar
function initialValues(product) {
  if (!product) {
    return { code: "", name: "", category_id: "", price: "", stock: "0", min_stock: "", description: "" };
  }
  return {
    code: product.code,
    name: product.name,
    category_id: String(product.category_id),
    price: product.price.replace(".", ","), // se muestra con coma, como en Argentina
    stock: String(product.stock),
    min_stock: product.min_stock === null ? "" : String(product.min_stock),
    description: product.description || "",
  };
}

/**
 * Formulario de producto. Si recibe `product` es para editar (el código queda bloqueado).
 * La validación la hace el backend: acá solo se muestran sus errores.
 * onSubmit(values) debe devolver una promesa; si falla, se muestran los errores.
 */
export default function ProductForm({ categories, product, onSubmit, onCancel, submitLabel = "Guardar cambios" }) {
  const [values, setValues] = useState(() => initialValues(product));
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [fields, setFields] = useState({});

  const set = (key) => (event) => setValues((v) => ({ ...v, [key]: event.target.value }));

  async function handleSubmit(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setFields({});
    try {
      await onSubmit(values);
    } catch (err) {
      setError(err.message);
      setFields(err.fields || {});
    } finally {
      setSaving(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} noValidate>
      {error && <ErrorMessage banner>{error}</ErrorMessage>}

      <div className="form-grid">
        <Field label="Código" name="code" error={fields.code} hint={product ? "El código no se puede modificar." : null}>
          <input id="code" className="control" value={values.code} onChange={set("code")} disabled={!!product} />
        </Field>
        <Field label="Categoría" name="category_id" error={fields.category_id}>
          <select id="category_id" className="control" value={values.category_id} onChange={set("category_id")}>
            <option value="">Elegí una categoría</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </Field>
        <Field label="Nombre" name="name" error={fields.name} className="span-2">
          <input id="name" className="control" value={values.name} onChange={set("name")} />
        </Field>
        <Field label="Precio (ARS)" name="price" error={fields.price} hint="Podés escribir 1.234,56 o 1234.56">
          <input id="price" className="control" inputMode="decimal" value={values.price} onChange={set("price")} />
        </Field>
        <Field label="Stock" name="stock" error={fields.stock}>
          <input id="stock" className="control" inputMode="numeric" value={values.stock} onChange={set("stock")} />
        </Field>
        <Field label="Stock mínimo (opcional)" name="min_stock" error={fields.min_stock} hint="Avisa cuando el stock llega a este número o menos.">
          <input id="min_stock" className="control" inputMode="numeric" value={values.min_stock} onChange={set("min_stock")} />
        </Field>
        <Field label="Descripción (opcional)" name="description" error={fields.description} className="span-2">
          <textarea id="description" className="control" rows="3" value={values.description} onChange={set("description")} />
        </Field>
      </div>

      <div className="modal-actions">
        {onCancel && (
          <button type="button" className="btn btn-secondary" onClick={onCancel} disabled={saving}>
            Cancelar
          </button>
        )}
        <button type="submit" className="btn btn-primary" disabled={saving}>
          {saving ? "Guardando…" : submitLabel}
        </button>
      </div>
    </form>
  );
}
