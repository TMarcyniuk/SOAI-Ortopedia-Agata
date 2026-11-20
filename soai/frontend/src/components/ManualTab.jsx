import { useCallback, useEffect, useState } from "react";

import { createCategory, createProduct, getCategories } from "../api.js";
import CategoryList from "./CategoryList.jsx";
import ProductForm, { ErrorMessage } from "./ProductForm.jsx";

// Pestaña "Manual": alta de un producto y administración de categorías.
// Al guardar, el formulario queda limpio para cargar el siguiente.
// `active` es true cuando la pestaña está a la vista: ahí se vuelven a pedir las categorías
// (así aparecen las que se crearon con una importación y los conteos están al día).
export default function ManualTab({ active }) {
  const [categories, setCategories] = useState([]);
  const [loadError, setLoadError] = useState("");
  const [formKey, setFormKey] = useState(0); // al cambiar, el formulario se vuelve a armar vacío
  const [notice, setNotice] = useState("");

  const loadCategories = useCallback(() => {
    getCategories()
      .then((list) => {
        setCategories(list);
        setLoadError("");
      })
      .catch((err) => setLoadError(err.message));
  }, []);

  useEffect(() => {
    if (active) loadCategories();
  }, [active, loadCategories]);

  async function handleSubmit(values) {
    setNotice("");
    const product = await createProduct(values); // si falla, ProductForm muestra los errores
    setNotice(`Se guardó "${product.name}" (${product.code}). Ya podés cargar el siguiente.`);
    setFormKey((k) => k + 1);
    loadCategories(); // para actualizar la cantidad de productos de cada categoría
  }

  async function handleCreateCategory(name) {
    const category = await createCategory(name);
    setCategories((list) => [...list, { ...category, product_count: 0 }]);
    return category;
  }

  function handleDeleted(category) {
    setCategories((list) => list.filter((c) => c.id !== category.id));
    setNotice(`Se eliminó la categoría "${category.name}".`);
  }

  return (
    <>
      <div className="card">
        {notice && <p className="notice" role="status">{notice}</p>}
        {loadError && <ErrorMessage banner>{loadError}</ErrorMessage>}
        <ProductForm
          key={formKey}
          categories={categories}
          onSubmit={handleSubmit}
          onCreateCategory={handleCreateCategory}
          submitLabel="Guardar producto"
        />
      </div>
      <CategoryList categories={categories} onDeleted={handleDeleted} />
    </>
  );
}
