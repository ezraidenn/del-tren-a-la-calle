// Escena 1 · Anillos de 0 a 1, 1 a 3 y 3 a 5 km alrededor de las 34 estaciones: negocios ganados de 2019 a 2025.
window.dibujarEscena1 = async function (selector = "#grafica-escena-1") {
  const { COLOR, cargarCsv, entero, conSigno, pct, fallo } = window.E8;
  let datos;
  try { datos = await cargarCsv("escena-1"); } catch (e) { return fallo(selector, e); }
  datos.forEach((d) => {
    const [a, b] = d.anillo.replace(" km", "").split("-").map(Number);
    d.min = a; d.max = b;
  });

  const W = 960, H = 450, cx = 250, cy = 225;
  const radio = d3.scaleLinear().domain([0, d3.max(datos, (d) => d.max)]).range([0, 215]);
  // Intensidad del morado según cuánto creció cada anillo (%).
  const tono = d3.scaleLinear().domain(d3.extent(datos, (d) => d.cambio_pct)).range([0.3, 0.92]);
  const svg = d3.select(selector).append("svg").attr("viewBox", `0 0 ${W} ${H}`)
    .attr("role", "img").attr("aria-label", "Tres anillos concéntricos alrededor de una estación con los negocios ganados en cada uno");

  const arco = d3.arc().startAngle(0).endAngle(2 * Math.PI);
  const anillos = svg.append("g").attr("transform", `translate(${cx},${cy})`);
  anillos.selectAll("path").data(datos.slice().reverse()).join("path")
    .attr("d", (d) => arco({ innerRadius: radio(d.min), outerRadius: radio(d.max) }))
    .attr("fill", COLOR.morado).attr("fill-opacity", (d) => tono(d.cambio_pct))
    .attr("stroke", "#fff").attr("stroke-width", 2)
    .append("title").text((d) => `${d.anillo}: ${entero(d.negocios_2019)} negocios en 2019 y ${entero(d.negocios_2025)} en 2025`);

  // La estación al centro y las distancias sobre el eje horizontal.
  anillos.append("rect").attr("x", -16).attr("y", -9).attr("width", 32).attr("height", 18).attr("rx", 5)
    .attr("fill", COLOR.tinta);
  anillos.append("rect").attr("x", -11).attr("y", -4).attr("width", 22).attr("height", 3).attr("rx", 1.5).attr("fill", COLOR.oro);
  anillos.append("text").attr("y", 30).attr("text-anchor", "middle").style("font-size", "15px").style("font-weight", 700)
    .style("paint-order", "stroke").style("stroke", "#fff").style("stroke-width", "4px").text("estación");
  const kms = [...new Set(datos.map((d) => d.max))];
  anillos.selectAll("text.km").data(kms).join("text").attr("class", "km")
    .attr("x", (k) => radio(k) * Math.cos(Math.PI / 4)).attr("y", (k) => radio(k) * Math.sin(Math.PI / 4) + 18)
    .attr("text-anchor", "start")
    .style("font-size", "15px").style("fill", COLOR.tinta).style("font-weight", 600)
    .style("paint-order", "stroke").style("stroke", "#fff").style("stroke-width", "4px").text((k) => `${k} km`);

  // Ganancia escrita dentro de cada anillo, arriba del centro.
  anillos.selectAll("text.cambio").data(datos).join("text").attr("class", "cambio")
    .attr("y", (d) => -(d.min === 0 ? radio(d.max) * 0.45 : (radio(d.min) + radio(d.max)) / 2))
    .attr("text-anchor", "middle").attr("dy", "0.35em")
    .style("font-size", (d) => (d.min === 0 ? "15px" : "22px")).style("font-weight", 800)
    .style("fill", (d) => (tono(d.cambio_pct) > 0.5 ? "#ffffff" : COLOR.morado))
    .text((d) => conSigno(d.cambio));

  // Panel derecho: cada anillo con 2019 (oro, comparación) y 2025 (morado).
  const p = svg.append("g").attr("transform", "translate(560,50)");
  const ancho = d3.scaleLinear().domain([0, d3.max(datos, (d) => d.negocios_2025)]).range([0, 250]);
  datos.forEach((d, i) => {
    const g = p.append("g").attr("transform", `translate(0,${i * 125})`);
    g.append("text").style("font-size", "17px").style("font-weight", 800).text(`De ${d.min} a ${d.max} km`);
    g.append("text").attr("x", 340).attr("text-anchor", "end").style("font-size", "17px").style("font-weight", 800)
      .style("fill", COLOR.morado).text(pct(d.cambio_pct));
    [["2019", d.negocios_2019, COLOR.oro, COLOR.oroOscuro], ["2025", d.negocios_2025, COLOR.morado, COLOR.morado]]
      .forEach(([anio, v, c, ct], j) => {
        const y = 16 + j * 34;
        g.append("text").attr("y", y + 17).style("font-size", "15px").style("fill", COLOR.grisTexto).text(anio);
        g.append("rect").attr("x", 44).attr("y", y).attr("width", ancho(v)).attr("height", 24).attr("rx", 4).attr("fill", c);
        g.append("text").attr("x", 44 + ancho(v) + 8).attr("y", y + 17).style("font-size", "15px").style("font-weight", 700)
          .style("fill", ct).text(entero(v));
      });
  });
};
