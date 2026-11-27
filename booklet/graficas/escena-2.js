// Escena 2 · Ranking de las 34 estaciones por negocios ganados o perdidos a 5 km, 2019 a 2025.
window.dibujarEscena2 = async function (selector = "#grafica-escena-2") {
  const { COLOR, cargarCsv, entero, conSigno, pct, fallo } = window.E8;
  let datos;
  try { datos = await cargarCsv("escena-2", ["estacion_id"]); } catch (e) { return fallo(selector, e); }

  const ABREV = { "Yucatán": "Yuc.", "Quintana Roo": "Q. Roo", "Campeche": "Camp.", "Tabasco": "Tab.", "Chiapas": "Chis." };
  const fila = 25;
  const W = 960, m = { t: 40, r: 170, b: 50, l: 300 };
  const H = m.t + m.b + fila * datos.length;
  const svg = d3.select(selector).append("svg").attr("viewBox", `0 0 ${W} ${H}`)
    .attr("role", "img").attr("aria-label", "Barras horizontales del cambio de negocios a 5 km de cada estación");

  const ext = d3.extent(datos, (d) => d.cambio);
  const x = d3.scaleLinear().domain([Math.min(ext[0], 0) * 1.1, ext[1] * 1.05]).nice().range([m.l, W - m.r]);
  const y = d3.scaleBand().domain(datos.map((d) => d.estacion_id)).range([m.t, H - m.b]).padding(0.22);

  svg.append("g").attr("class", "rejilla").attr("transform", `translate(0,${m.t})`)
    .call(d3.axisTop(x).ticks(6).tickSize(-(H - m.t - m.b)).tickFormat(""));
  svg.append("g").attr("class", "eje").attr("transform", `translate(0,${m.t})`)
    .call(d3.axisTop(x).ticks(6).tickFormat((v) => conSigno(v)));
  svg.append("line").attr("x1", x(0)).attr("x2", x(0)).attr("y1", m.t).attr("y2", H - m.b)
    .attr("stroke", COLOR.tinta).attr("stroke-width", 1.2);

  const g = svg.append("g").selectAll("g").data(datos).join("g")
    .attr("transform", (d) => `translate(0,${y(d.estacion_id)})`);

  const destacada = (d) => d.estacion_id === "TM015" || d.estacion_id === "TM001";

  g.append("text").attr("x", m.l - 12).attr("y", y.bandwidth() / 2).attr("dy", "0.35em").attr("text-anchor", "end")
    .style("font-size", "15px").style("font-weight", (d) => (destacada(d) ? 800 : 500))
    .text((d) => `${d.lugar}. ${d.estacion} (${ABREV[d.estado] || d.estado})${d.estaciones_en_su_estado === 1 ? " *" : ""}`);

  g.append("rect")
    .attr("x", (d) => x(Math.min(0, d.cambio))).attr("width", (d) => Math.abs(x(d.cambio) - x(0)))
    .attr("height", y.bandwidth()).attr("rx", 3)
    .attr("fill", (d) => (d.cambio < 0 ? COLOR.oro : destacada(d) ? COLOR.morado : COLOR.moradoMedio))
    .append("title").text((d) => `${d.estacion}, ${d.estado}: ${entero(d.negocios_2019)} negocios en 2019 y ` +
      `${entero(d.negocios_2025)} en 2025 (${conSigno(d.cambio)}, ${pct(d.cambio_pct)})`);

  g.append("text")
    .attr("x", (d) => (d.cambio < 0 ? x(0) + 8 : x(d.cambio) + 8)).attr("y", y.bandwidth() / 2).attr("dy", "0.35em")
    .style("font-size", "15px").style("font-weight", 600)
    .style("fill", (d) => (d.cambio < 0 ? COLOR.oroOscuro : COLOR.grisTexto))
    .text((d) => {
      if (d.negocios_2019 === 0 && d.negocios_2025 === 0) return "sin negocios a 5 km";
      if (d.negocios_2019 === 0) return `${conSigno(d.cambio)} (no había en 2019)`;
      return `${conSigno(d.cambio)} (${pct(d.cambio_pct)})`;
    });

  // Nota al pie: un estado con una sola estación no se compara con los demás por su total.
  const unicas = datos.filter((d) => d.estaciones_en_su_estado === 1);
  unicas.forEach((d, i) => {
    svg.append("text").attr("x", 0).attr("y", H - m.b + 30 + i * 20).style("font-size", "15px").style("fill", COLOR.grisTexto)
      .text(`* ${d.estacion} es la única estación de ${d.estado}: su cambio es todo el de ese estado.`);
  });
};
