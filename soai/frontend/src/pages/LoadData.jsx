import { useRef, useState } from "react";

import ImportTab from "../components/ImportTab.jsx";
import ManualTab from "../components/ManualTab.jsx";

const TABS = [
  { id: "manual", label: "Manual" },
  { id: "excel", label: "Desde Excel" },
];

export default function LoadData() {
  const [tab, setTab] = useState("manual");
  const tabRefs = useRef({});

  // Con las flechas izquierda y derecha se pasa de una pestaña a la otra
  function handleKeyDown(event) {
    const step = event.key === "ArrowRight" ? 1 : event.key === "ArrowLeft" ? -1 : 0;
    if (!step) return;
    event.preventDefault();
    const index = (TABS.findIndex((t) => t.id === tab) + step + TABS.length) % TABS.length;
    setTab(TABS[index].id);
    tabRefs.current[TABS[index].id].focus();
  }

  return (
    <>
      <h1>Cargar datos</h1>

      <div className="tabs" role="tablist" aria-label="Forma de cargar datos" onKeyDown={handleKeyDown}>
        {TABS.map((t) => (
          <button
            key={t.id}
            id={`tab-${t.id}`}
            ref={(element) => {
              tabRefs.current[t.id] = element;
            }}
            type="button"
            role="tab"
            aria-selected={tab === t.id}
            aria-controls={`panel-${t.id}`}
            tabIndex={tab === t.id ? 0 : -1}
            className={tab === t.id ? "tab active" : "tab"}
            onClick={() => setTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {/* Las dos pestañas quedan montadas (solo se ocultan) para no perder lo que se estaba haciendo */}
      <div id="panel-manual" role="tabpanel" aria-labelledby="tab-manual" hidden={tab !== "manual"}>
        <ManualTab active={tab === "manual"} />
      </div>
      <div id="panel-excel" role="tabpanel" aria-labelledby="tab-excel" hidden={tab !== "excel"}>
        <ImportTab />
      </div>
    </>
  );
}
