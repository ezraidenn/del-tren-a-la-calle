// Escena 4 · Variación de negocios por AGEB urbana de Mérida, 2019 a 2025.
window.dibujarEscena4 = async function (selector = "#grafica-escena-4") {
  const { COLOR, cargarCsv, cargarJson, entero, conSigno, pct, fallo } = window.E8;
  let datos, geo;
  try {
    [datos, geo] = await Promise.all([cargarCsv("escena-4", ["cvegeo_ageb"]), cargarJson("merida_ageb")]);
  } catch (e) { return fallo(selector, e); }

  const porClave = new Map(datos.map((d) => [d.cvegeo_ageb, d]));
  const CENTRO = "3105000010510";

  // Cortes del cambio absoluto: oro para pérdida, morado para ganancia, gris claro sin cambio.
  const cortes = [-49.5, -9.5, -0.5, 0.5, 9.5, 49.5];
  const colores = ["#9a5b08", "#ed9f22", "#fbe3b8", "#f3f4f6", "#e9d8f3", "#9b5bbf", "#600d8b"];
  const escala = d3.scaleThreshold().domain(cortes).range(colores);
  const etiquetas = ["−50 o más", "−49 a −10", "−9 a −1", "sin cambio", "+1 a +9", "+10 a +49", "+50 o más"];

  const W = 960, H = 760, mapaW = 700;
  const svg = d3.select(selector).append("svg").attr("viewBox", `0 0 ${W} ${H}`)
    .attr("role", "img").attr("aria-label", "Mapa de las AGEB urbanas de Mérida coloreadas por negocios ganados o perdidos");

  // El encuadre es la ciudad de Mérida (localidad 0001); las AGEB de las comisarías quedan fuera del recuadro
  // pero cuentan en los totales.
  const ciudad = { type: "FeatureCollection", features: geo.features.filter((f) => f.properties.cvegeo_ageb.slice(5, 9) === "0001") };
  const proy = d3.geoMercator().fitExtent([[10, 10], [mapaW, H - 10]], ciudad);
  const camino = d3.geoPath(proy);
  const recorte = `recorte-mapa-${Math.random().toString(36).slice(2, 8)}`;
  svg.append("clipPath").attr("id", recorte).append("rect").attr("width", mapaW + 10).attr("height", H);

  svg.append("g").attr("clip-path", `url(#${recorte})`).selectAll("path").data(geo.features).join("path")
    .attr("d", camino)
    .attr("fill", (f) => {
      const d = porClave.get(f.properties.cvegeo_ageb);
      return d ? escala(d.cambio) : "#ffffff";
    })
    .attr("stroke", (f) => (porClave.has(f.properties.cvegeo_ageb) ? "#ffffff" : COLOR.grisClaro))
    .attr("stroke-width", 0.6)
    .append("title").text((f) => {
      const d = porClave.get(f.properties.cvegeo_ageb);
      if (!d) return `AGEB ${f.properties.cvegeo_ageb}: sin dato de negocios en el Censo 2020`;
      return `AGEB ${d.cvegeo_ageb}: ${entero(d.negocios_2019)} negocios en 2019 y ${entero(d.negocios_2025)} en 2025 ` +
        `(${conSigno(d.cambio)}, ${pct(d.cambio_pct)})`;
    });

  // Señal del Centro, la AGEB con más negocios y la mayor pérdida.
  const fCentro = geo.features.find((f) => f.properties.cvegeo_ageb === CENTRO);
  const dCentro = porClave.get(CENTRO);
  if (fCentro && dCentro) {
    const [cx, cy] = camino.centroid(fCentro);
    svg.append("circle").attr("cx", cx).attr("cy", cy).attr("r", 9).attr("fill", "none")
      .attr("stroke", COLOR.tinta).attr("stroke-width", 2);
    // La etiqueta va fuera de la mancha urbana, a la izquierda, con halo blanco para leerse sobre el mapa.
    const lx = 150, ly = cy + 150;
    svg.append("line").attr("x1", cx - 7).attr("y1", cy + 7).attr("x2", lx + 4).attr("y2", ly - 22)
      .attr("stroke", COLOR.tinta).attr("stroke-width", 1.5);
    const t = svg.append("text").attr("x", lx).attr("y", ly).attr("text-anchor", "end")
      .style("font-size", "16px").style("font-weight", 800)
      .style("paint-order", "stroke").style("stroke", "#fff").style("stroke-width", "4px");
    t.append("tspan").text("Centro");
    t.append("tspan").attr("x", lx).attr("dy", "1.2em").style("font-weight", 600)
      .text(`${conSigno(dCentro.cambio)} negocios (${pct(dCentro.cambio_pct)})`);
  }

  // Leyenda y resumen a la derecha del mapa.
  const ley = svg.append("g").attr("transform", `translate(${mapaW + 30},40)`);
  ley.append("text").style("font-size", "16px").style("font-weight", 800).text("Negocios ganados o");
  ley.append("text").attr("y", 20).style("font-size", "16px").style("font-weight", 800).text("perdidos, 2019 a 2025");
  colores.slice().reverse().forEach((c, i) => {
    const g = ley.append("g").attr("transform", `translate(0,${48 + i * 28})`);
    g.append("rect").attr("width", 22).attr("height", 18).attr("rx", 3).attr("fill", c)
      .attr("stroke", COLOR.grisClaro);
    g.append("text").attr("x", 30).attr("y", 14).style("font-size", "15px").text(etiquetas[colores.length - 1 - i]);
  });
  const g0 = ley.append("g").attr("transform", `translate(0,${48 + colores.length * 28})`);
  g0.append("rect").attr("width", 22).attr("height", 18).attr("rx", 3).attr("fill", "#fff").attr("stroke", COLOR.gris);
  g0.append("text").attr("x", 30).attr("y", 14).style("font-size", "15px").text("sin dato");

  const crecen = datos.filter((d) => d.cambio > 0).length;
  const bajan = datos.filter((d) => d.cambio < 0).length;
  const iguales = datos.length - crecen - bajan;
  const resumen = [
    [`${entero(crecen)} AGEB`, "ganaron negocios"],
    [`${entero(bajan)} AGEB`, "perdieron negocios"],
    [`${entero(iguales)} AGEB`, "quedaron igual"],
  ];
  const r = ley.append("g").attr("transform", `translate(0,${48 + (colores.length + 1) * 28 + 40})`);
  resumen.forEach(([a, b], i) => {
    r.append("text").attr("y", i * 48).style("font-size", "20px").style("font-weight", 800)
      .style("fill", i === 1 ? COLOR.oroOscuro : COLOR.morado).text(a);
    r.append("text").attr("y", i * 48 + 20).style("font-size", "15px").style("fill", COLOR.grisTexto).text(b);
  });
};
