import { Link, Navigate, Routes, Route } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import Products from "./pages/Products.jsx";
import LoadData from "./pages/LoadData.jsx";

function NotFound() {
  return (
    <>
      <h1>Página no encontrada</h1>
      <p>La página que buscás no existe. <Link to="/products">Volver a Productos</Link></p>
    </>
  );
}

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        {/* La página de inicio es la lista de productos */}
        <Route path="/" element={<Navigate to="/products" replace />} />
        <Route path="/products" element={<Products />} />
        <Route path="/load-data" element={<LoadData />} />
        <Route path="*" element={<NotFound />} />
      </Route>
    </Routes>
  );
}
