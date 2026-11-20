import { Routes, Route } from "react-router-dom";

import Layout from "./components/Layout.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Products from "./pages/Products.jsx";
import LoadData from "./pages/LoadData.jsx";

export default function App() {
  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/" element={<Dashboard />} />
        <Route path="/products" element={<Products />} />
        <Route path="/load-data" element={<LoadData />} />
        <Route path="*" element={<p>La página que buscás no existe.</p>} />
      </Route>
    </Routes>
  );
}
