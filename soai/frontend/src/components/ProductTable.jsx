const money = new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" });
const integer = new Intl.NumberFormat("es-AR");

// Estados del producto: siempre se muestran con texto, no solo con color
const STATUS = {
  normal: { label: "Normal", className: "badge-ok" },
  low: { label: "Stock bajo", className: "badge-warn" },
  out: { label: "Sin stock", className: "badge-danger" },
  inactive: { label: "Inactivo", className: "badge-muted" },
};

export const BanIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" aria-hidden="true">
    <circle cx="12" cy="12" r="9" />
    <path d="M5.6 5.6l12.8 12.8" />
  </svg>
);

// Tabla de productos con sus acciones (editar y desactivar/reactivar)
export default function ProductTable({ items, loading, onEdit, onToggle }) {
  return (
    <div className={loading ? "table-wrap is-loading" : "table-wrap"} aria-busy={loading}>
      <table>
        <caption className="sr-only">Lista de productos</caption>
        <thead>
          <tr>
            <th>Código</th>
            <th>Nombre</th>
            <th>Categoría</th>
            <th className="num">Precio</th>
            <th className="num">Stock</th>
            <th className="num">Mínimo</th>
            <th>Estado</th>
            <th><span className="sr-only">Acciones</span></th>
          </tr>
        </thead>
        <tbody>
          {items.map((p) => (
            <tr key={p.id} className={p.is_active ? "" : "row-inactive"}>
              <td>{p.code}</td>
              <td>{p.name}</td>
              <td>{p.category_name}</td>
              <td className="num">{money.format(Number(p.price))}</td>
              <td className="num">{integer.format(p.stock)}</td>
              <td className="num">{p.min_stock === null ? "—" : integer.format(p.min_stock)}</td>
              <td>
                <span className={`badge ${STATUS[p.status].className}`}>{STATUS[p.status].label}</span>
              </td>
              <td>
                <div className="actions">
                  <button type="button" className="btn btn-secondary" onClick={() => onEdit(p)}>
                    Editar
                  </button>
                  {p.is_active ? (
                    <button type="button" className="btn btn-danger" onClick={() => onToggle(p)}>
                      <BanIcon /> Desactivar
                    </button>
                  ) : (
                    <button type="button" className="btn btn-secondary" onClick={() => onToggle(p)}>
                      Reactivar
                    </button>
                  )}
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
