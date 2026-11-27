// Escena 1 · Negocios por anillo de distancia a las 34 estaciones, 2019 contra 2025.
window.dibujarEscena1 = async function (selector = "#grafica-escena-1") {
  const { COLOR, cargarCsv, entero, conSigno, pct, fallo } = window.E8;
  let datos;
  try { datos = await cargarCsv("escena-1"); } catch (e) { return fallo(selector, e); }

  const W = 960, H = 460, m = { t: 56, r: 24, b: 84, l: 84 };
  const svg = d3.select(selector).append("svg").attr("viewBox", `0 0 ${W} ${H}`)
    .attr("role", "img").attr("aria-label", "Barras agrupadas de negocios por anillo de distancia en 2019 y 2025");

  const anios = [
    { clave: "negocios_2019", etiqueta: "2019", color: COLOR.oro },
    { clave: "negocios_2025", etiqueta: "2025", color: COLOR.morado },
  ];
  const x0 = d3.scaleBand().domain(datos.map((d) => d.anillo)).range([m.l, W - m.r]).paddingInner(0.28).paddingOuter(0.12);
  const x1 = d3.scaleBand().domain(anios.map((a) => a.clave)).range([0, x0.bandwidth()]).padding(0.08);
  const y = d3.scaleLinear().domain([0, d3.max(datos, (d) => d.negocios_2025) * 1.12]).nice().range([H - m.b, m.t]);

  svg.append("g").attr("class", "rejilla").attr("transform", `translate(${m.l},0)`)
    .call(d3.axisLeft(y).ticks(5).tickSize(-(W - m.l - m.r)).tickFormat(""));
  svg.append("g").attr("class", "eje").attr("transform", `translate(${m.l},0)`)
    .call(d3.axisLeft(y).ticks(5).tickFormat(entero));
  svg.append("g").attr("class", "eje").attr("transform", `translate(0,${H - m.b})`)
    .call(d3.axisBottom(x0).tickFormat((a) => `De ${a.replace("-", " a ")} de la estación`).tickSizeOuter(0))
    .selectAll("text").style("font-size", "16px").style("fill", COLOR.tinta).attr("dy", "1.2em");

  const grupo = svg.append("g").selectAll("g").data(datos).join("g")
    .attr("transform", (d) => `translate(${x0(d.anillo)},0)`);

  grupo.selectAll("rect").data((d) => anios.map((a) => ({ ...a, valor: d[a.clave], anillo: d.anillo }))).join("rect")
    .attr("x", (d) => x1(d.clave)).attr("width", x1.bandwidth())
    .attr("y", (d) => y(d.valor)).attr("height", (d) => y(0) - y(d.valor))
    .attr("rx", 4).attr("fill", (d) => d.color)
    .append("title").text((d) => `${d.anillo}, ${d.etiqueta}: ${entero(d.valor)} negocios`);

  grupo.selectAll("text.valor").data((d) => anios.map((a) => ({ ...a, valor: d[a.clave] }))).join("text")
    .attr("class", "valor").attr("x", (d) => x1(d.clave) + x1.bandwidth() / 2).attr("y", (d) => y(d.valor) - 8)
    .attr("text-anchor", "middle").style("font-size", "15px").style("font-weight", 600)
    .style("fill", (d) => (d.clave === "negocios_2025" ? COLOR.morado : COLOR.oroOscuro))
    .text((d) => entero(d.valor));

  // Cambio de cada anillo, arriba del grupo.
  grupo.append("text").attr("x", x0.bandwidth() / 2).attr("y", m.t - 22).attr("text-anchor", "middle")
    .style("font-size", "17px").style("font-weight", 800).style("fill", COLOR.oroOscuro)
    .text((d) => `${conSigno(d.cambio)} (${pct(d.cambio_pct)})`);

  // Leyenda dentro del SVG para que viaje con la imagen impresa.
  const ley = svg.append("g").attr("transform", `translate(${m.l},${H - 16})`);
  anios.forEach((a, i) => {
    const g = ley.append("g").attr("transform", `translate(${i * 110},0)`);
    g.append("rect").attr("y", -13).attr("width", 16).attr("height", 16).attr("rx", 3).attr("fill", a.color);
    g.append("text").attr("x", 22).style("font-size", "15px").text(a.etiqueta);
  });
  ley.append("text").attr("x", 230).style("font-size", "15px").style("fill", COLOR.oroOscuro).style("font-weight", 700)
    .text("Arriba: negocios ganados de 2019 a 2025");
};
