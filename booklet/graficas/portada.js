// Las 3 cifras de «La historia en 10 segundos», calculadas de los CSV de booklet/datos/.
window.dibujarPortada = async function () {
  const { cargarCsv, entero, conSigno, pct, fallo } = window.E8;
  let e2, e3, e4;
  try {
    [e2, e3, e4] = await Promise.all([
      cargarCsv("escena-2", ["estacion_id"]), cargarCsv("escena-3", ["mes"]), cargarCsv("escena-4", ["cvegeo_ageb"]),
    ]);
  } catch (e) { return fallo("#datos-clave", e); }
  const poner = (id, texto) => { document.getElementById(id).textContent = texto; };

  // 1. Negocios a 5 km de las 34 estaciones.
  const n19 = d3.sum(e2, (d) => d.negocios_2019), n25 = d3.sum(e2, (d) => d.negocios_2025);
  poner("cifra-negocios", `${conSigno(n25 - n19)} negocios`);
  poner("detalle-negocios", `a 5 km de las ${e2.length} estaciones: de ${entero(n19)} en 2019 a ${entero(n25)} en 2025 ` +
    `(${pct((n25 / n19 - 1) * 100)}). INEGI, DENUE nov 2019 y may 2025.`);

  // 2. Pasajeros del mismo periodo, último año contra el anterior.
  const ultimo = d3.max(e3, (d) => d.anio);
  const meses = new Set(e3.filter((d) => d.anio === ultimo).map((d) => d.mes.slice(5, 7)));
  const suma = (anio) => d3.sum(e3.filter((d) => d.anio === anio && meses.has(d.mes.slice(5, 7))), (d) => d.pasajeros);
  const actual = suma(ultimo), previo = suma(ultimo - 1);
  const ultimoMes = window.E8.MESES[d3.max([...meses], (m) => +m) - 1];
  poner("cifra-pasajeros", `${pct((actual / previo - 1) * 100)} pasajeros`);
  poner("detalle-pasajeros", `de enero a ${ultimoMes} de ${ultimo} contra el mismo periodo de ${ultimo - 1}: ` +
    `${entero(actual)} frente a ${entero(previo)}. Tren Maya, datos abiertos.`);

  // 3. La AGEB que más negocios perdió en Mérida y cuántas ganaron.
  const peor = e4.reduce((a, b) => (b.cambio < a.cambio ? b : a));
  const ganaron = e4.filter((d) => d.cambio > 0).length;
  poner("cifra-centro", `${conSigno(peor.cambio)} negocios`);
  poner("detalle-centro", `en la AGEB del Centro de Mérida (${peor.cvegeo_ageb}), mientras ${entero(ganaron)} de las ` +
    `${entero(e4.length)} AGEB urbanas ganaron negocios. INEGI, DENUE y Censo 2020.`);
};
