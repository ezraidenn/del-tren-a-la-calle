// Escena 2 · Las 34 estaciones sobre la península: cuántos negocios ganó o perdió cada una a 5 km, 2019 a 2025.
// En pantalla, un tren recorre la ruta y cada estación aparece cuando pasa; al elegir una estación se ve su
// detalle por anillo. Impresa, muestra el estado final con el detalle de Mérida Teya.
window.dibujarEscena2 = async function (selector = "#grafica-escena-2") {
  const { COLOR, cargarCsv, cargarJson, entero, conSigno, pct, fallo, animar } = window.E8;
  let datos, estados, anillos;
  try {
    [datos, estados, anillos] = await Promise.all([
      cargarCsv("escena-2", ["estacion_id"]), cargarJson("estados_tren_maya"), cargarCsv("escena-2-anillos", ["estacion_id"]),
    ]);
  } catch (e) { return fallo(selector, e); }
  const porEstacion = d3.group(anillos, (d) => d.estacion_id);
  const TEYA = "TM015";

  const W = 960, H = 640, mapa = [[20, 20], [640, H - 20]];
  const svg = d3.select(selector).append("svg").attr("viewBox", `0 0 ${W} ${H}`)
    .attr("role", "img").attr("aria-label", "Mapa de las 34 estaciones del Tren Maya con círculos del tamaño de los negocios ganados o perdidos");

  // --- Mapa base -------------------------------------------------------------
  const puntos = { type: "MultiPoint", coordinates: datos.map((d) => [d.lon, d.lat]) };
  const proy = d3.geoMercator().fitExtent([[60, 70], [600, H - 50]], puntos);
  const camino = d3.geoPath(proy);
  svg.append("clipPath").attr("id", "recorte-mapa-escena-2").append("rect")
    .attr("x", mapa[0][0]).attr("y", mapa[0][1]).attr("width", mapa[1][0] - mapa[0][0]).attr("height", mapa[1][1] - mapa[0][1]).attr("rx", 10);
  const base = svg.append("g").attr("clip-path", "url(#recorte-mapa-escena-2)");
  base.append("rect").attr("width", W).attr("height", H).attr("fill", "#f5f7fa");
  base.selectAll("path.estado").data(estados.features).join("path").attr("class", "estado").attr("d", camino)
    .attr("fill", "#ffffff").attr("stroke", COLOR.grisClaro).attr("stroke-width", 1.2);
  // Nombres de los estados de la península en un punto despejado de la ruta (Chiapas y Tabasco quedan en la orilla).
  const ROTULO_ESTADO = { "04": [-89.95, 19.05], "23": [-88.75, 19.95], "31": [-89.35, 20.3] };
  base.selectAll("text.estado").data(estados.features.filter((f) => ROTULO_ESTADO[f.properties.cve_ent])).join("text")
    .attr("class", "estado").attr("transform", (f) => `translate(${proy(ROTULO_ESTADO[f.properties.cve_ent])})`)
    .attr("text-anchor", "middle").style("font-size", "15px").style("font-weight", 700).style("letter-spacing", "0.12em")
    .style("fill", "#c4c9d1").text((f) => f.properties.nombre.toUpperCase());

  // Trazo esquemático: estaciones en el orden de la ruta y de Centenario de vuelta a Escárcega.
  const ruta = datos.slice().sort((a, b) => a.orden_ruta - b.orden_ruta);
  const vertices = ruta.map((d) => proy([d.lon, d.lat]));
  const escarcega = ruta.find((d) => d.estacion === "Escárcega");
  if (escarcega) vertices.push(proy([escarcega.lon, escarcega.lat]));
  const via = base.append("path").attr("d", d3.line()(vertices)).attr("fill", "none")
    .attr("stroke", COLOR.gris).attr("stroke-width", 2).attr("stroke-dasharray", "1 5").attr("stroke-linecap", "round");
  // Distancia recorrida sobre la vía hasta cada estación, para saber cuándo pasa el tren.
  const acumulada = [0];
  for (let i = 1; i < vertices.length; i++) acumulada.push(acumulada[i - 1] + Math.hypot(vertices[i][0] - vertices[i - 1][0], vertices[i][1] - vertices[i - 1][1]));
  const largoVia = acumulada[acumulada.length - 1];
  ruta.forEach((d, i) => { d.paso = acumulada[i] / largoVia; });

  // --- Estaciones ------------------------------------------------------------
  const r = d3.scaleSqrt().domain([0, d3.max(datos, (d) => Math.abs(d.cambio))]).range([0, 34]);
  const radioDe = (d) => Math.max(3.5, r(Math.abs(d.cambio)));
  const nodos = base.append("g").selectAll("g").data(datos.slice().sort((a, b) => Math.abs(b.cambio) - Math.abs(a.cambio)))
    .join("g").attr("class", "estacion").attr("transform", (d) => `translate(${proy([d.lon, d.lat])})`)
    .attr("tabindex", 0).attr("role", "button").style("cursor", "pointer").style("outline", "none")
    .attr("aria-label", (d) => `${d.estacion}: ${conSigno(d.cambio)} negocios. Ver detalle por anillo`);
  const circulos = nodos.append("circle").attr("r", radioDe)
    .attr("fill", (d) => (d.cambio > 0 ? COLOR.morado : d.cambio < 0 ? COLOR.oro : "#ffffff"))
    .attr("fill-opacity", (d) => (d.cambio === 0 ? 1 : 0.82))
    .attr("stroke", (d) => (d.cambio === 0 ? COLOR.gris : "#ffffff")).attr("stroke-width", 1.2);
  circulos.append("title").text((d) => `${d.lugar}. ${d.estacion} (${d.estado}): ${entero(d.negocios_2019)} negocios en 2019 y ` +
    `${entero(d.negocios_2025)} en 2025 (${conSigno(d.cambio)}${d.negocios_2019 ? `, ${pct(d.cambio_pct)}` : ""})`);
  // Anillo de selección, encima del círculo elegido.
  const marca = base.append("circle").attr("fill", "none").attr("stroke", COLOR.tinta).attr("stroke-width", 2.5).style("pointer-events", "none");

  // Rótulos: las 5 que más ganaron, Mérida Teya y las que perdieron.
  const LADO = { TM025: "der", TM001: "abajo", TM015: "arriba", TM009: "der", TM006: "izq", TM005: "abajo", TM030: "der" };
  const rotulados = datos.filter((d) => d.lugar <= 5 || d.estacion_id === TEYA || d.cambio < 0);
  const rotulos = base.append("g").selectAll("text").data(rotulados).join("text")
    .attr("transform", (d) => {
      const [x, y] = proy([d.lon, d.lat]), rr = radioDe(d) + 6, lado = LADO[d.estacion_id] || "der";
      return `translate(${lado === "izq" ? x - rr : lado === "der" ? x + rr : x},${lado === "arriba" ? y - rr - 16 : lado === "abajo" ? y + rr + 14 : y - 4})`;
    })
    .attr("text-anchor", (d) => ({ izq: "end", der: "start" }[LADO[d.estacion_id] || "der"] || "middle"))
    .style("pointer-events", "none").style("paint-order", "stroke").style("stroke", "#fff").style("stroke-width", "4px").style("stroke-linejoin", "round");
  rotulos.append("tspan").attr("x", 0).style("font-size", "15px").style("font-weight", (d) => (d.estacion_id === TEYA ? 800 : 600))
    .style("fill", COLOR.tinta).text((d) => `${d.estacion}${d.estaciones_en_su_estado === 1 ? " *" : ""}`);
  rotulos.append("tspan").attr("x", 0).attr("dy", "1.15em").style("font-size", "15px").style("font-weight", 800)
    .style("fill", (d) => (d.cambio < 0 ? COLOR.oroOscuro : COLOR.morado)).text((d) => conSigno(d.cambio));

  // Contador en la esquina del mapa: negocios ganados en las estaciones por las que ya pasó el tren.
  const total = d3.sum(datos, (d) => d.cambio);
  const contador = svg.append("g").attr("transform", "translate(40,52)").style("pointer-events", "none");
  const cifra = contador.append("text").style("font-size", "30px").style("font-weight", 800).style("fill", COLOR.morado)
    .text(`${conSigno(total)} negocios`);
  contador.append("text").attr("y", 22).style("font-size", "15px").style("fill", COLOR.grisTexto)
    .text(`a 5 km de las ${datos.length} estaciones, 2019 a 2025`);

  // El tren: rectángulo con la franja oro, que se mueve sobre la vía.
  const tren = base.append("g").style("pointer-events", "none").attr("opacity", 0);
  tren.append("rect").attr("x", -13).attr("y", -8).attr("width", 26).attr("height", 16).attr("rx", 5).attr("fill", COLOR.tinta);
  tren.append("rect").attr("x", -9).attr("y", -3).attr("width", 18).attr("height", 3).attr("rx", 1.5).attr("fill", COLOR.oro);

  // --- Panel derecho ---------------------------------------------------------
  const p = svg.append("g").attr("transform", "translate(670,36)");
  p.append("text").style("font-size", "16px").style("font-weight", 800).text("Negocios a 5 km, 2019 a 2025");
  [[COLOR.morado, "ganó"], [COLOR.oro, "perdió"], ["#ffffff", "igual"]].forEach(([c, txt], i) => {
    const g = p.append("g").attr("transform", `translate(${10 + i * 88},28)`);
    g.append("circle").attr("r", 8).attr("fill", c).attr("stroke", i === 2 ? COLOR.gris : "none");
    g.append("text").attr("x", 14).attr("dy", "0.35em").style("font-size", "15px").text(txt);
  });
  const ge = p.append("g").attr("transform", "translate(0,52)");
  [100, 500].forEach((v, i) => {
    const x = 30 + i * 120;
    ge.append("circle").attr("cx", x).attr("cy", 44 - r(v)).attr("r", r(v)).attr("fill", "none").attr("stroke", COLOR.gris);
    ge.append("text").attr("x", x + r(v) + 6).attr("y", 40).style("font-size", "15px").style("fill", COLOR.grisTexto).text(entero(v));
  });

  // Detalle de la estación elegida, por anillo.
  const det = p.append("g").attr("transform", "translate(0,128)");
  det.append("rect").attr("x", -10).attr("y", -22).attr("width", 290).attr("height", 176).attr("rx", 8)
    .attr("fill", "#faf7fc").attr("stroke", COLOR.moradoSuave);
  const detTitulo = det.append("text").style("font-size", "16px").style("font-weight", 800).style("fill", COLOR.morado);
  const detSub = det.append("text").attr("y", 20).style("font-size", "14px").style("fill", COLOR.grisTexto);
  const detFilas = det.append("g").attr("transform", "translate(0,44)");
  det.append("text").attr("y", 128).style("font-size", "13px").style("fill", COLOR.grisTexto).text("Oro: 2019 · morado: 2025");
  det.append("text").attr("class", "solo-pantalla").attr("y", 140 + 3).style("font-size", "13px")
    .style("fill", COLOR.morado).style("font-weight", 600).text("Toca otra estación para ver su detalle");

  function mostrar(est) {
    const filas = porEstacion.get(est.estacion_id) || [];
    marca.attr("transform", `translate(${proy([est.lon, est.lat])})`).attr("r", radioDe(est) + 3);
    detTitulo.text(est.estacion);
    detSub.text(`${est.estado} · lugar ${est.lugar} de ${datos.length} · ${conSigno(est.cambio)} negocios`);
    const ancho = d3.scaleLinear().domain([0, d3.max(filas, (d) => Math.max(d.negocios_2019, d.negocios_2025)) || 1]).range([0, 120]);
    const f = detFilas.selectAll("g.fila").data(filas, (d) => d.anillo).join((e) => {
      const g = e.append("g").attr("class", "fila");
      g.append("text").attr("class", "km").attr("y", 12).style("font-size", "14px");
      g.append("rect").attr("class", "a19").attr("x", 58).attr("y", 0).attr("height", 7).attr("rx", 2).attr("fill", COLOR.oro);
      g.append("rect").attr("class", "a25").attr("x", 58).attr("y", 9).attr("height", 7).attr("rx", 2).attr("fill", COLOR.morado);
      g.append("text").attr("class", "val").attr("x", 270).attr("y", 12).attr("text-anchor", "end")
        .style("font-size", "14px").style("font-weight", 700);
      return g;
    }).attr("transform", (d, i) => `translate(0,${i * 28})`);
    f.select("text.km").text((d) => d.anillo);
    f.select("rect.a19").attr("width", (d) => ancho(d.negocios_2019));
    f.select("rect.a25").attr("width", (d) => ancho(d.negocios_2025));
    f.select("text.val").style("fill", (d) => (d.cambio < 0 ? COLOR.oroOscuro : COLOR.morado))
      .text((d) => (d.negocios_2019 || d.negocios_2025 ? conSigno(d.cambio) : "sin negocios"));
  }
  nodos.on("click", (e, d) => mostrar(d))
    .on("keydown", (e, d) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); mostrar(d); } });
  mostrar(datos.find((d) => d.estacion_id === TEYA) || datos[0]);

  // Ranking corto.
  const orden = datos.slice().sort((a, b) => a.lugar - b.lugar);
  const lista = [...orden.slice(0, 5), null, ...orden.filter((d) => d.cambio < 0)];
  const gl = p.append("g").attr("transform", "translate(0,330)");
  gl.append("text").style("font-size", "16px").style("font-weight", 800).text("Ranking");
  lista.forEach((d, i) => {
    const y = 26 + i * 22;
    if (!d) { gl.append("text").attr("y", y).style("font-size", "15px").style("fill", COLOR.gris).text("…"); return; }
    gl.append("text").attr("y", y).style("font-size", "15px").style("font-weight", d.estacion_id === TEYA ? 800 : 500)
      .text(`${d.lugar}. ${d.estacion}`);
    gl.append("text").attr("x", 270).attr("y", y).attr("text-anchor", "end").style("font-size", "15px").style("font-weight", 700)
      .style("fill", d.cambio < 0 ? COLOR.oroOscuro : COLOR.morado).text(conSigno(d.cambio));
  });
  const pie = p.append("text").attr("y", 330 + 26 + lista.length * 22 + 14).style("font-size", "14px").style("fill", COLOR.grisTexto);
  datos.filter((d) => d.estaciones_en_su_estado === 1).forEach((d, i) => {
    pie.append("tspan").attr("x", 0).attr("dy", i ? "1.2em" : 0).text(`* ${d.estacion}: única estación de ${d.estado}.`);
  });
  pie.append("tspan").attr("x", 0).attr("dy", "1.3em").text("Punteado: orden de la ruta, no la vía real.");

  // --- Animación: el tren recorre la península ------------------------------
  const DURACION = 7000;
  animar(svg.node(), {
    inicio() {
      circulos.attr("transform", "scale(0)");
      rotulos.attr("opacity", 0);
      marca.attr("opacity", 0);
      cifra.text("0 negocios");
    },
    correr() {
      const nodoVia = via.node(), largo = nodoVia.getTotalLength();
      tren.attr("opacity", 1);
      tren.transition().duration(DURACION).ease(d3.easeSinInOut)
        .attrTween("transform", () => (t) => { const q = nodoVia.getPointAtLength(t * largo); return `translate(${q.x},${q.y})`; })
        .tween("contador", () => (t) => {
          const suma = d3.sum(ruta.filter((d) => d.paso <= t + 1e-9), (d) => d.cambio);
          cifra.text(`${conSigno(suma)} negocios`);
        })
        .on("end", () => { tren.transition().duration(400).attr("opacity", 0); cifra.text(`${conSigno(total)} negocios`); });
      // Cada estación aparece con un pequeño rebote cuando pasa el tren (la curva de tiempo es la misma del tren).
      const tiempo = (d) => {
        // Inversa aproximada de easeSinInOut: momento en que el tren llega a la fracción d.paso.
        const s = Math.min(1, Math.max(0, d.paso));
        return (Math.acos(1 - 2 * s) / Math.PI) * DURACION;
      };
      circulos.transition().delay(tiempo).duration(650).ease(d3.easeBackOut.overshoot(1.6)).attr("transform", "scale(1)");
      rotulos.transition().delay((d) => tiempo(d) + 300).duration(400).attr("opacity", 1);
      marca.transition().delay(DURACION).duration(400).attr("opacity", 1);
    },
    fin() {
      circulos.attr("transform", null);
      rotulos.attr("opacity", 1);
      marca.attr("opacity", 1);
      tren.attr("opacity", 0);
      cifra.text(`${conSigno(total)} negocios`);
    },
  });
};
