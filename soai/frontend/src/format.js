// Formatos de números para mostrar en pantalla (es-AR). Los usan las tablas y la vista previa de la importación.
export const money = new Intl.NumberFormat("es-AR", { style: "currency", currency: "ARS" });
export const integer = new Intl.NumberFormat("es-AR");
