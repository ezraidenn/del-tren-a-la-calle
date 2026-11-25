"""Subtema 4: capas del Geoportal de Mérida.

El Geoportal (geoportal.merida.gob.mx) responde a cualquier descarga
automatizada con un desafío antibots (redirección 302 a una página de
verificación con captcha). No se rodea: el script solo registra la respuesta
y deja en cada carpeta un PENDIENTE.md con los pasos para exportar la capa a
mano desde el navegador.

- 4.1 Unidades deportivas: sustituto público mientras se exporta la capa.
  Se usan las instalaciones deportivas de OpenStreetMap dentro del límite
  municipal de Mérida (API Overpass).
- 4.2 Circuito Enlace: sustituto público mientras se exporta la capa. El
  recorrido no se publica fuera del Geoportal (ni en OpenStreetMap ni en la
  prensa); se usa la infraestructura ciclista de OpenStreetMap en Mérida.
- 4.3 Paraderos: sustituto público. Se usan las paradas del GTFS oficial de la
  Agencia de Transporte de Yucatán (Sistema Va-y-Ven), que cubre el
  transporte público de Mérida y su zona metropolitana.

Salidas en datos/para-etl/04_geoportal_merida/:
- 4.1_unidades_deportivas/unidades_deportivas_osm.csv y .geojson: una fila por
  instalación con lat/lon (EPSG:4326), tipo, deporte y acceso.
- 4.2_circuito_enlace/infraestructura_ciclista_osm.csv y .geojson: ciclovías y
  carriles (líneas, con longitud) y estacionamientos de bicicletas (puntos).
- 4.3_paraderos/paraderos_aty.csv: una fila por parada con lat/lon (EPSG:4326) y rutas.
- 4.3_paraderos/paraderos_aty.geojson: los mismos puntos en GeoJSON (EPSG:4326).

Uso: python src/04_geoportal_merida.py
"""

from __future__ import annotations

import json
import time
from urllib.parse import urlencode

import numpy as np
import pandas as pd
import requests

import comun
import gtfs_aty

TIPO = "04_geoportal_merida"

CAPAS = {
    "4.1_unidades_deportivas": {
        "id": "E8-04.1", "nombre": "Unidades deportivas",
        "institucion": "Ayuntamiento de Mérida",
        "url_original": "https://geoportal.merida.gob.mx/unidadesdeportivas",
    },
    "4.2_circuito_enlace": {
        "id": "E8-04.2", "nombre": "Circuito Enlace (transporte gratuito del Centro)",
        "institucion": "Ayuntamiento de Mérida",
        "url_original": "https://geoportal.merida.gob.mx/circuitoenlace",
    },
    "4.3_paraderos": {
        "id": "E8-04.3", "nombre": "Paraderos de transporte público",
        "institucion": "Ayuntamiento de Mérida (capa original); Agencia de Transporte de Yucatán (sustituto)",
        "url_original": "https://geoportal.merida.gob.mx/paraderos",
    },
}

LICENCIA_PENDIENTE = "Por confirmar en el Geoportal al exportar la capa"
ROBOTS = ("https://geoportal.merida.gob.mx/robots.txt: «User-agent: * / Disallow: /geoapijs / "
          "Disallow: /vistas / Disallow: /embed/»")
LICENCIA_GTFS = ("Sin licencia explícita. Publicado por la ATY como GTFS para reutilización "
                 "en aplicaciones de terceros; uso académico con atribución a la ATY.")
LICENCIA_OSM = "ODbL 1.0 (© colaboradores de OpenStreetMap); las bases derivadas se comparten con la misma licencia"
OSM_ARCHIVO = "osm_instalaciones_deportivas.json"
OSM_CONSULTA = ('[out:json][timeout:120];area(3605961522)->.m;'
                '(nwr["leisure"~"^(sports_centre|stadium|pitch|sports_hall|track)$"](area.m););out center tags;')
OSM_CICLISTA_ARCHIVO = "osm_infraestructura_ciclista.json"
OSM_CICLISTA_CONSULTA = (
    '[out:json][timeout:180];area(3605961522)->.m;('
    'way["highway"="cycleway"](area.m);'
    'way["cycleway"~"^(lane|track|shared_lane|share_busway)$"](area.m);'
    'way["cycleway:both"~"^(lane|track|shared_lane)$"](area.m);'
    'way["cycleway:left"~"^(lane|track|shared_lane)$"](area.m);'
    'way["cycleway:right"~"^(lane|track|shared_lane)$"](area.m);'
    'way["highway"="path"]["bicycle"="designated"](area.m);'
    'nwr["amenity"="bicycle_parking"](area.m);nwr["amenity"="bicycle_rental"](area.m););out geom tags;')
OVERPASS = ["https://maps.mail.ru/osm/tools/overpass/api/interpreter",
            "https://overpass-api.de/api/interpreter"]


def comprobar_acceso(url: str) -> dict:
    """Una sola petición sin seguir redirecciones, para dejar constancia."""
    try:
        r = comun.SESION.get(url, allow_redirects=False, timeout=30)
        destino = r.headers.get("Location", "")
        antibots = "perfdrive" in destino or "__uzdbm" in r.text[:4000]
        if antibots:
            resultado = "redirige a la verificación antibots (validate.perfdrive.com)"
        elif r.status_code == 200:
            resultado = ("responde 200 de forma intermitente; las demás peticiones redirigen a la "
                         "verificación antibots y robots.txt prohíbe /geoapijs, /vistas y /embed/")
        else:
            resultado = f"HTTP {r.status_code}"
        return {"fecha_utc": comun.ahora_utc(), "http": r.status_code, "antibots": antibots,
                "resultado": resultado}
    except requests.RequestException as e:
        return {"fecha_utc": comun.ahora_utc(), "http": None, "antibots": None, "resultado": str(e)[:200]}


EXT_MANUALES = {".kml", ".geojson", ".json"}
SALIDA_MANUAL = {"4.1_unidades_deportivas": "unidades_deportivas",
                 "4.2_circuito_enlace": "circuito_enlace",
                 "4.3_paraderos": "paraderos_geoportal"}


def exportaciones_manuales(carpeta: str) -> list:
    origen = comun.carpeta_fuente(TIPO, carpeta)
    return sorted(p for p in origen.iterdir()
                  if p.suffix.lower() in EXT_MANUALES and p.name != "procedencia.json"
                  and not p.name.startswith("osm_"))


def registrar_manual(carpeta: str, ruta) -> None:
    """Registra en procedencia.json una capa exportada a mano desde el Geoportal."""
    origen = ruta.parent
    previos = {a["archivo"]: a for a in comun.leer_procedencia(origen).get("archivos", [])}
    sha = comun.sha256_de(ruta)
    if ruta.name in previos and previos[ruta.name]["sha256"] == sha:
        return
    comun.registrar(origen, {}, {
        "archivo": ruta.name,
        "url": CAPAS[carpeta]["url_original"],
        "descargado_utc": comun.ahora_utc(),
        "bytes": ruta.stat().st_size,
        "sha256": sha,
        "content_type": "application/vnd.google-earth.kml+xml" if ruta.suffix.lower() == ".kml"
        else "application/geo+json",
        "nota": "Exportado a mano desde el navegador según PENDIENTE.md; la fecha es la de registro.",
    })


def _coords_kml(texto: str) -> list[list[float]]:
    puntos = []
    for tramo in texto.split():
        partes = tramo.split(",")
        if len(partes) >= 2:
            puntos.append([float(partes[0]), float(partes[1])])
    return puntos


def leer_kml(ruta) -> list[dict]:
    from lxml import etree
    arbol = etree.parse(str(ruta))
    rasgos = []
    for pm in arbol.iter("{*}Placemark"):
        props = {"nombre": (pm.findtext("{*}name") or "").strip()}
        for dato in pm.iter("{*}Data", "{*}SimpleData"):
            clave = dato.get("name")
            valor = dato.findtext("{*}value") if dato.tag.endswith("}Data") else dato.text
            if clave:
                props[clave] = (valor or "").strip()
        geoms = []
        for g in pm.iter("{*}Point", "{*}LineString", "{*}Polygon"):
            if g.tag.endswith("Point"):
                geoms.append({"type": "Point", "coordinates": _coords_kml(g.findtext(".//{*}coordinates"))[0]})
            elif g.tag.endswith("LineString"):
                geoms.append({"type": "LineString", "coordinates": _coords_kml(g.findtext(".//{*}coordinates"))})
            else:
                anillo = g.find(".//{*}outerBoundaryIs//{*}coordinates")
                geoms.append({"type": "Polygon", "coordinates": [_coords_kml(anillo.text)]})
        if len(geoms) == 1:
            geom = geoms[0]
        elif geoms:
            geom = {"type": "GeometryCollection", "geometries": geoms}
        else:
            continue
        rasgos.append({"type": "Feature", "geometry": geom, "properties": props})
    return rasgos


def _primer_par(geom: dict) -> list[float]:
    c = geom.get("coordinates") or geom["geometries"][0]["coordinates"]
    while isinstance(c[0], list):
        c = c[0]
    return c


def convertir_manual(carpeta: str, rutas: list) -> None:
    """Pasa las capas exportadas a mano a GeoJSON EPSG:4326 (y CSV si son puntos)."""
    rasgos = []
    for ruta in rutas:
        if ruta.suffix.lower() == ".kml":
            nuevos = leer_kml(ruta)
        else:
            nuevos = json.loads(ruta.read_text(encoding="utf-8-sig"))["features"]
        for r in nuevos:
            lon, lat = _primer_par(r["geometry"])[:2]
            if not (-91.5 < lon < -87.5 and 19.5 < lat < 22.0):
                raise ValueError(f"{ruta.name}: coordenadas fuera de Yucatán ({lon}, {lat}). "
                                 "Exporta la capa en WGS84 (EPSG:4326) o en KML.")
            r.setdefault("properties", {})["archivo_origen"] = ruta.name
        rasgos.extend(nuevos)
    destino = comun.carpeta_fuente(TIPO, carpeta, base=comun.PARA_ETL)
    nombre = SALIDA_MANUAL[carpeta]
    (destino / f"{nombre}.geojson").write_text(json.dumps(
        {"type": "FeatureCollection", "name": nombre,
         "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
         "features": rasgos}, ensure_ascii=False) + "\n", encoding="utf-8")
    if rasgos and all(r["geometry"]["type"] == "Point" for r in rasgos):
        filas = [{**r["properties"], "lon": r["geometry"]["coordinates"][0],
                  "lat": r["geometry"]["coordinates"][1]} for r in rasgos]
        pd.DataFrame(filas).to_csv(destino / f"{nombre}.csv", index=False, encoding="utf-8")
    print(f"  {carpeta}: {len(rasgos):,} elementos exportados a mano convertidos")


def capas_pendientes() -> None:
    for carpeta in ("4.1_unidades_deportivas", "4.2_circuito_enlace"):
        destino = comun.carpeta_fuente(TIPO, carpeta)
        manuales = exportaciones_manuales(carpeta)
        ficha = comun.leer_procedencia(destino)
        ficha.update(CAPAS[carpeta])
        con_sustituto = True  # 4.1 y 4.2 tienen sustituto de OpenStreetMap
        ficha.update({
            "licencia": LICENCIA_OSM if con_sustituto and not manuales else LICENCIA_PENDIENTE,
            "estado": "real" if manuales else "sustituto" if con_sustituto else "pendiente",
            "acceso": "Exportación manual desde el navegador; ver PENDIENTE.md",
            "robots": ROBOTS,
            "comprobacion_acceso": comprobar_acceso(CAPAS[carpeta]["url_original"]),
        })
        ficha.setdefault("archivos", [])
        comun.guardar_procedencia(destino, ficha)
        print(f"  {carpeta}: {ficha['comprobacion_acceso']['resultado']}")
        for ruta in manuales:
            registrar_manual(carpeta, ruta)
        if manuales:
            convertir_manual(carpeta, manuales)


def escribir_geojson(df: pd.DataFrame, ruta, propiedades: list[str]) -> None:
    rasgos = []
    for _, f in df.iterrows():
        rasgos.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(float(f["lon"]), 7), round(float(f["lat"]), 7)]},
            "properties": {c: (None if pd.isna(f[c]) else f[c]) for c in propiedades},
        })
    ruta.write_text(json.dumps({"type": "FeatureCollection", "name": ruta.stem,
                                "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
                                "features": rasgos}, ensure_ascii=False) + "\n", encoding="utf-8")


def paraderos() -> None:
    carpeta = "4.3_paraderos"
    origen = comun.carpeta_fuente(TIPO, carpeta)
    ficha = {**CAPAS[carpeta],
             "licencia": LICENCIA_GTFS,
             "estado": "sustituto",
             "sustituto": "Paradas (stops.txt) del GTFS oficial del Sistema Va-y-Ven, Agencia de Transporte de Yucatán",
             "url_sustituto": gtfs_aty.URL_PRODUCTOR,
             "robots": ROBOTS,
             "comprobacion_acceso": comprobar_acceso(CAPAS[carpeta]["url_original"])}
    gtfs_aty.asegurar_zip(ficha)
    comun.registrar(origen, ficha, next(a for a in comun.leer_procedencia(origen)["archivos"]
                                        if a["archivo"] == gtfs_aty.NOMBRE_ZIP))
    info = gtfs_aty.feed_info()

    paradas = gtfs_aty.leer("stops")
    rutas = gtfs_aty.leer("routes", usecols=["route_id", "route_short_name", "route_long_name"])
    viajes = gtfs_aty.leer("trips", usecols=["trip_id", "route_id"])
    horarios = gtfs_aty.leer("stop_times", usecols=["trip_id", "stop_id"])

    pares = (horarios.drop_duplicates().merge(viajes, on="trip_id")
             .merge(rutas, on="route_id")[["stop_id", "route_short_name"]].drop_duplicates())
    por_parada = (pares.groupby("stop_id")["route_short_name"]
                  .agg(lambda s: ";".join(sorted(s, key=lambda x: (len(x), x))))
                  .rename("rutas").reset_index())
    por_parada["num_rutas"] = por_parada["rutas"].str.count(";") + 1

    salida = paradas.merge(por_parada, on="stop_id", how="left")
    salida["num_rutas"] = salida["num_rutas"].fillna(0).astype(int)
    # El nombre de parada de la ATY termina con «_<stop_id>»; se separa.
    salida["nombre"] = salida["stop_name"].str.replace(r"_\d+$", "", regex=True).str.strip()
    salida["lat"] = pd.to_numeric(salida["stop_lat"])
    salida["lon"] = pd.to_numeric(salida["stop_lon"])
    salida["accesible_silla_ruedas"] = salida["wheelchair_boarding"].map({"1": "si", "2": "no"}).fillna("sin dato")
    salida["fuente"] = "ATY GTFS Va-y-Ven"
    salida["version_gtfs"] = info.get("feed_version", "")
    salida = salida[["stop_id", "nombre", "lat", "lon", "accesible_silla_ruedas", "num_rutas", "rutas",
                     "fuente", "version_gtfs"]].sort_values("stop_id", key=lambda s: s.astype(int))

    fuera = salida[(salida.lat.abs() > 90) | (salida.lon.abs() > 180)]
    if len(fuera):
        raise ValueError(f"{len(fuera)} paradas con coordenadas fuera de rango")

    destino = comun.carpeta_fuente(TIPO, carpeta, base=comun.PARA_ETL)
    salida.to_csv(destino / "paraderos_aty.csv", index=False, encoding="utf-8")
    escribir_geojson(salida, destino / "paraderos_aty.geojson",
                     ["stop_id", "nombre", "accesible_silla_ruedas", "num_rutas", "rutas", "fuente", "version_gtfs"])
    print(f"  {carpeta}: {len(salida):,} paradas, {int((salida.num_rutas > 0).sum()):,} con servicio")

    # Si el equipo ya exportó a mano la capa original del Geoportal, también se convierte.
    manuales = exportaciones_manuales(carpeta)
    for ruta in manuales:
        registrar_manual(carpeta, ruta)
    if manuales:
        ficha_actual = comun.leer_procedencia(origen)
        ficha_actual["estado"] = "real"
        comun.guardar_procedencia(origen, ficha_actual)
        convertir_manual(carpeta, manuales)


def descargar_overpass(origen, archivo: str, consulta: str) -> dict:
    """Guarda la respuesta de Overpass una sola vez y la registra; devuelve el JSON."""
    ruta = origen / archivo
    if not ruta.exists():
        # Overpass es un servicio público y a veces está saturado: se prueba cada espejo con espera creciente.
        url_usada = ""
        for intento in range(5):
            for servidor in OVERPASS:
                url = f"{servidor}?{urlencode({'data': consulta})}"
                try:
                    r = comun.SESION.get(url, timeout=200)
                    if r.ok and r.text.lstrip().startswith("{") and '"elements"' in r.text:
                        ruta.write_bytes(r.content)
                        url_usada = url
                        break
                except requests.RequestException:
                    pass
            if ruta.exists():
                break
            time.sleep(20 * (intento + 1))
        else:
            raise SystemExit("Overpass no respondió; vuelve a intentar más tarde")
        comun.registrar(origen, {}, {
            "archivo": archivo, "url": url_usada, "descargado_utc": comun.ahora_utc(),
            "bytes": ruta.stat().st_size, "sha256": comun.sha256_de(ruta), "content_type": "application/json",
            "nota": "Respuesta de la API Overpass de OpenStreetMap; la consulta va en el parámetro data de la URL.",
        })
    return json.loads(ruta.read_text(encoding="utf-8"))


def marcar_sustituto(origen, descripcion: str) -> None:
    ficha = comun.leer_procedencia(origen)
    if ficha.get("estado") != "real":
        ficha.update({"estado": "sustituto", "sustituto": descripcion,
                      "url_sustituto": "https://www.openstreetmap.org/relation/5961522",
                      "licencia": LICENCIA_OSM})
        comun.guardar_procedencia(origen, ficha)


def unidades_deportivas_osm() -> None:
    """Sustituto de 4.1: instalaciones deportivas de OpenStreetMap dentro del municipio de Mérida."""
    carpeta = "4.1_unidades_deportivas"
    origen = comun.carpeta_fuente(TIPO, carpeta)
    datos = descargar_overpass(origen, OSM_ARCHIVO, OSM_CONSULTA)
    marcar_sustituto(origen, "Instalaciones deportivas de OpenStreetMap (leisure = sports_centre, stadium, pitch, "
                             "sports_hall o track) dentro del límite municipal de Mérida (relación OSM 5961522)")
    filas = []
    for e in datos["elements"]:
        t = e.get("tags", {})
        punto = e if e["type"] == "node" else e.get("center", {})
        if "lat" not in punto:
            continue
        acceso = t.get("access", "sin dato")
        filas.append({
            "osm_id": f"{e['type']}/{e['id']}", "nombre": t.get("name"), "tipo": t.get("leisure"),
            "deporte": t.get("sport"), "acceso": acceso, "operador": t.get("operator"),
            "superficie": t.get("surface"), "iluminado": t.get("lit"),
            "acceso_publico_probable": acceso not in {"private", "customers", "no", "members"},
            "lat": round(float(punto["lat"]), 7), "lon": round(float(punto["lon"]), 7),
            "fuente": "OpenStreetMap", "version_osm": datos.get("osm3s", {}).get("timestamp_osm_base", ""),
        })
    salida = pd.DataFrame(filas).sort_values("osm_id", kind="stable")
    destino = comun.carpeta_fuente(TIPO, carpeta, base=comun.PARA_ETL)
    salida.to_csv(destino / "unidades_deportivas_osm.csv", index=False, encoding="utf-8")
    escribir_geojson(salida, destino / "unidades_deportivas_osm.geojson",
                     [c for c in salida.columns if c not in {"lat", "lon"}])
    print(f"  {carpeta}: {len(salida):,} instalaciones deportivas de OpenStreetMap "
          f"({int(salida['acceso_publico_probable'].sum()):,} sin acceso restringido)")


def categoria_ciclista(t: dict) -> str:
    if t.get("amenity") == "bicycle_parking":
        return "estacionamiento"
    if t.get("amenity") == "bicycle_rental":
        return "renta de bicicletas"
    if t.get("highway") in {"cycleway", "path"}:
        return "ciclovía"
    return "carril en calle"


def longitud_m(geometria: list[dict]) -> float:
    if len(geometria) < 2:
        return 0.0
    lat = np.radians([g["lat"] for g in geometria])
    lon = np.radians([g["lon"] for g in geometria])
    a = np.sin(np.diff(lat) / 2) ** 2 + np.cos(lat[:-1]) * np.cos(lat[1:]) * np.sin(np.diff(lon) / 2) ** 2
    return float((2 * 6_371_000 * np.arcsin(np.sqrt(a))).sum())


def infraestructura_ciclista_osm() -> None:
    """Sustituto de 4.2: ciclovías, carriles y estacionamientos de bicicletas de OpenStreetMap en Mérida."""
    carpeta = "4.2_circuito_enlace"
    origen = comun.carpeta_fuente(TIPO, carpeta)
    if exportaciones_manuales(carpeta):
        return
    datos = descargar_overpass(origen, OSM_CICLISTA_ARCHIVO, OSM_CICLISTA_CONSULTA)
    marcar_sustituto(origen, "Infraestructura ciclista de OpenStreetMap (ciclovías, carriles en calle, "
                             "estacionamientos y renta de bicicletas) dentro del límite municipal de Mérida "
                             "(relación OSM 5961522). El recorrido del Circuito Enlace no se publica fuera del "
                             "Geoportal")
    version = datos.get("osm3s", {}).get("timestamp_osm_base", "")
    filas, rasgos = [], []
    for e in datos["elements"]:
        t = e.get("tags", {})
        geom = e.get("geometry") or []
        if e["type"] == "node":
            lat, lon = e["lat"], e["lon"]
            figura = {"type": "Point", "coordinates": [round(lon, 7), round(lat, 7)]}
        elif geom:
            lat = sum(g["lat"] for g in geom) / len(geom)
            lon = sum(g["lon"] for g in geom) / len(geom)
            coords = [[round(g["lon"], 7), round(g["lat"], 7)] for g in geom]
            cerrado = t.get("amenity") == "bicycle_parking" and len(coords) > 3 and coords[0] == coords[-1]
            figura = ({"type": "Polygon", "coordinates": [coords]} if cerrado
                      else {"type": "LineString", "coordinates": coords})
        else:
            continue
        fila = {
            "osm_id": f"{e['type']}/{e['id']}", "categoria": categoria_ciclista(t), "nombre": t.get("name"),
            "tipo_via": t.get("highway"),
            "tipo_carril": (t.get("cycleway") or t.get("cycleway:both") or t.get("cycleway:right")
                            or t.get("cycleway:left")),
            "superficie": t.get("surface"), "segregada": t.get("segregated"), "iluminado": t.get("lit"),
            "capacidad": int(t["capacity"]) if str(t.get("capacity", "")).isdigit() else None,
            "longitud_m": round(longitud_m(geom), 1) if figura["type"] == "LineString" else None,
            "lat": round(float(lat), 7), "lon": round(float(lon), 7),
            "fuente": "OpenStreetMap", "version_osm": version,
        }
        filas.append(fila)
        rasgos.append({"type": "Feature", "geometry": figura,
                       "properties": {k: (None if pd.isna(v) else v) for k, v in fila.items()
                                      if k not in {"lat", "lon"}}})
    salida = pd.DataFrame(filas).sort_values("osm_id", kind="stable")
    destino = comun.carpeta_fuente(TIPO, carpeta, base=comun.PARA_ETL)
    salida.to_csv(destino / "infraestructura_ciclista_osm.csv", index=False, encoding="utf-8")
    rasgos.sort(key=lambda r: r["properties"]["osm_id"])
    (destino / "infraestructura_ciclista_osm.geojson").write_text(json.dumps(
        {"type": "FeatureCollection", "name": "infraestructura_ciclista_osm",
         "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
         "features": rasgos}, ensure_ascii=False) + "\n", encoding="utf-8")
    km = salida.loc[salida["categoria"].isin(["ciclovía", "carril en calle"]), "longitud_m"].sum() / 1000
    print(f"  {carpeta}: {len(salida):,} elementos de infraestructura ciclista de OpenStreetMap "
          f"({km:,.1f} km de ciclovías y carriles)")


def main() -> None:
    print("Subtema 4: Geoportal de Mérida")
    capas_pendientes()
    unidades_deportivas_osm()
    infraestructura_ciclista_osm()
    paraderos()


if __name__ == "__main__":
    main()
