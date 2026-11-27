// Escena 2 · Las 34 estaciones sobre la península: cuántos negocios ganó o perdió cada una a 5 km, 2019 a 2025.
window.dibujarEscena2 = async function (selector = "#grafica-escena-2") {
  const { COLOR, cargarCsv, cargarJson, entero, conSigno, pct, fallo } = window.E8;
  let datos, estados;
  try {
    [datos, estados] = await Promise.all([cargarCsv("escena-2", ["estacion_id"]), cargarJson("estados_tren_maya")]);
  } catch (e) { return fallo(selector, e); }

  const W = 960, H = 640, mapa = [[20, 20], [640, H - 20]];
  const svg = d3.select(selector).append("svg").attr("viewBox", `0 0 ${W} ${H}`)
    .attr("role", "img").attr("aria-label", "Mapa de las 34 estaciones del Tren Maya con círculos del tamaño de los negocios ganados o perdidos");

  // El encuadre son las estaciones; los estados se recortan al rectángulo del mapa.
  const puntos = { type: "MultiPoint", coordinates: datos.map((d) => [d.lon, d.lat]) };
  const proy = d3.geoMercator().fitExtent([[60, 50], [600, H - 50]], puntos);
  const camino = d3.geoPath(proy);
  svg.append("clipPath").attr("id", "recorte-mapa-escena-2").append("rect")
    .attr("x", mapa[0][0]).attr("y", mapa[0][1]).attr("width", mapa[1][0] - mapa[0][0]).attr("height", mapa[1][1] - mapa[0][1]).attr("rx", 10);
  const base = svg.append("g").attr("clip-path", "url(#recorte-mapa-escena-2)");
  base.append("rect").attr("x", 0).attr("y", 0).attr("width", W).attr("height", H).attr("fill", "#f5f7fa");
  base.selectAll("path").data(estados.features).join("path").attr("d", camino)
    .attr("fill", "#ffffff").attr("stroke", COLOR.grisClaro).attr("stroke-width", 1.2);
  // Nombres de los estados de la península en un punto despejado de la ruta (Chiapas y Tabasco quedan en la orilla).
  const ROTULO_ESTADO = { "04": [-89.95, 19.05], "23": [-88.75, 19.95], "31": [-89.35, 20.3] };
  base.selectAll("text.estado").data(estados.features.filter((f) => ROTULO_ESTADO[f.properties.cve_ent])).join("text")
    .attr("class", "estado")
    .attr("transform", (f) => `translate(${proy(ROTULO_ESTADO[f.properties.cve_ent])})`).attr("text-anchor", "middle")
    .style("font-size", "15px").style("font-weight", 700).style("letter-spacing", "0.12em")
    .style("fill", "#c4c9d1").text((f) => f.properties.nombre.toUpperCase());

  // Trazo esquemático: estaciones unidas en el orden de la ruta, y Centenario de vuelta a Escárcega.
  const ruta = datos.slice().sort((a, b) => a.orden_ruta - b.orden_ruta);
  const linea = ruta.map((d) => proy([d.lon, d.lat]));
  const escarcega = ruta.find((d) => d.estacion === "Escárcega");
  if (escarcega) linea.push(proy([escarcega.lon, escarcega.lat]));
  base.append("path").attr("d", d3.line()(linea)).attr("fill", "none")
    .attr("stroke", COLOR.gris).attr("stroke-width", 2).attr("stroke-dasharray", "1 5").attr("stroke-linecap", "round");

  const r = d3.scaleSqrt().domain([0, d3.max(datos, (d) => Math.abs(d.cambio))]).range([0, 34]);
  const TEYA = "TM015";
  const nodos = base.append("g").selectAll("g").data(datos.slice().sort((a, b) => Math.abs(b.cambio) - Math.abs(a.cambio)))
    .join("g").attr("transform", (d) => `translate(${proy([d.lon, d.lat])})`);
  nodos.append("circle").attr("r", (d) => Math.max(3.5, r(Math.abs(d.cambio))))
    .attr("fill", (d) => (d.cambio > 0 ? COLOR.morado : d.cambio < 0 ? COLOR.oro : "#ffffff"))
    .attr("fill-opacity", (d) => (d.cambio === 0 ? 1 : 0.82))
    .attr("stroke", (d) => (d.estacion_id === TEYA ? COLOR.tinta : d.cambio === 0 ? COLOR.gris : "#ffffff"))
    .attr("stroke-width", (d) => (d.estacion_id === TEYA ? 2.5 : 1.2))
    .append("title").text((d) => `${d.lugar}. ${d.estacion} (${d.estado}): ${entero(d.negocios_2019)} negocios en 2019 y ` +
      `${entero(d.negocios_2025)} en 2025 (${conSigno(d.cambio)}${d.negocios_2019 ? `, ${pct(d.cambio_pct)}` : ""})`);

  // Rótulos: las 5 que más ganaron, Mérida Teya y las que perdieron. Posición del texto respecto al círculo.
  const LADO = { TM025: "der", TM001: "abajo", TM015: "arriba", TM009: "der", TM006: "izq", TM005: "abajo", TM030: "der" };
  const rotulados = datos.filter((d) => d.lugar <= 5 || d.estacion_id === TEYA || d.cambio < 0);
  const t = base.append("g").selectAll("text").data(rotulados).join("text")
    .attr("transform", (d) => {
      const [x, y] = proy([d.lon, d.lat]), rr = Math.max(3.5, r(Math.abs(d.cambio))) + 6;
      const lado = LADO[d.estacion_id] || "der";
      return `translate(${lado === "izq" ? x - rr : lado === "der" ? x + rr : x},${lado === "arriba" ? y - rr - 16 : lado === "abajo" ? y + rr + 14 : y - 4})`;
    })
    .attr("text-anchor", (d) => ({ izq: "end", der: "start" }[LADO[d.estacion_id] || "der"] || "middle"))
    .style("paint-order", "stroke").style("stroke", "#fff").style("stroke-width", "4px").style("stroke-linejoin", "round");
  t.append("tspan").attr("x", 0).style("font-size", "15px").style("font-weight", (d) => (d.estacion_id === TEYA ? 800 : 600))
    .style("fill", COLOR.tinta).text((d) => `${d.estacion}${d.estaciones_en_su_estado === 1 ? " *" : ""}`);
  t.append("tspan").attr("x", 0).attr("dy", "1.15em").style("font-size", "15px").style("font-weight", 800)
    .style("fill", (d) => (d.cambio < 0 ? COLOR.oroOscuro : COLOR.morado)).text((d) => conSigno(d.cambio));

  // Panel derecho: escala de tamaños, colores y lo más alto y lo más bajo del ranking.
  const p = svg.append("g").attr("transform", "translate(670,40)");
  p.append("text").style("font-size", "16px").style("font-weight", 800).text("Negocios a 5 km, 2019 a 2025");
  [[COLOR.morado, "ganó negocios"], [COLOR.oro, "perdió negocios"], ["#ffffff", "sin cambio"]].forEach(([c, txt], i) => {
    const g = p.append("g").attr("transform", `translate(10,${34 + i * 26})`);
    g.append("circle").attr("r", 8).attr("fill", c).attr("stroke", i === 2 ? COLOR.gris : "none");
    g.append("text").attr("x", 20).attr("dy", "0.35em").style("font-size", "15px").text(txt);
  });
  const ejemplo = [100, 500];
  const ge = p.append("g").attr("transform", "translate(0,130)");
  ejemplo.forEach((v, i) => {
    const x = 40 + i * 110;
    ge.append("circle").attr("cx", x).attr("cy", 40 - r(v)).attr("r", r(v)).attr("fill", "none").attr("stroke", COLOR.gris);
    ge.append("text").attr("x", x).attr("y", 62).attr("text-anchor", "middle").style("font-size", "15px")
      .style("fill", COLOR.grisTexto).text(`${entero(v)} negocios`);
  });

  const orden = datos.slice().sort((a, b) => a.lugar - b.lugar);
  const lista = [...orden.slice(0, 5), null, ...orden.filter((d) => d.cambio < 0)];
  const gl = p.append("g").attr("transform", "translate(0,240)");
  gl.append("text").style("font-size", "16px").style("font-weight", 800).text("Ranking");
  lista.forEach((d, i) => {
    const y = 28 + i * 24;
    if (!d) { gl.append("text").attr("y", y).style("font-size", "15px").style("fill", COLOR.gris).text("…"); return; }
    gl.append("text").attr("y", y).style("font-size", "15px")
      .style("font-weight", d.estacion_id === TEYA ? 800 : 500).text(`${d.lugar}. ${d.estacion}`);
    gl.append("text").attr("x", 270).attr("y", y).attr("text-anchor", "end").style("font-size", "15px").style("font-weight", 700)
      .style("fill", d.cambio < 0 ? COLOR.oroOscuro : COLOR.morado).text(conSigno(d.cambio));
  });

  const unicas = datos.filter((d) => d.estaciones_en_su_estado === 1);
  unicas.forEach((d, i) => {
    p.append("text").attr("y", 240 + 28 + lista.length * 24 + 20 + i * 20).style("font-size", "14px").style("fill", COLOR.grisTexto)
      .text(`* ${d.estacion}: única estación de ${d.estado}.`);
  });
  const nota = p.append("text").attr("y", H - 70).style("font-size", "14px").style("fill", COLOR.grisTexto);
  nota.append("tspan").attr("x", 0).text("Línea punteada: orden de la ruta,");
  nota.append("tspan").attr("x", 0).attr("dy", "1.2em").text("no el trazo real de la vía.");
};
