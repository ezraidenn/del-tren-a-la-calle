"""Subtema 9, fuente 9.3: guía de la estación Teya-Mérida en rutatrenmaya.mx.

Baja https://rutatrenmaya.mx/estacion-teya-merida-en-el-tren-maya/ (una sola
página), la guarda tal cual en datos/originales/09_scraping/<carpeta>/paginas/
con su registro en procedencia.json y extrae dos tablas a
datos/para-etl/09_scraping/<carpeta>/:

- tarifas_desde_teya.csv: precios y duración del viaje en Tren Maya desde
  Mérida-Teya a cada estación, por tipo de boleto (tabla larga).
- conexiones_transporte.csv: transporte público entre la estación y la
  ciudad (origen, destino, costo, duración y ruta), tal como lo describe la guía.

rutatrenmaya.mx es un sitio privado, no oficial. robots.txt (revisado el
2026-11-24) no restringe la ruta. Su aviso legal
(https://rutatrenmaya.mx/aviso-legal-y-condidiones-generales-de-uso/) permite
copiar y almacenar para uso personal y prohíbe la reproducción con fines
comerciales; este uso es académico y sin fines comerciales.

Uso, desde la raíz del repositorio:
    python src/scraping/9.3_guia_estacion_teya.py
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import comun  # noqa: E402

TIPO = "09_scraping"
CARPETA = "9.3_guia_estacion_teya"
URL = "https://rutatrenmaya.mx/estacion-teya-merida-en-el-tren-maya/"
ORIGEN = "Mérida Teya"
COL_TARIFAS = ["tabla", "estacion_origen", "estacion_destino", "tipo_tarifa", "precio_mxn",
               "disponible", "duracion_texto", "duracion_min", "horario", "fecha_consulta", "url"]
COL_CONEXIONES = ["servicio", "origen", "destino", "costo_mxn", "duracion_min", "ruta",
                  "fecha_consulta", "url"]

FICHA = {
    "id": "E8-09.3",
    "nombre": "Guía de la estación Teya-Mérida (rutatrenmaya.mx)",
    "institucion": "rutatrenmaya.mx (sitio privado de información turística, no oficial)",
    "url_original": URL,
    "licencia": "Todos los derechos reservados. El aviso legal "
                "(https://rutatrenmaya.mx/aviso-legal-y-condidiones-generales-de-uso/) permite "
                "copiar y almacenar para uso personal y prohíbe la reproducción con fines "
                "comerciales. robots.txt no restringe la ruta. Uso académico, sin fines comerciales.",
    "acceso": "Scraping de una página con requests y BeautifulSoup.",
}


def limpiar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip()


def a_numero(texto: str) -> str:
    """'$1,295.50 MXN' -> '1295.50'; si no hay precio, cadena vacía."""
    m = re.search(r"\$\s*([\d,]+(?:\.\d+)?)", texto)
    return m.group(1).replace(",", "") if m else ""


def a_minutos(texto: str) -> str:
    """'7 h 32 min' -> '452'; '46 min' -> '46'; si no hay duración, cadena vacía."""
    h = re.search(r"(\d+)\s*h", texto)
    m = re.search(r"(\d+)\s*min", texto)
    if not h and not m:
        return ""
    return str((int(h.group(1)) * 60 if h else 0) + (int(m.group(1)) if m else 0))


def encabezado_previo(nodo, niveles=("h2", "h3", "h4")) -> str:
    previo = nodo.find_previous(list(niveles))
    return limpiar(previo.get_text(" ")) if previo else ""


def extraer_tarifas(sopa: BeautifulSoup, fecha: str) -> list[dict]:
    filas = []
    for tabla in sopa.find_all("table"):
        titulo = encabezado_previo(tabla)
        renglones = [[limpiar(c.get_text(" ")) for c in tr.find_all(["td", "th"])]
                     for tr in tabla.find_all("tr")]
        if not renglones:
            continue
        cabecera, datos = renglones[0], renglones[1:]
        # Tablas del Tren Restaurante: el destino está en el título («Mérida-Teya -> Izamal»).
        es_restaurante = cabecera[0].upper() == "HORARIO"
        tabla_nombre = (f"{encabezado_previo(tabla, ('h2',))} | {titulo}"
                        if es_restaurante else titulo)
        for r in datos:
            if len(r) != len(cabecera) or "ESTAS AQU" in " ".join(r).upper():
                continue
            if es_restaurante:
                destino = limpiar(titulo.split("->")[-1]) if "->" in titulo else ""
                horario, valores = r[0], r[1:-1]
            else:
                destino, horario, valores = r[0], "", r[1:-1]
            duracion = r[-1]
            for tipo, valor in zip(cabecera[1:-1], valores):
                disponible = "NO DISPONIBLE" not in valor.upper()
                filas.append({
                    "tabla": tabla_nombre, "estacion_origen": ORIGEN, "estacion_destino": destino,
                    "tipo_tarifa": tipo.title(), "precio_mxn": a_numero(valor),
                    "disponible": int(disponible),
                    "duracion_texto": duracion if disponible else "",
                    "duracion_min": a_minutos(duracion) if disponible else "",
                    "horario": horario, "fecha_consulta": fecha, "url": URL,
                })
    return filas


def extraer_conexiones(sopa: BeautifulSoup, fecha: str) -> list[dict]:
    """Recorre la sección «¿Cómo moverse desde la estación…?» párrafo por párrafo."""
    inicio = next((h for h in sopa.find_all("h2") if "moverse" in h.get_text().lower()), None)
    if inicio is None:
        return []
    filas, servicio, actual = [], "", None
    for nodo in inicio.find_all_next(["h2", "h3", "h4", "p"]):
        if nodo.name == "h2":
            break
        texto = limpiar(nodo.get_text(" "))
        if nodo.name in ("h3", "h4"):
            servicio = texto.rstrip(":")
            continue
        if "->" in texto:
            origen, destino = (limpiar(x) for x in texto.split("->", 1))
            actual = {"servicio": servicio, "origen": origen, "destino": destino,
                      "costo_mxn": "", "duracion_min": "", "ruta": "",
                      "fecha_consulta": fecha, "url": URL}
            filas.append(actual)
            continue
        if actual is None:
            continue
        if "Costo" in texto and not actual["costo_mxn"]:
            actual["costo_mxn"] = a_numero(texto)
        if "Duración" in texto and not actual["duracion_min"]:
            actual["duracion_min"] = a_minutos(texto.split("Duración", 1)[1])
        if re.match(r"\W*Ruta\s+\d+\s*:", texto) and not actual["ruta"]:
            actual["ruta"] = limpiar(re.sub(r"^\W+", "", texto))
    return filas


def escribir(destino: Path, columnas: list[str], filas: list[dict]) -> None:
    with open(destino, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=columnas)
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"  {len(filas)} renglones en {destino.relative_to(comun.RAIZ)}")


def main() -> None:
    carpeta = comun.carpeta_fuente(TIPO, CARPETA)
    (carpeta / "paginas").mkdir(exist_ok=True)
    nombre = "paginas/estacion_teya_merida.html"
    ruta = comun.descargar(URL, carpeta, nombre, FICHA, nota="Guía de la estación Mérida-Teya.")
    fecha = next(a["descargado_utc"] for a in comun.leer_procedencia(carpeta)["archivos"]
                 if a["archivo"] == nombre)
    sopa = BeautifulSoup(ruta.read_bytes(), "html.parser")
    salida = comun.carpeta_fuente(TIPO, CARPETA, base=comun.PARA_ETL)
    escribir(salida / "tarifas_desde_teya.csv", COL_TARIFAS, extraer_tarifas(sopa, fecha))
    escribir(salida / "conexiones_transporte.csv", COL_CONEXIONES, extraer_conexiones(sopa, fecha))


if __name__ == "__main__":
    main()
