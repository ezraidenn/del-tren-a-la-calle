// Escena 3 · Pasajeros por mes del Tren Maya, 2025 contra 2026.
window.dibujarEscena3 = async function (selector = "#grafica-escena-3") {
  const { COLOR, cargarCsv, entero, pct, MESES, fallo } = window.E8;
  let datos;
  try { datos = await cargarCsv("escena-3", ["mes"]); } catch (e) { return fallo(selector, e); }
  datos.forEach((d) => { d.m = +d.mes.slice(5, 7); });

  const series = d3.groups(datos, (d) => d.anio).map(([anio, valores]) => ({ anio, valores }));
  // Morado: 2026, lo que se analiza. Oro: 2025, contra qué se compara.
  const colorDe = (anio) => (anio === 2026 ? COLOR.morado : COLOR.oro);

  const W = 960, H = 460, m = { t: 30, r: 90, b: 50, l: 90 };
  const svg = d3.select(selector).append("svg").attr("viewBox", `0 0 ${W} ${H}`)
    .attr("role", "img").attr("aria-label", "Líneas de pasajeros mensuales del Tren Maya en 2025 y 2026");

  const x = d3.scalePoint().domain(d3.range(1, 13)).range([m.l, W - m.r]).padding(0.3);
  const y = d3.scaleLinear().domain([0, d3.max(datos, (d) => d.pasajeros) * 1.1]).nice().range([H - m.b, m.t]);

  svg.append("g").attr("class", "rejilla").attr("transform", `translate(${m.l},0)`)
    .call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat(""));
  svg.append("g").attr("class", "eje").attr("transform", `translate(${m.l},0)`)
    .call(d3.axisLeft(y).ticks(5).tickFormat((v) => (v === 0 ? "0" : `${entero(v / 1000)} mil`)));
  svg.append("g").attr("class", "eje").attr("transform", `translate(0,${H - m.b})`)
    .call(d3.axisBottom(x).tickFormat((v) => MESES[v - 1]).tickSizeOuter(0));

  // Meses de 2026 con caída anual: banda suave detrás de las líneas.
  const caidas = datos.filter((d) => d.anio === 2026 && d.variacion_anual_pct < -10);
  if (caidas.length) {
    const paso = x.step();
    const x0 = x(d3.min(caidas, (d) => d.m)) - paso / 2, x1 = x(d3.max(caidas, (d) => d.m)) + paso / 2;
    svg.insert("rect", ":first-child").attr("x", x0).attr("width", x1 - x0).attr("y", m.t).attr("height", H - m.b - m.t)
      .attr("fill", "#f3f4f6");
    svg.append("text").attr("x", (x0 + x1) / 2).attr("y", m.t + 20).attr("text-anchor", "middle")
      .style("font-size", "15px").style("font-weight", 700).style("fill", COLOR.oroOscuro)
      .text("2026 por debajo de 2025");
  }

  const linea = d3.line().x((d) => x(d.m)).y((d) => y(d.pasajeros));
  const g = svg.append("g").selectAll("g").data(series).join("g");
  g.append("path").attr("d", (s) => linea(s.valores)).attr("fill", "none")
    .attr("stroke", (s) => colorDe(s.anio)).attr("stroke-width", (s) => (s.anio === 2026 ? 3.5 : 2.5));
  g.selectAll("circle").data((s) => s.valores).join("circle")
    .attr("cx", (d) => x(d.m)).attr("cy", (d) => y(d.pasajeros)).attr("r", 5)
    .attr("fill", (d) => colorDe(d.anio)).attr("stroke", "#fff").attr("stroke-width", 1.5)
    .append("title").text((d) => `${MESES[d.m - 1]} ${d.anio}: ${entero(d.pasajeros)} pasajeros` +
      (d.variacion_anual_pct != null ? ` (${pct(d.variacion_anual_pct)} contra ${d.anio - 1})` : ""));

  // Etiqueta de cada serie al final de su línea.
  g.append("text").attr("x", (s) => x(s.valores[s.valores.length - 1].m) + 12)
    .attr("y", (s) => y(s.valores[s.valores.length - 1].pasajeros) - (s.anio === 2026 ? 0 : 0)).attr("dy", (s) => (s.anio === 2026 ? "-0.4em" : "0.35em"))
    .style("font-size", "17px").style("font-weight", 800).style("fill", (s) => (s.anio === 2026 ? COLOR.morado : COLOR.oroOscuro))
    .text((s) => s.anio);

  // Variación anual de los meses con caída, entre el punto de 2026 y el de 2025.
  svg.append("g").selectAll("text").data(caidas).join("text")
    // El último mes va debajo del punto: ahí las dos líneas casi se tocan.
    .attr("x", (d) => x(d.m)).attr("y", (d) => y(d.pasajeros) + (d.m === d3.max(caidas, (c) => c.m) ? 30 : -14))
    .attr("text-anchor", "middle")
    .style("paint-order", "stroke").style("stroke", "#fff").style("stroke-width", "4px")
    .style("font-size", "15px").style("font-weight", 700).style("fill", COLOR.oroOscuro)
    .text((d) => pct(d.variacion_anual_pct, 0));
};
