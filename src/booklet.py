"""Genera los datos del capítulo del booklet (carpeta booklet/datos/).

Solo usa datos reales del repositorio:
- escena 1: negocios por anillo de distancia, 2019 contra 2025, alrededor de
  las 34 estaciones del Tren Maya (data mart del DENUE, subtema 3);
- escena 2: cambio de negocios a 5 km de cada estación (mismo data mart);
- escena 3: pasajeros por mes del Tren Maya (gold ind_tren_maya_mensual);
- escena 4: variación de negocios por AGEB urbana de Mérida (gold
  ind_negocios_ageb_merida) y sus polígonos simplificados del Marco
  Geoestadístico.

También escribe booklet/graficas/escena-N.html, una página por escena, con el texto
de booklet/index.html, que es donde se editan los títulos y las lecturas.

El GeoJSON va con los anillos en el sentido que usa D3 (exterior en sentido
horario), simplificado con Ramer-Douglas-Peucker a unos 9 m.

Uso: python src/booklet.py
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
MART = RAIZ / "procesamiento" / "03_denue_datamart" / "data"
GOLD = RAIZ / "datos" / "gold"
POLIGONOS = RAIZ / "datos" / "para-etl" / "03_inegi" / "3.3_censo_2020_ageb" / "ageb_urbana_yucatan_poligonos.geojson"
SALIDA = RAIZ / "booklet" / "datos"
GRAFICAS = RAIZ / "booklet" / "graficas"
MERIDA = "31050"
TOLERANCIA_GRADOS = 0.00008  # unos 9 m: suficiente para un mapa impreso de la ciudad
ANILLOS = ["0-1 km", "1-3 km", "3-5 km"]


def csv(df: pd.DataFrame, nombre: str) -> str:
    texto = df.to_csv(index=False, lineterminator="\n")
    (SALIDA / nombre).write_text(texto, encoding="utf-8", newline="")
    return texto


def pct(a: float, b: float) -> float | None:
    return round((b - a) / a * 100, 1) if a else None


def escena_1_y_2() -> tuple[pd.DataFrame, pd.DataFrame]:
    anillos = pd.read_csv(MART / "processed" / "station_ring_change_2019_2025.csv")
    catalogo = pd.read_csv(MART / "reference" / "estaciones_tren_maya_catalogo_maestro.csv")

    e1 = (anillos.groupby("distance_band", as_index=False)[["businesses_2019", "businesses_2025"]].sum()
          .rename(columns={"distance_band": "anillo", "businesses_2019": "negocios_2019",
                           "businesses_2025": "negocios_2025"}))
    e1["anillo"] = pd.Categorical(e1["anillo"], ANILLOS, ordered=True)
    e1 = e1.sort_values("anillo")
    e1[["negocios_2019", "negocios_2025"]] = e1[["negocios_2019", "negocios_2025"]].astype(int)
    e1["cambio"] = e1["negocios_2025"] - e1["negocios_2019"]
    e1["cambio_pct"] = [pct(a, b) for a, b in zip(e1["negocios_2019"], e1["negocios_2025"])]
    e1["estaciones"] = 34

    tot = (anillos.groupby(["nearest_station_id"], as_index=False)[["businesses_2019", "businesses_2025"]].sum()
           .rename(columns={"nearest_station_id": "station_id"}))
    e2 = catalogo[["station_id", "station_name", "state", "municipality"]].merge(tot, on="station_id", how="left")
    e2[["businesses_2019", "businesses_2025"]] = e2[["businesses_2019", "businesses_2025"]].fillna(0).astype(int)
    e2 = e2.rename(columns={"station_id": "estacion_id", "station_name": "estacion", "state": "estado",
                            "municipality": "municipio", "businesses_2019": "negocios_2019",
                            "businesses_2025": "negocios_2025"})
    e2["cambio"] = e2["negocios_2025"] - e2["negocios_2019"]
    e2["cambio_pct"] = [pct(a, b) for a, b in zip(e2["negocios_2019"], e2["negocios_2025"])]
    e2["estaciones_en_su_estado"] = e2.groupby("estado")["estacion_id"].transform("count")
    e2 = e2.sort_values(["cambio", "estacion_id"], ascending=[False, True]).reset_index(drop=True)
    e2.insert(0, "lugar", range(1, len(e2) + 1))

    assert len(e2) == 34, len(e2)
    assert e1["negocios_2019"].sum() == e2["negocios_2019"].sum() == anillos["businesses_2019"].sum()
    assert e1["negocios_2025"].sum() == e2["negocios_2025"].sum() == anillos["businesses_2025"].sum()
    return e1, e2


def escena_3() -> pd.DataFrame:
    g = pd.read_csv(GOLD / "ind_tren_maya_mensual.csv", parse_dates=["fecha_mes"])
    e3 = pd.DataFrame({
        "mes": g["fecha_mes"].dt.strftime("%Y-%m"),
        "anio": g["fecha_mes"].dt.year,
        "pasajeros": g["pasajeros_transportados"].astype(int),
        "boletos_vendidos": g["boletos_vendidos"].astype(int),
        "variacion_anual_pct": g["variacion_anual_pasajeros_pct"],
    })
    return e3


def rdp(puntos: list[list[float]], tol: float) -> list[list[float]]:
    """Simplificación de Ramer-Douglas-Peucker de un anillo."""
    if len(puntos) < 4:
        return puntos
    (x1, y1), (x2, y2) = puntos[0], puntos[-1]
    dx, dy = x2 - x1, y2 - y1
    norma = math.hypot(dx, dy)
    mayor, indice = -1.0, 0
    for i in range(1, len(puntos) - 1):
        x0, y0 = puntos[i]
        d = (abs(dy * x0 - dx * y0 + x2 * y1 - y2 * x1) / norma) if norma else math.hypot(x0 - x1, y0 - y1)
        if d > mayor:
            mayor, indice = d, i
    if mayor <= tol:
        return [puntos[0], puntos[-1]]
    return rdp(puntos[: indice + 1], tol)[:-1] + rdp(puntos[indice:], tol)


def area_con_signo(anillo: list[list[float]]) -> float:
    return sum(x1 * y2 - x2 * y1 for (x1, y1), (x2, y2) in zip(anillo, anillo[1:])) / 2


def simplificar_anillo(anillo: list[list[float]], exterior: bool) -> list[list[float]]:
    # Se parte el anillo en dos mitades para que RDP no lo colapse (inicio y fin son el mismo punto).
    mitad = len(anillo) // 2
    s = rdp(anillo[: mitad + 1], TOLERANCIA_GRADOS)[:-1] + rdp(anillo[mitad:], TOLERANCIA_GRADOS)
    s = [[round(x, 5), round(y, 5)] for x, y in s]
    if len(s) < 4:
        s = [[round(x, 5), round(y, 5)] for x, y in anillo]
    # D3 dibuja en la esfera: el anillo exterior va en sentido horario y los huecos al revés.
    if (area_con_signo(s) > 0) == exterior:
        s.reverse()
    return s


def simplificar_poligono(anillos: list[list[list[float]]]) -> list[list[list[float]]]:
    return [simplificar_anillo(a, i == 0) for i, a in enumerate(anillos)]


def escena_4() -> tuple[pd.DataFrame, dict]:
    g = pd.read_csv(GOLD / "ind_negocios_ageb_merida.csv", dtype={"cvegeo_ageb": str})
    teya = pd.read_csv(MART / "reference" / "estaciones_tren_maya_catalogo_maestro.csv").set_index("station_id").loc["TM015"]
    geo = json.loads(POLIGONOS.read_text(encoding="utf-8"))
    feats = [f for f in geo["features"] if str(f["properties"]["cvegeo_ageb"]).startswith(MERIDA)]

    def centroide(f):
        anillo = f["geometry"]["coordinates"][0] if f["geometry"]["type"] == "Polygon" else f["geometry"]["coordinates"][0][0]
        xs, ys = zip(*anillo)
        return sum(ys) / len(ys), sum(xs) / len(xs)

    def km(lat1, lon1, lat2, lon2):
        p = math.pi / 180
        a = (math.sin((lat2 - lat1) * p / 2) ** 2
             + math.cos(lat1 * p) * math.cos(lat2 * p) * math.sin((lon2 - lon1) * p / 2) ** 2)
        return 2 * 6371.0 * math.asin(math.sqrt(a))

    dist = {}
    for f in feats:
        lat, lon = centroide(f)
        dist[f["properties"]["cvegeo_ageb"]] = round(km(lat, lon, teya["latitude"], teya["longitude"]), 2)

    e4 = pd.DataFrame({
        "cvegeo_ageb": g["cvegeo_ageb"],
        "poblacion_2020": g["pobtot"],
        "negocios_2019": g["establecimientos_2019"].astype(int),
        "negocios_2025": g["establecimientos_2025"].astype(int),
    })
    e4["cambio"] = e4["negocios_2025"] - e4["negocios_2019"]
    e4["cambio_pct"] = g["variacion_pct_2019_2025"]
    e4["negocios_por_1000_hab_2025"] = g["establecimientos_por_1000_hab_2025"]
    e4["grado_marginacion_2020"] = g["gm_2020"]
    e4["distancia_estacion_teya_km"] = e4["cvegeo_ageb"].map(dist)

    salida = []
    claves = set(e4["cvegeo_ageb"])
    for f in feats:
        clave = f["properties"]["cvegeo_ageb"]
        geom = f["geometry"]
        if geom["type"] == "Polygon":
            coords = simplificar_poligono(geom["coordinates"])
        else:
            coords = [simplificar_poligono(p) for p in geom["coordinates"]]
        salida.append({"type": "Feature", "properties": {"cvegeo_ageb": clave, "con_dato": clave in claves},
                       "geometry": {"type": geom["type"], "coordinates": coords}})
    salida.sort(key=lambda f: f["properties"]["cvegeo_ageb"])
    gj = {"type": "FeatureCollection",
          "name": "ageb_urbanas_merida_simplificadas",
          "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
          "features": salida}
    sin_poligono = claves - {f["properties"]["cvegeo_ageb"] for f in salida}
    assert not sin_poligono, sorted(sin_poligono)[:5]
    return e4, gj


PAGINA = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Escena {n} · Del tren a la calle</title>
  <link rel="stylesheet" href="estilo.css">
  <script src="https://cdn.jsdelivr.net/npm/d3@7.9.0/dist/d3.min.js"></script>
  <script src="comun.js"></script>
</head>
<body>
  <!-- Generado por src/booklet.py a partir de booklet/index.html. Los textos se editan en index.html. -->
  <main class="pagina">
    {articulo}
  </main>
  <script src="escena-{n}.js"></script>
  <script>dibujarEscena{n}();</script>
</body>
</html>
"""


def paginas_escena() -> int:
    """Una página por escena con el mismo texto que el capítulo completo (booklet/index.html)."""
    import re
    indice = (RAIZ / "booklet" / "index.html").read_text(encoding="utf-8")
    articulos = re.findall(r'<article class="escena">.*?</article>', indice, flags=re.S)
    for n, articulo in enumerate(articulos, start=1):
        assert f'id="grafica-escena-{n}"' in articulo, n
        (GRAFICAS / f"escena-{n}.html").write_text(PAGINA.format(n=n, articulo=articulo), encoding="utf-8")
    return len(articulos)


def main() -> None:
    SALIDA.mkdir(parents=True, exist_ok=True)
    GRAFICAS.mkdir(parents=True, exist_ok=True)
    e1, e2 = escena_1_y_2()
    e3 = escena_3()
    e4, gj = escena_4()
    for n, df in enumerate([e1, e2, e3, e4], start=1):
        csv(df, f"escena-{n}.csv")
    geo_texto = json.dumps(gj, ensure_ascii=False, separators=(",", ":"))
    (SALIDA / "merida_ageb.geojson").write_text(geo_texto, encoding="utf-8")
    (GRAFICAS / "datos.js").unlink(missing_ok=True)

    print(e1.to_string(index=False))
    print(e2.head(6).to_string(index=False))
    print(e2.tail(4).to_string(index=False))
    print(e3.to_string(index=False))
    print(e4.describe().to_string())
    print(f"polígonos: {len(gj['features'])}, geojson {len(geo_texto) / 1e3:.0f} KB")
    print(f"páginas de escena: {paginas_escena()}")


if __name__ == "__main__":
    main()
