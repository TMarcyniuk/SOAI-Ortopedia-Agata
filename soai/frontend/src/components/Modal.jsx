import { useEffect, useRef } from "react";

// Ventana de diálogo con el <dialog> nativo (se cierra con Esc y mantiene el foco adentro)
export default function Modal({ title, onClose, children }) {
  const ref = useRef(null);
  useEffect(() => {
    if (!ref.current.open) ref.current.showModal();
  }, []);
  return (
    <dialog
      ref={ref}
      className="modal"
      aria-label={title}
      onCancel={(event) => {
        event.preventDefault();
        onClose();
      }}
    >
      <h2>{title}</h2>
      {children}
    </dialog>
  );
}
