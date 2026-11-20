// Funciones fetch al backend. La dirección sale de VITE_API_URL (.env).
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:5000";

// Hace el pedido y, si el backend devuelve un error, lo lanza como Error
// con { status, fields } para mostrar el mensaje (y los errores por campo).
async function request(path, options = {}) {
  let response;
  try {
    response = await fetch(`${API_URL}${path}`, options);
  } catch {
    throw new Error("No se pudo conectar con el servidor.");
  }
  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const error = new Error(data.error || "Ocurrió un error inesperado.");
    error.status = response.status;
    error.fields = data.fields || {};
    throw error;
  }
  return data;
}

export const getHealth = () => request("/api/health");

// Arma ?a=1&b=2 salteando los valores vacíos
function toQuery(params) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== "" && value !== null && value !== undefined) query.set(key, value);
  });
  const text = query.toString();
  return text ? `?${text}` : "";
}

export const getCategories = () => request("/api/categories");

export const getProducts = (params) => request(`/api/products${toQuery(params)}`);

export const updateProduct = (id, values) =>
  request(`/api/products/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(values),
  });

export const toggleProductActive = (id) =>
  request(`/api/products/${id}/toggle-active`, { method: "POST" });
