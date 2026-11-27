// Utilidades compartidas por las escenas del capítulo «Del tren a la calle».
(function () {
  const BASE = window.E8_BASE || (location.pathname.includes("/graficas/") ? "../datos/" : "datos/");

  const COLOR = {
    morado: "#600d8b", moradoMedio: "#9b5bbf", moradoSuave: "#e9d8f3",
    oro: "#ed9f22", oroOscuro: "#9a5b08", oroSuave: "#fbe3b8",
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

  // Primero el CSV publicado; si el navegador no deja leerlo (archivo abierto sin servidor), la copia de datos.js.
  async function cargarCsv(nombre, comoTexto = []) {
    try {
      const texto = await d3.text(`${BASE}${nombre}.csv`);
      return parsear(texto, comoTexto);
    } catch (e) {
      if (window.E8_DATOS && window.E8_DATOS[nombre]) return parsear(window.E8_DATOS[nombre], comoTexto);
      throw e;
    }
  }

  async function cargarJson(nombre) {
    try {
      return await d3.json(`${BASE}${nombre}.geojson`);
    } catch (e) {
      if (window.E8_DATOS && window.E8_DATOS[nombre]) return window.E8_DATOS[nombre];
      throw e;
    }
  }

  const entero = d3.format(",d");
  const conSigno = (v) => (v > 0 ? "+" : v < 0 ? "−" : "") + entero(Math.abs(v));
  const pct = (v, dec = 1) => (v == null || Number.isNaN(v) ? "s/d" : `${v > 0 ? "+" : v < 0 ? "−" : ""}${Math.abs(v).toFixed(dec)} %`);
  const MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"];

  function fallo(selector, error) {
    console.error(error);
    d3.select(selector).append("p").attr("class", "error-carga")
      .text("No se pudieron leer los datos de la escena. Abre la carpeta booklet/ con un servidor local (python -m http.server) o revisa que exista graficas/datos.js.");
  }

  window.E8 = { COLOR, cargarCsv, cargarJson, entero, conSigno, pct, MESES, fallo };
})();
