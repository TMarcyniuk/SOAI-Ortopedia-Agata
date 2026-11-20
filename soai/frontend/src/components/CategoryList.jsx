import { useState } from "react";

import { deleteCategory } from "../api.js";
import Modal from "./Modal.jsx";
import { ErrorMessage } from "./ProductForm.jsx";

const TrashIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
    <path d="M4 7h16M10 11v6M14 11v6M6 7l1 12a1 1 0 0 0 1 1h8a1 1 0 0 0 1-1l1-12M9 7V4h6v3" />
  </svg>
);

// Lista de categorías con su cantidad de productos. Solo se puede eliminar una que no tenga ninguno.
export default function CategoryList({ categories, onDeleted }) {
  const [deleting, setDeleting] = useState(null); // categoría a eliminar
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  function close() {
    setDeleting(null);
    setError("");
  }

  async function handleDelete() {
    setBusy(true);
    setError("");
    try {
      await deleteCategory(deleting.id);
      onDeleted(deleting);
      close();
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="card category-list">
      <h2 className="section-title">Categorías</h2>
      <p className="muted">Solo se puede eliminar una categoría que no tiene productos.</p>

      {categories.length === 0 ? (
        <p className="muted">Todavía no hay categorías.</p>
      ) : (
        <ul className="category-items">
          {categories.map((c) => {
            const count = c.product_count ?? 0;
            return (
              <li key={c.id}>
                <span className="category-name">{c.name}</span>
                <span className="muted">{count === 1 ? "1 producto" : `${count} productos`}</span>
                <button
                  type="button"
                  className="btn btn-danger"
                  disabled={count > 0}
                  aria-label={`Eliminar la categoría ${c.name}`}
                  onClick={() => setDeleting(c)}
                >
                  <TrashIcon /> Eliminar
                </button>
              </li>
            );
          })}
        </ul>
      )}

      {deleting && (
        <Modal title="Eliminar categoría" onClose={close}>
          {error && <ErrorMessage banner>{error}</ErrorMessage>}
          <p>¿Querés eliminar la categoría "{deleting.name}"? Se borra para siempre y no se puede deshacer.</p>
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={close} disabled={busy}>
              Cancelar
            </button>
            <button type="button" className="btn btn-danger" onClick={handleDelete} disabled={busy}>
              <TrashIcon /> {busy ? "Eliminando…" : "Sí, eliminar"}
            </button>
          </div>
        </Modal>
      )}
    </section>
  );
}
