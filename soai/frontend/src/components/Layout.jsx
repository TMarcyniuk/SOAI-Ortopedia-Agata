import { useEffect, useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { getHealth } from "../api.js";

const MENU = [
  { to: "/products", label: "Productos" },
  { to: "/load-data", label: "Cargar datos" },
];

// Logo reconstruido con ladrillos redondeados (colores estimados del logo de Agata)
function Logo() {
  return (
    <div className="logo">
      <svg viewBox="0 0 48 58" width="40" height="48" role="img" aria-label="Logo de Agata">
        <rect x="0" y="4" width="14" height="14" rx="4" fill="var(--amber-500)" />
        <rect x="17" y="0" width="14" height="24" rx="4" fill="var(--brand)" />
        <rect x="0" y="21" width="27" height="13" rx="4" fill="var(--pink-500)" />
        <rect x="30" y="27" width="18" height="14" rx="4" fill="var(--amber-500)" />
        <rect x="3" y="37" width="14" height="21" rx="4" fill="var(--brand)" />
        <rect x="20" y="44" width="18" height="12" rx="4" fill="var(--pink-500)" />
      </svg>
      <div className="logo-text">
        <span className="logo-small">ORTOPEDIA</span>
        <span className="logo-big">Agata</span>
      </div>
    </div>
  );
}

// Indicador chico para verificar que el frontend llega al backend
function ServerStatus() {
  const [status, setStatus] = useState("checking"); // checking | ok | down

  useEffect(() => {
    getHealth()
      .then(() => setStatus("ok"))
      .catch(() => setStatus("down"));
  }, []);

  const text = {
    checking: "Conectando con el servidor…",
    ok: "Servidor conectado",
    down: "Sin conexión con el servidor",
  }[status];

  return <p className={`server-status server-${status}`}>{text}</p>;
}

export default function Layout() {
  return (
    <div className="app">
      <aside className="sidebar">
        <Logo />
        <nav className="menu" aria-label="Menú principal">
          {MENU.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => (isActive ? "menu-link active" : "menu-link")}
            >
              {item.label}
            </NavLink>
          ))}
        </nav>
        <ServerStatus />
      </aside>
      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
