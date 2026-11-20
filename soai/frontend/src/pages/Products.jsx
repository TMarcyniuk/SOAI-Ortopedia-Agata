import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getCategories, getProducts, toggleProductActive, updateProduct } from "../api.js";
import Modal from "../components/Modal.jsx";
import ProductForm, { ErrorMessage } from "../components/ProductForm.jsx";
import ProductTable, { BanIcon } from "../components/ProductTable.jsx";

const integer = new Intl.NumberFormat("es-AR");
const EMPTY_FILTERS = { q: "", category_id: "", stock: "all", active: "1" };

export default function Products() {
  const [categories, setCategories] = useState([]);
  const [searchText, setSearchText] = useState("");
  const [filters, setFilters] = useState(EMPTY_FILTERS);
  const [page, setPage] = useState(1);
  const [data, setData] = useState(null); // { items, total, pages }
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");
  const [reloadKey, setReloadKey] = useState(0);
  const [editing, setEditing] = useState(null); // producto que se está editando
  const [toggling, setToggling] = useState(null); // producto a desactivar o reactivar
  const [toggleBusy, setToggleBusy] = useState(false);
  const [toggleError, setToggleError] = useState("");
  const [notice, setNotice] = useState("");

  // Categorías para el filtro y el formulario (se cargan una vez)
  useEffect(() => {
    getCategories()
      .then(setCategories)
      .catch((err) => setLoadError(err.message));
  }, []);

  // Buscador con debounce de 300 ms: recién consulta cuando se deja de escribir
  useEffect(() => {
    const timer = setTimeout(() => {
      setFilters((f) => (f.q === searchText ? f : { ...f, q: searchText }));
      setPage(1);
    }, 300);
    return () => clearTimeout(timer);
  }, [searchText]);

  // Trae la lista cada vez que cambian los filtros o la página
  useEffect(() => {
    let ignore = false; // evita que una respuesta vieja pise a una más nueva
    setLoading(true);
    getProducts({ ...filters, page, per_page: 25 })
      .then((result) => {
        if (ignore) return;
        setData(result);
        setLoadError("");
      })
      .catch((err) => {
        if (!ignore) setLoadError(err.message);
      })
      .finally(() => {
        if (!ignore) setLoading(false);
      });
    return () => {
      ignore = true;
    };
  }, [filters, page, reloadKey]);

  // El aviso de éxito desaparece solo
  useEffect(() => {
    if (!notice) return;
    const timer = setTimeout(() => setNotice(""), 4000);
    return () => clearTimeout(timer);
  }, [notice]);

  function changeFilter(key, value) {
    setFilters((f) => ({ ...f, [key]: value }));
    setPage(1);
  }

  function clearFilters() {
    setSearchText("");
    setFilters(EMPTY_FILTERS);
    setPage(1);
  }

  async function handleSave(values) {
    await updateProduct(editing.id, values); // si falla, ProductForm muestra los errores
    setEditing(null);
    setNotice("Producto actualizado.");
    setReloadKey((k) => k + 1);
  }

  async function handleToggle() {
    setToggleBusy(true);
    setToggleError("");
    try {
      const updated = await toggleProductActive(toggling.id);
      setToggling(null);
      setNotice(updated.is_active ? "Producto reactivado." : "Producto desactivado.");
      setReloadKey((k) => k + 1);
    } catch (err) {
      setToggleError(err.message);
    } finally {
      setToggleBusy(false);
    }
  }

  const hasFilters = filters.q || filters.category_id || filters.stock !== "all" || filters.active !== "1";
  const items = data ? data.items : [];

  return (
    <>
      <h1>Productos</h1>

      {notice && <p className="notice" role="status">{notice}</p>}
      {loadError && <ErrorMessage banner>{loadError}</ErrorMessage>}

      <input
        type="search"
        className="control search-input"
        placeholder="Buscar por código o nombre"
        aria-label="Buscar por código o nombre"
        value={searchText}
        onChange={(event) => setSearchText(event.target.value)}
      />

      <div className="filters">
        <div className="field">
          <label htmlFor="f-category">Categoría</label>
          <select id="f-category" className="control" value={filters.category_id} onChange={(e) => changeFilter("category_id", e.target.value)}>
            <option value="">Todas</option>
            {categories.map((c) => (
              <option key={c.id} value={c.id}>{c.name}</option>
            ))}
          </select>
        </div>
        <div className="field">
          <label htmlFor="f-stock">Stock</label>
          <select id="f-stock" className="control" value={filters.stock} onChange={(e) => changeFilter("stock", e.target.value)}>
            <option value="all">Todos</option>
            <option value="low">Stock bajo</option>
            <option value="out">Sin stock</option>
          </select>
        </div>
        <div className="field">
          <label htmlFor="f-active">Estado</label>
          <select id="f-active" className="control" value={filters.active} onChange={(e) => changeFilter("active", e.target.value)}>
            <option value="1">Activos</option>
            <option value="0">Inactivos</option>
            <option value="all">Todos</option>
          </select>
        </div>
      </div>

      {!data && loading && <p className="muted">Cargando productos…</p>}

      {data && data.total === 0 && (
        <div className="empty-state">
          {hasFilters ? (
            <>
              <p>No encontramos productos con esos filtros.</p>
              <p><button type="button" className="btn btn-secondary" onClick={clearFilters}>Limpiar filtros</button></p>
            </>
          ) : (
            <p>Todavía no cargaste productos. Empezá por <Link to="/load-data">Cargar datos</Link>.</p>
          )}
        </div>
      )}

      {data && data.total > 0 && (
        <>
          <ProductTable
            items={items}
            loading={loading}
            onEdit={setEditing}
            onToggle={(product) => {
              setToggleError("");
              setToggling(product);
            }}
          />

          <div className="pagination">
            <p className="muted">
              Página {data.page} de {data.pages} · {integer.format(data.total)} {data.total === 1 ? "producto" : "productos"}
            </p>
            <div className="actions">
              <button type="button" className="btn btn-secondary" disabled={page <= 1} onClick={() => setPage(page - 1)}>
                Anterior
              </button>
              <button type="button" className="btn btn-secondary" disabled={page >= data.pages} onClick={() => setPage(page + 1)}>
                Siguiente
              </button>
            </div>
          </div>
        </>
      )}

      {editing && (
        <Modal title="Editar producto" onClose={() => setEditing(null)}>
          <ProductForm categories={categories} product={editing} onSubmit={handleSave} onCancel={() => setEditing(null)} />
        </Modal>
      )}

      {toggling && (
        <Modal title={toggling.is_active ? "Desactivar producto" : "Reactivar producto"} onClose={() => setToggling(null)}>
          {toggleError && <ErrorMessage banner>{toggleError}</ErrorMessage>}
          <p>
            {toggling.is_active
              ? `¿Querés desactivar "${toggling.name}"? Dejará de aparecer entre los productos activos, pero no se borra y lo podés reactivar cuando quieras.`
              : `¿Querés reactivar "${toggling.name}"? Va a volver a aparecer entre los productos activos.`}
          </p>
          <div className="modal-actions">
            <button type="button" className="btn btn-secondary" onClick={() => setToggling(null)} disabled={toggleBusy}>
              Cancelar
            </button>
            {toggling.is_active ? (
              <button type="button" className="btn btn-danger" onClick={handleToggle} disabled={toggleBusy}>
                <BanIcon /> {toggleBusy ? "Desactivando…" : "Sí, desactivar"}
              </button>
            ) : (
              <button type="button" className="btn btn-primary" onClick={handleToggle} disabled={toggleBusy}>
                {toggleBusy ? "Reactivando…" : "Sí, reactivar"}
              </button>
            )}
          </div>
        </Modal>
      )}
    </>
  );
}
