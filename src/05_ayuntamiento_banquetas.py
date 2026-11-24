"""Fuente 5.3: Ayuntamiento de Mérida, obras de banquetas y accesibilidad peatonal.

La referencia del equipo era una nota de prensa del Ayuntamiento. De ella solo
se guardan metadatos (URL, título, fecha, fecha de consulta), no el texto.

Como dato público del mismo tema se usa el Sistema de Recursos Federales
Transferidos (SRFT) de la SHCP, que publica en datos abiertos cada proyecto
que estados y municipios hacen con recursos federales: nombre de la obra,
ejecutor, montos, fechas, metas (metros cuadrados) y georreferencias. Se
filtra el municipio de Mérida (entidad 31, municipio 050), 2023 a 2026.

Página: https://www.transparenciapresupuestaria.gob.mx/Entidades-Federativas
(Datos abiertos > Proyectos). Los zips nacionales pesan de 24 a 139 MB, así
que se bajan a una carpeta temporal fuera del repositorio; en originales/ se
guardan las filas de Mérida de cada tabla sin transformar (solo pasadas de
latin-1 a UTF-8) y procedencia.json registra la URL, bytes y SHA-256 del zip.

Salidas en datos/para-etl/05_solicitud_datos/5.3_ayuntamiento_banquetas/:
- obras_banquetas_merida.csv: una fila por obra de banquetas, guarniciones o
  accesibilidad peatonal en Mérida, con su último reporte, metros, montos y
  coordenadas (EPSG:4326).
- obras_banquetas_merida.geojson: las obras con coordenadas, como puntos.

Uso: python src/05_ayuntamiento_banquetas.py
"""

from __future__ import annotations

import hashlib
import html
import json
import math
import os
import re
import tempfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

import comun

TIPO = "05_solicitud_datos"
CARPETA = "5.3_ayuntamiento_banquetas"
URL_NOTA = ("https://prensa.merida.gob.mx/12416/Ante-demanda-ciudadana-Cecilia-Patron-mejora-la-"
            "infraestructura-para-los-transeuntes-del-centro-historico/amp")
BASE_SRFT = "https://www.transparenciapresupuestaria.gob.mx/work/models/PTP/DatosAbiertos"
PAGINA_SRFT = "https://www.transparenciapresupuestaria.gob.mx/Entidades-Federativas"
PERIODOS = {  # periodo -> (ruta del zip, carpeta preferida dentro del zip)
    "2023": ("Entidades_Federativas/2023/ef2023.zip", "cuarto_informe_definitivo"),
    "2024": ("Entidades_Federativas/2024/ef2024.zip", ""),
    "2025": ("Entidades_Federativas/2025/ef2025.zip", ""),
    "2026_3T": ("Entidades_Federativas/2026/ef2026_3T.zip", ""),
}
TABLAS = {"proyectos": "ef", "georreferencias": "georreferencias", "metas": "metas_avances"}
ENTIDAD, MUNICIPIO = "31", "50"
CACHE = Path(tempfile.gettempdir()) / "del-tren-srft"
PALABRAS = r"BANQUET|GUARNICI|ACERA|PEATON|ESCARPA|ACCESIBIL|RAMPA|ANDADOR|CRUCE SEGURO"
PLAZA_GRANDE = (20.96705, -89.62372)  # lat, lon de la Plaza Grande, centro de Mérida
RADIO_CENTRO_KM = 1.2

FICHA = {
    "id": "E8-05.3",
    "nombre": "Ayuntamiento de Mérida: obras de banquetas y accesibilidad peatonal en el Centro",
    "institucion": "Ayuntamiento de Mérida (ejecutor); Secretaría de Hacienda y Crédito Público (publica el SRFT)",
    "url_original": URL_NOTA,
    "licencia": ("Nota de prensa: solo metadatos. SRFT: datos abiertos de la SHCP; la página no muestra "
                 "licencia propia; los conjuntos de la SHCP en datos.gob.mx se publican con CC-BY-4.0 "
                 "(Decreto de datos abiertos de 2015)."),
    "estado": "sustituto",
    "sustituto": "Proyectos del SRFT (Transparencia Presupuestaria, SHCP) del municipio de Mérida, 2023-2026",
    "url_sustituto": PAGINA_SRFT,
    "acceso": "Descarga directa de los zips de datos abiertos; filtro por entidad 31 y municipio 050",
}


# --- Nota de prensa: solo metadatos -------------------------------------------------

def nota_prensa() -> None:
    origen = comun.carpeta_fuente(TIPO, CARPETA)
    r = comun.SESION.get(URL_NOTA, timeout=60)
    r.raise_for_status()
    pagina = r.content.decode("utf-8", errors="replace")
    ld = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', pagina, re.S).group(1))
    texto = html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", pagina)))
    fecha_pagina = re.search(r"(Lunes|Martes|Miércoles|Jueves|Viernes|Sábado|Domingo) \d{1,2} de \w+ de \d{4}", texto)
    ubicacion = re.search(r"calle (\d+), entre las calles (\d+) y (\d+)", texto)
    fila = {
        "url": URL_NOTA,
        "url_canonica": ld.get("mainEntityOfPage", ""),
        "titulo": ld.get("headline", ""),
        "fecha_publicacion": ld.get("datePublished", ""),
        "fecha_en_pagina": fecha_pagina.group(0) if fecha_pagina else "",
        "institucion": (ld.get("publisher") or {}).get("name", ""),
        "ubicacion_mencionada": (f"calle {ubicacion.group(1)} entre {ubicacion.group(2)} y {ubicacion.group(3)}, "
                                 "Centro Histórico") if ubicacion else "",
        "fecha_consulta_utc": comun.ahora_utc(),
        "sha256_pagina": hashlib.sha256(r.content).hexdigest(),
    }
    nombre = "nota_prensa_metadatos.csv"
    pd.DataFrame([fila]).to_csv(origen / nombre, index=False, encoding="utf-8")
    comun.registrar(origen, FICHA, {
        "archivo": nombre, "url": URL_NOTA, "descargado_utc": fila["fecha_consulta_utc"],
        "bytes": (origen / nombre).stat().st_size, "sha256": comun.sha256_de(origen / nombre),
        "content_type": "text/csv",
        "nota": ("Solo metadatos de la nota (no se guarda el texto). sha256_pagina es el hash de la página "
                 "AMP consultada."),
    })
    print(f"  nota de prensa: {fila['titulo'][:60]}… ({fila['fecha_publicacion'][:10]})")


# --- SRFT -------------------------------------------------------------------------

def preparar_tls() -> None:
    """Completa la cadena TLS de transparenciapresupuestaria.gob.mx sin desactivar la verificación.

    El servidor envía un intermedio que no corresponde a su certificado (R10 en vez de YR2).
    Se agregan al almacén de certifi el intermedio YR2 y la firma cruzada de ISRG Root YR por
    ISRG Root X1, ambos bajados por HTTPS verificado del sitio oficial de Let's Encrypt.
    """
    import certifi
    base = "https://letsencrypt.org/certs/gen-y/"
    extra = "".join(comun.SESION.get(base + n, timeout=60).text for n in ("int-yr2.pem", "root-yr-by-x1.pem"))
    if extra.count("BEGIN CERTIFICATE") != 2:
        raise RuntimeError("No se pudieron obtener los certificados de Let's Encrypt")
    almacen = Path(tempfile.gettempdir()) / "del-tren-ca.pem"
    almacen.write_text(Path(certifi.where()).read_text(encoding="utf-8") + "\n" + extra, encoding="utf-8")
    comun.SESION.verify = str(almacen)
    # requests da prioridad a estas variables sobre SESION.verify; solo afecta a este proceso.
    os.environ["REQUESTS_CA_BUNDLE"] = str(almacen)


def bajar_zip(ruta: str) -> tuple[Path, dict]:
    CACHE.mkdir(parents=True, exist_ok=True)
    url = f"{BASE_SRFT}/{ruta}"
    destino = CACHE / Path(ruta).name
    if not destino.exists():
        with comun.SESION.get(url, stream=True, timeout=600) as r:
            r.raise_for_status()
            temporal = destino.with_suffix(".parcial")
            with open(temporal, "wb") as f:
                for bloque in r.iter_content(1 << 20):
                    f.write(bloque)
            temporal.replace(destino)
        print(f"  bajado {destino.name} ({destino.stat().st_size:,} bytes) a la carpeta temporal")
    bajado = datetime.fromtimestamp(destino.stat().st_mtime, timezone.utc).replace(microsecond=0)
    return destino, {"url": url, "bytes": destino.stat().st_size, "sha256": comun.sha256_de(destino),
                     "descargado_utc": bajado.isoformat().replace("+00:00", "Z")}


def miembro(z: zipfile.ZipFile, base: str, preferida: str) -> str:
    candidatos = [n for n in z.namelist() if Path(n).name.lower().startswith(base)
                  and Path(n).suffix.lower() == ".csv"]
    if base == "ef":
        candidatos = [n for n in candidatos if re.match(r"ef\d{4}\.csv", Path(n).name.lower())]
    candidatos.sort(key=lambda n: preferida not in n)
    if not candidatos:
        raise ValueError(f"no hay {base}*.csv en el zip")
    return candidatos[0]


def extraer_periodo(periodo: str, ruta: str, preferida: str) -> None:
    origen = comun.carpeta_fuente(TIPO, CARPETA)
    zip_local, zip_info = bajar_zip(ruta)
    with zipfile.ZipFile(zip_local) as z:
        folios = None
        for tabla, base in TABLAS.items():
            nombre_zip = miembro(z, base, preferida)
            with z.open(nombre_zip) as f:
                df = pd.read_csv(f, encoding="latin-1", dtype=str, keep_default_na=False)
            if tabla == "proyectos":
                col_mun = "ID_MUNICIPIO" if "ID_MUNICIPIO" in df else "ID_MUNICIPIO_RESPONSABLE"
                df = df[(df["ID_ENTIDAD_FEDERATIVA"] == ENTIDAD) & (df[col_mun] == MUNICIPIO)]
                folios = set(df["FOLIO"])
                filtro = f"ID_ENTIDAD_FEDERATIVA == {ENTIDAD} y {col_mun} == {MUNICIPIO}"
            else:
                df = df[df["FOLIO"].isin(folios)]
                filtro = "FOLIO en los proyectos de Mérida del mismo periodo"
            nombre = f"srft_{periodo}_{tabla}_merida.csv"
            df.to_csv(origen / nombre, index=False, encoding="utf-8")
            comun.registrar(origen, FICHA, {
                "archivo": nombre, "url": zip_info["url"], "descargado_utc": zip_info["descargado_utc"],
                "bytes": (origen / nombre).stat().st_size, "sha256": comun.sha256_de(origen / nombre),
                "content_type": "text/csv", "registros": len(df),
                "zip": {"bytes": zip_info["bytes"], "sha256": zip_info["sha256"], "archivo_en_zip": nombre_zip},
                "filtro": filtro,
                "nota": ("Filas de Mérida sin transformar, tal como vienen en el zip nacional; codificación "
                         "original latin-1 pasada a UTF-8. El zip no se versiona por su tamaño."),
            })
            print(f"  {nombre}: {len(df):,} filas")


def diccionario() -> None:
    origen = comun.carpeta_fuente(TIPO, CARPETA)
    comun.descargar(f"{BASE_SRFT}/Diccionarios/diccionario_ef.xlsx", origen, "srft_diccionario_proyectos.xlsx",
                    FICHA, nota="Diccionario de datos de la base de Proyectos del SRFT.")


# --- Para ETL ---------------------------------------------------------------------

def a_num(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.str.replace(",", "", regex=False).replace("", None), errors="coerce")


def combinar(df: pd.DataFrame, nueva: str, vieja: str) -> pd.Series:
    """Une una columna que cambió de nombre entre años (por ejemplo LAT y LATITUD)."""
    a = df[nueva].fillna("") if nueva in df else pd.Series("", index=df.index)
    b = df[vieja].fillna("") if vieja in df else pd.Series("", index=df.index)
    return a.where(a != "", b)


def distancia_km(lat: float, lon: float) -> float:
    la1, lo1, la2, lo2 = map(math.radians, (PLAZA_GRANDE[0], PLAZA_GRANDE[1], lat, lon))
    a = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(a))


def tipo_obra(nombre: str) -> str:
    n = nombre.upper()
    if "BANQUET" in n and "GUARNICI" in n:
        return "guarniciones y banquetas"
    for clave, etiqueta in (("BANQUET", "banquetas"), ("GUARNICI", "guarniciones"), ("ESCARPA", "banquetas"),
                            ("ACERA", "banquetas"), ("ANDADOR", "andador"), ("PEATON", "infraestructura peatonal"),
                            ("RAMPA", "rampas de accesibilidad"), ("ACCESIBIL", "accesibilidad"),
                            ("CRUCE SEGURO", "cruce seguro")):
        if clave in n:
            return etiqueta
    return "otra"


def colonia(nombre: str) -> str:
    m = re.search(r"\b(COL(?:ONIA)?|FRACC(?:IONAMIENTO)?|BARRIO)\.?\s+(.+?)\s+(?:LOCALIDAD|MUNICIPIO|\d{3}-\d{2}-\d{4}|-)",
                  nombre.upper())
    if m:
        return f"{m.group(1).title()} {m.group(2).title()}".strip()
    m = re.search(r"ASENTAMIENTO\s+(.+?)\s+(?:PROYECTO|-\s*\d+$)", nombre.upper())
    if m:
        return m.group(1).title()
    m = re.search(r"LOCALIDAD\s+(.+?)\s+MUNICIPIO", nombre.upper())
    return m.group(1).title() if m else ""


def fecha_iso(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, format="%d/%m/%Y", errors="coerce").dt.strftime("%Y-%m-%d")


def para_etl() -> None:
    origen = comun.carpeta_fuente(TIPO, CARPETA)
    leer = lambda n: pd.read_csv(origen / n, dtype=str, keep_default_na=False)  # noqa: E731
    proyectos = pd.concat([leer(f"srft_{p}_proyectos_merida.csv").assign(periodo=p) for p in PERIODOS],
                          ignore_index=True)
    geo = pd.concat([leer(f"srft_{p}_georreferencias_merida.csv").assign(periodo=p) for p in PERIODOS],
                    ignore_index=True)
    metas = pd.concat([leer(f"srft_{p}_metas_merida.csv").assign(periodo=p) for p in PERIODOS],
                      ignore_index=True)

    proyectos["APROBADO"] = combinar(proyectos, "APROBADO", "MONTO_GLOBAL_APROBADO")
    obras = proyectos[proyectos["NOMBRE"].str.contains(PALABRAS, case=False, regex=True)].copy()
    obras["_orden"] = obras["CICLO"].astype(int) * 10 + pd.to_numeric(obras["TRIMESTRE"], errors="coerce").fillna(0)
    obras = obras.sort_values("_orden").drop_duplicates("FOLIO", keep="last")

    # Metas: último reporte de cada folio
    metas["_orden"] = metas["CICLO"].astype(int) * 10 + pd.to_numeric(metas["TRIMESTRE"], errors="coerce").fillna(0)
    metas = metas.sort_values("_orden").drop_duplicates(["FOLIO", "UNIDAD_MEDIDA"], keep="last")
    m2 = metas[metas["UNIDAD_MEDIDA"].str.contains("cuadrad", case=False)].set_index("FOLIO")
    ml = metas[metas["UNIDAD_MEDIDA"].str.contains("lineal", case=False)].set_index("FOLIO")
    meta_principal = metas.drop_duplicates("FOLIO", keep="last").set_index("FOLIO")

    # Georreferencias: primer punto del último periodo y número de puntos
    geo["lat"] = a_num(combinar(geo, "LAT", "LATITUD"))
    geo["lon"] = a_num(combinar(geo, "LON", "LONGITUD"))
    geo = geo[geo["lat"].between(20.5, 21.5) & geo["lon"].between(-90.0, -89.2)]
    ult_geo = geo.sort_values("periodo").groupby("FOLIO")
    puntos = ult_geo.agg(lat=("lat", "first"), lon=("lon", "first"), direccion=("DIRECCION", "first"),
                         num_puntos=("lat", "size"))

    s = pd.DataFrame({
        "folio": obras["FOLIO"],
        "ciclo_reporte": obras["CICLO"],
        "trimestre_reporte": obras["TRIMESTRE"],
        "nombre_obra": obras["NOMBRE"].str.strip(),
        "tipo_obra": obras["NOMBRE"].map(tipo_obra),
        "colonia_o_localidad": obras["NOMBRE"].map(colonia),
        "ejecutor": obras["INSTITUCION_EJECUTORA"],
        "ejecuta_ayuntamiento": obras["INSTITUCION_EJECUTORA"].str.contains("municipio de m", case=False),
        "clasificacion": obras["CLASIFICACION"],
        "monto_aprobado_mxn": a_num(obras["APROBADO"]),
        "comprometido_mxn": a_num(combinar(obras, "COMPROMETIDO", "MONTO_COMPROMETIDO")),
        "devengado_mxn": a_num(combinar(obras, "DEVENGADO", "MONTO_DEVENGADO")),
        "ejercido_mxn": a_num(combinar(obras, "EJERCIDO", "MONTO_EJERCIDO")),
        "pagado_mxn": a_num(combinar(obras, "PAGADO", "MONTO_PAGADO")),
        "fecha_inicio": fecha_iso(obras["FECHA_INICIO"]),
        "fecha_estimada_termino": fecha_iso(obras["FECHA_ESTIMADA_TERMINO"]),
        "estatus": combinar(obras, "DESC_ESTATUS", "ESTATUS"),
    })
    s["meta_unidad"] = s["folio"].map(meta_principal["UNIDAD_MEDIDA"])
    s["meta"] = a_num(s["folio"].map(meta_principal["META_MODIFICADA"]).fillna(""))
    s["avance_fisico"] = a_num(s["folio"].map(meta_principal["AVANCE_FISICO"]).fillna(""))
    s["metros_cuadrados"] = a_num(s["folio"].map(m2["META_MODIFICADA"]).fillna(""))
    s["metros_lineales"] = a_num(s["folio"].map(ml["META_MODIFICADA"]).fillna(""))
    s = s.join(puntos, on="folio")
    s["distancia_plaza_grande_km"] = [round(distancia_km(a, o), 3) if pd.notna(a) else None
                                      for a, o in zip(s["lat"], s["lon"])]
    s["en_centro_historico"] = (s["distancia_plaza_grande_km"].le(RADIO_CENTRO_KM)
                                | s["nombre_obra"].str.contains(r"CENTRO HIST|COL\.? CENTRO\b", case=False))
    s["fuente"] = "SRFT, Transparencia Presupuestaria (SHCP)"
    s = s.sort_values(["fecha_inicio", "folio"], na_position="last")

    destino = comun.carpeta_fuente(TIPO, CARPETA, base=comun.PARA_ETL)
    s.to_csv(destino / "obras_banquetas_merida.csv", index=False, encoding="utf-8")
    rasgos = []
    for f in s[s["lat"].notna()].to_dict("records"):
        props = {k: (None if isinstance(v, float) and math.isnan(v) else v)
                 for k, v in f.items() if k not in ("lat", "lon")}
        props["num_puntos"] = None if props.get("num_puntos") is None else int(props["num_puntos"])
        rasgos.append({"type": "Feature",
                       "geometry": {"type": "Point", "coordinates": [round(f["lon"], 7), round(f["lat"], 7)]},
                       "properties": props})
    (destino / "obras_banquetas_merida.geojson").write_text(json.dumps(
        {"type": "FeatureCollection", "name": "obras_banquetas_merida",
         "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:OGC:1.3:CRS84"}},
         "features": rasgos}, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(f"  para-etl: {len(s)} obras ({int(s['ejecuta_ayuntamiento'].sum())} del Ayuntamiento), "
          f"{len(rasgos)} con coordenadas, {int(s['en_centro_historico'].sum())} en el Centro Histórico")


def main() -> None:
    print("Fuente 5.3: Ayuntamiento de Mérida, banquetas")
    nota_prensa()
    preparar_tls()
    diccionario()
    for periodo, (ruta, preferida) in PERIODOS.items():
        extraer_periodo(periodo, ruta, preferida)
    para_etl()


if __name__ == "__main__":
    main()
