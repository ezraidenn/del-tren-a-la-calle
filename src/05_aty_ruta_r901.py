"""Fuente 5.2: ATY, ruta R901 IE-TRAM La Plancha – Estación Tren Maya Teya.

Fuentes públicas de la Agencia de Transporte de Yucatán (ATY):
- https://transporteyucatan.org.mx/rutas/R901 : ficha de la ruta. El servidor
  responde con un PDF (mapa e información de la ruta); se guarda tal cual.
- https://transporteyucatan.org.mx/ietram : página del IE-TRAM con la tarifa y
  el horario publicado de la R901; se guarda tal cual.
- GTFS oficial del Sistema Va-y-Ven (ver src/gtfs_aty.py): paradas, trazo,
  viajes programados y tarifas de la R901.

robots.txt de transporteyucatan.org.mx: «User-agent: * / Disallow:» (sin
restricciones). Se hace una petición por recurso.

Salidas en datos/para-etl/05_solicitud_datos/5.2_aty_ruta_r901/:
- r901_paradas.csv y r901_paradas.geojson: paradas en orden por sentido.
- r901_trazo.geojson: recorrido por sentido (LineString, EPSG:4326).
- r901_viajes_gtfs.csv: viajes programados en el GTFS (salida, llegada, días).
- r901_horario_publicado.csv: horario publicado en la página del IE-TRAM.
- r901_tarifas.csv: tarifas publicadas y su correspondencia en el GTFS.

Uso: python src/05_aty_ruta_r901.py  (después de src/04_geoportal_merida.py,
que baja el GTFS).
"""

from __future__ import annotations

import html
import io
import json
import re

import pandas as pd

import comun
import gtfs_aty

TIPO = "05_solicitud_datos"
CARPETA = "5.2_aty_ruta_r901"
RUTA_ID = "901"
URL_RUTA = "https://transporteyucatan.org.mx/rutas/R901"
URL_IETRAM = "https://transporteyucatan.org.mx/ietram"

FICHA = {
    "id": "E8-05.2",
    "nombre": "ATY: ruta R901 IE-TRAM La Plancha – Teya",
    "institucion": "Agencia de Transporte de Yucatán (ATY)",
    "url_original": URL_RUTA,
    "licencia": ("Sin licencia explícita en transporteyucatan.org.mx; robots.txt sin restricciones. "
                 "Información pública de la ATY; uso académico con atribución."),
    "estado": "real",
    "acceso": "Descarga directa de páginas públicas de la ATY y del GTFS oficial del Sistema Va-y-Ven",
    "robots": "https://transporteyucatan.org.mx/robots.txt: «User-agent: * / Disallow:»",
    "gtfs": "datos/originales/04_geoportal_merida/4.3_paraderos/gtfs_va_y_ven_aty.zip",
}

DIAS = {"L-V": "lunes a viernes", "Sabado": "sábado", "Domingo": "domingo",
        "L-M-X-J": "lunes a jueves", "V-S": "viernes y sábado",
        "Viernes Feria Xmatkuil": "viernes de la Feria de Xmatkuil (servicio especial)"}


def descargar_paginas() -> tuple:
    origen = comun.carpeta_fuente(TIPO, CARPETA)
    pdf = comun.descargar(URL_RUTA, origen, "rutas_R901.pdf", FICHA,
                          nota="La URL de la ficha de ruta responde con un PDF (application/pdf).")
    pagina = comun.descargar(URL_IETRAM, origen, "ietram.html", FICHA,
                             nota="Página del IE-TRAM con tarifas y horario publicado de la R901.")
    return pdf, pagina


def a_24h(texto: str) -> str:
    """«5:30 a.m.» -> «05:30»; «12:00 a.m.» -> «00:00»."""
    m = re.match(r"\s*(\d{1,2}):(\d{2})\s*([ap])\.?\s*m\.?", texto.strip().lower())
    if not m:
        raise ValueError(f"hora no reconocida: {texto!r}")
    h, mi, ap = int(m.group(1)), int(m.group(2)), m.group(3)
    if ap == "a" and h == 12:
        h = 0
    elif ap == "p" and h < 12:
        h += 12
    return f"{h:02d}:{mi:02d}"


def horario_publicado(ruta_html) -> pd.DataFrame:
    texto = ruta_html.read_text(encoding="utf-8")
    inicio = texto.find("La ruta 901")
    fin = texto.find("La ruta 902", inicio)
    if inicio < 0 or fin < 0:
        raise ValueError("No se encontró el horario de la R901 en la página del IE-TRAM")
    tablas = pd.read_html(io.StringIO(texto[inicio:fin]))
    filas = []
    for tabla in tablas[:2]:
        salida_col, llegada_col = tabla.columns[:2]
        sentido = "La Plancha -> Teya" if "Plancha" in str(salida_col) else "Teya -> La Plancha"
        horas = [f for f in tabla.itertuples(index=False) if re.match(r"\s*\d{1,2}:\d{2}", str(f[0]))]
        for i, f in enumerate(horas, start=1):
            filas.append({"sentido": sentido, "corrida": i,
                          "salida": a_24h(str(f[0])), "llegada": a_24h(str(f[1])),
                          "texto_salida": f[0], "texto_llegada": f[1],
                          "columna_salida": salida_col, "columna_llegada": llegada_col})
    df = pd.DataFrame(filas)
    df["nota"] = "Sujeto a cambios, según la página del IE-TRAM"
    return df


def tarifas(ruta_html) -> pd.DataFrame:
    crudo = re.sub(r"<[^>]+>", " ", ruta_html.read_text(encoding="utf-8"))
    texto = html.unescape(re.sub(r"\s+", " ", crudo))
    m = re.search(r"Para la Ruta 901.*?tarjeta blanca\.", texto)
    if not m:
        raise ValueError("No se encontró el párrafo de tarifas de la R901")
    parrafo = m.group(0)
    reglas = [
        (r"\$(\d+) para turistas", "turistas", "Pago antes de abordar"),
        (r"\$(\d+) locales con tarjeta de tarifa general", "general con tarjeta Va-y-Ven", "Tarjeta de tarifa general"),
        (r"\$(\d+) para estudiantes y adultos mayores", "estudiantes y adultos mayores", "Tarjeta amarilla"),
    ]
    filas = []
    for patron, usuario, condicion in reglas:
        v = re.search(patron, parrafo)
        filas.append({"tipo_usuario": usuario, "tarifa_mxn": float(v.group(1)) if v else None,
                      "condicion": condicion, "fuente": URL_IETRAM})
    if "SIN COSTO" in parrafo.upper():
        filas.append({"tipo_usuario": "personas con discapacidad", "tarifa_mxn": 0.0,
                      "condicion": "Tarjeta blanca", "fuente": URL_IETRAM})
    df = pd.DataFrame(filas)
    df["texto_publicado"] = parrafo

    reglas_gtfs = gtfs_aty.leer("fare_rules")
    atributos = gtfs_aty.leer("fare_attributes")
    g = reglas_gtfs[reglas_gtfs.route_id == RUTA_ID].merge(atributos, on="fare_id")
    gtfs = pd.DataFrame({
        "tipo_usuario": "GTFS fare_id " + g["fare_id"],
        "tarifa_mxn": pd.to_numeric(g["price"]),
        "condicion": g["payment_method"].map({"0": "pago a bordo", "1": "pago antes de abordar"}),
        "fuente": "GTFS ATY fare_attributes.txt / fare_rules.txt",
        "texto_publicado": "",
    })
    return pd.concat([df, gtfs], ignore_index=True)


def minutos(hhmmss: str) -> int:
    h, m, s = (int(x) for x in hhmmss.split(":"))
    return h * 60 + m + round(s / 60)


def datos_gtfs() -> dict:
    rutas = gtfs_aty.leer("routes")
    ruta = rutas[rutas.route_id == RUTA_ID].iloc[0]
    viajes = gtfs_aty.leer("trips")
    viajes = viajes[viajes.route_id == RUTA_ID]
    ids = set(viajes.trip_id)
    horarios = gtfs_aty.leer_filtrado("stop_times", "trip_id", ids)
    horarios["stop_sequence"] = horarios["stop_sequence"].astype(int)
    paradas = gtfs_aty.leer("stops")
    formas = gtfs_aty.leer("shapes")
    formas = formas[formas.shape_id.isin(set(viajes.shape_id))]
    calendario = gtfs_aty.leer("calendar")
    return {"ruta": ruta, "viajes": viajes, "horarios": horarios, "paradas": paradas,
            "formas": formas, "calendario": calendario}


def construir(d: dict) -> dict:
    viajes, horarios, paradas = d["viajes"], d["horarios"], d["paradas"]
    paradas = paradas.assign(nombre=paradas["stop_name"].str.replace(r"_\d+$", "", regex=True).str.strip())
    nombres = paradas.set_index("stop_id")["nombre"]

    # Viajes programados
    ext = (horarios.sort_values("stop_sequence").groupby("trip_id")
           .agg(salida=("departure_time", "first"), llegada=("arrival_time", "last"),
                parada_inicial=("stop_id", "first"), parada_final=("stop_id", "last"),
                num_paradas=("stop_id", "size")).reset_index())
    v = viajes.merge(ext, on="trip_id")
    v["duracion_min"] = v["llegada"].map(minutos) - v["salida"].map(minutos)
    v["dias"] = v["service_id"].map(DIAS).fillna(v["service_id"])
    cal = d["calendario"].set_index("service_id")
    v["vigencia_inicio"] = v["service_id"].map(cal["start_date"])
    v["vigencia_fin"] = v["service_id"].map(cal["end_date"])
    v["sentido"] = (v["parada_inicial"].map(nombres) + " -> " + v["parada_final"].map(nombres))
    v = v[["trip_id", "service_id", "dias", "vigencia_inicio", "vigencia_fin", "direction_id", "shape_id",
           "sentido", "salida", "llegada", "duracion_min", "num_paradas"]].sort_values(
        ["service_id", "direction_id", "salida"])

    # Paradas: patrón de paradas más frecuente por sentido
    filas = []
    for direccion, grupo in v.groupby("direction_id"):
        patrones = (horarios[horarios.trip_id.isin(grupo.trip_id)].sort_values("stop_sequence")
                    .groupby("trip_id")["stop_id"].agg(tuple))
        patron = patrones.value_counts().index[0]
        viaje_ref = patrones[patrones == patron].index[0]
        ref = horarios[horarios.trip_id == viaje_ref].sort_values("stop_sequence")
        t0 = minutos(ref["departure_time"].iloc[0])
        sentido = grupo["sentido"].mode().iloc[0]
        for orden, f in enumerate(ref.itertuples(index=False), start=1):
            p = paradas[paradas.stop_id == f.stop_id].iloc[0]
            filas.append({"direction_id": direccion, "sentido": sentido, "orden": orden,
                          "stop_id": f.stop_id, "nombre": p["nombre"],
                          "lat": float(p["stop_lat"]), "lon": float(p["stop_lon"]),
                          "min_desde_salida": minutos(f.arrival_time) - t0,
                          "distancia_m": round(float(f.shape_dist_traveled or 0), 1),
                          "accesible_silla_ruedas": {"1": "si", "2": "no"}.get(p["wheelchair_boarding"], "sin dato")})
    paradas_ruta = pd.DataFrame(filas)

    # Trazo por shape
    trazos = []
    sentido_por_forma = v.groupby("shape_id")["sentido"].agg(lambda s: s.mode().iloc[0])
    for forma, g in d["formas"].groupby("shape_id"):
        g = g.assign(n=g["shape_pt_sequence"].astype(int)).sort_values("n")
        coords = [[round(float(lo), 7), round(float(la), 7)] for la, lo in zip(g.shape_pt_lat, g.shape_pt_lon)]
        dist = pd.to_numeric(g["shape_dist_traveled"], errors="coerce").max()
        trazos.append({"type": "Feature", "geometry": {"type": "LineString", "coordinates": coords},
                       "properties": {"route_id": RUTA_ID, "ruta": d["ruta"]["route_short_name"],
                                      "nombre_ruta": d["ruta"]["route_long_name"], "shape_id": forma,
                                      "sentido": sentido_por_forma.get(forma, ""),
                                      "longitud_m": None if pd.isna(dist) else round(float(dist), 1),
                                      "puntos": len(coords)}})
    return {"viajes": v, "paradas": paradas_ruta, "trazos": trazos}


def coleccion(nombre: str, rasgos: list) -> str:
    return json.dumps({"type": "FeatureCollection", "name": nombre,
                       "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
                       "features": rasgos}, ensure_ascii=False) + "\n"


def main() -> None:
    print("Fuente 5.2: ATY ruta R901")
    _, pagina = descargar_paginas()
    if not gtfs_aty.ruta_zip().exists():
        raise SystemExit("Falta el GTFS de la ATY: corre primero python src/04_geoportal_merida.py")
    destino = comun.carpeta_fuente(TIPO, CARPETA, base=comun.PARA_ETL)

    publicado = horario_publicado(pagina)
    publicado.to_csv(destino / "r901_horario_publicado.csv", index=False, encoding="utf-8")
    tarifa = tarifas(pagina)
    tarifa.to_csv(destino / "r901_tarifas.csv", index=False, encoding="utf-8")

    r = construir(datos_gtfs())
    r["viajes"].to_csv(destino / "r901_viajes_gtfs.csv", index=False, encoding="utf-8")
    r["paradas"].to_csv(destino / "r901_paradas.csv", index=False, encoding="utf-8")
    puntos = [{"type": "Feature",
               "geometry": {"type": "Point", "coordinates": [round(f.lon, 7), round(f.lat, 7)]},
               "properties": {k: getattr(f, k) for k in ("direction_id", "sentido", "orden", "stop_id", "nombre",
                                                          "min_desde_salida", "distancia_m",
                                                          "accesible_silla_ruedas")}}
              for f in r["paradas"].itertuples(index=False)]
    (destino / "r901_paradas.geojson").write_text(coleccion("r901_paradas", puntos), encoding="utf-8")
    (destino / "r901_trazo.geojson").write_text(coleccion("r901_trazo", r["trazos"]), encoding="utf-8")

    # Versión del GTFS usada, para trazabilidad
    origen = comun.carpeta_fuente(TIPO, CARPETA)
    ficha = comun.leer_procedencia(origen)
    zip_gtfs = gtfs_aty.ruta_zip()
    ficha["gtfs_usado"] = {"archivo": FICHA["gtfs"], "sha256": comun.sha256_de(zip_gtfs),
                           "feed_version": gtfs_aty.feed_info().get("feed_version", "")}
    comun.guardar_procedencia(origen, ficha)

    print(f"  horario publicado: {len(publicado)} corridas; tarifas: {len(tarifa)} filas")
    print(f"  GTFS: {len(r['viajes'])} viajes, {len(r['paradas'])} paradas en orden, {len(r['trazos'])} trazos")


if __name__ == "__main__":
    main()
