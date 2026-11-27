// Utilidades compartidas por las escenas del capítulo «Del tren a la calle».
(function () {
  const BASE = window.E8_BASE || (location.pathname.includes("/graficas/") ? "../datos/" : "datos/");

  const COLOR = {
    morado: "#600d8b", moradoMedio: "#9b5bbf", moradoSuave: "#e9d8f3",
    oro: "#ed9f22", oroOscuro: "#b45309", oroSuave: "#fbe3b8",
    gris: "#9ca3af", grisClaro: "#e5e7eb", grisTexto: "#4b5563", tinta: "#0d0d0d",
  };

  // Lee un CSV con tipos, conservando como texto las columnas indicadas (claves con ceros, meses).
  function parsear(texto, comoTexto) {
    return d3.csvParse(texto, (r) => {
      const guardadas = {};
      for (const c of comoTexto) guardadas[c] = r[c];
      d3.autoType(r);
      Object.assign(r, guardadas);
      return r;
    });
  }

  // Las escenas solo leen los CSV y el GeoJSON de booklet/datos/, con rutas relativas.
  async function cargarCsv(nombre, comoTexto = []) {
    const texto = await d3.text(`${BASE}${nombre}.csv`);
    return parsear(texto, comoTexto);
  }

  async function cargarJson(nombre) {
    return d3.json(`${BASE}${nombre}.geojson`);
  }

  const entero = d3.format(",d");
  const conSigno = (v) => (v > 0 ? "+" : v < 0 ? "−" : "") + entero(Math.abs(v));
  const pct = (v, dec = 1) => (v == null || Number.isNaN(v) ? "s/d" : `${v > 0 ? "+" : v < 0 ? "−" : ""}${Math.abs(v).toFixed(dec)} %`);
  const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

  function fallo(selector, error) {
    console.error(error);
    d3.select(selector).append("p").attr("class", "error-carga")
      .text("No se pudieron leer los datos de la escena. Abre la carpeta booklet/ con un servidor local: python -m http.server -d booklet");
  }

  // Animación de entrada, solo en pantalla. Cada escena se dibuja ya terminada; «inicio» la lleva al estado
  // de arranque y «correr» la anima cuando entra en la vista. Con «reducir movimiento» o al imprimir no se
  // anima: «fin» deja el estado final.
  const quietos = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const finales = [];
  window.addEventListener("beforeprint", () => finales.forEach((f) => f()));
  function animar(nodo, { inicio, correr, fin }) {
    if (quietos || window.matchMedia("print").matches || !("IntersectionObserver" in window)) return;
    const svg = d3.select(nodo);
    const terminar = () => { svg.selectAll("*").interrupt(); fin(); };
    finales.push(terminar);
    inicio();
    const vigia = new IntersectionObserver((entradas) => {
      if (entradas.some((e) => e.isIntersecting)) { vigia.disconnect(); correr(); }
    }, { threshold: 0.35 });
    vigia.observe(nodo);
  }

  window.E8 = { COLOR, cargarCsv, cargarJson, entero, conSigno, pct, MESES, fallo, animar };
})();
