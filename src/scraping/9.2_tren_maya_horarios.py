"""Subtema 9, fuente 9.2: horarios oficiales del Tren Maya.

Baja https://www.trenmaya.gob.mx/horarios.php (una sola página), la guarda tal
cual en datos/originales/09_scraping/<carpeta>/paginas/ con su registro en
procedencia.json y convierte la tabla «Horario de Trenes» a
datos/para-etl/09_scraping/<carpeta>/horarios_tren_maya.csv, un renglón por
tramo de cada circulación.

La página no publica días de operación ni tipo de servicio por circulación;
esas columnas quedan como «no indicado». Tampoco tiene fecha de vigencia, por
eso cada renglón lleva la fecha de consulta.

El sitio no publica robots.txt (la ruta responde con la página de error) ni
términos de uso; solo un aviso de privacidad
(https://www.trenmaya.gob.mx/AvisoPrivacidad.php). Revisado el 2026-11-24.

Uso, desde la raíz del repositorio:
    python src/scraping/9.2_tren_maya_horarios.py
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
CARPETA = "9.2_tren_maya_horarios"
URL = "https://www.trenmaya.gob.mx/horarios.php"
NO_INDICADO = "no indicado"
COLUMNAS = ["circulacion", "tramo", "estacion_origen", "estacion_destino", "hora_salida",
            "hora_llegada", "tiempo_recorrido", "tiempo_total_circulacion", "tipo_servicio",
            "dias", "fecha_consulta", "url"]

FICHA = {
    "id": "E8-09.2",
    "nombre": "Tren Maya, horarios oficiales",
    "institucion": "Tren Maya S.A. de C.V.",
    "url_original": URL,
    "licencia": "Sin licencia ni términos de uso publicados en trenmaya.gob.mx (revisado el "
                "2026-11-24); sin robots.txt. Información pública de una empresa del Estado. "
                "Uso académico, sin fines comerciales.",
    "acceso": "Scraping de una página con requests y BeautifulSoup.",
}


def limpiar(texto: str) -> str:
    return re.sub(r"\s+", " ", texto).strip().rstrip(".").strip()


def separar_ruta(ruta: str) -> tuple[str, str]:
    """'Palenque – San Francisco Campeche' o 'Chetumal-Escarcega' -> (origen, destino)."""
    partes = re.split(r"\s*[–—]\s*|(?<=\w)-(?=\w)", ruta, maxsplit=1)
    if len(partes) != 2:
        return ruta, ""
    return limpiar(partes[0]), limpiar(partes[1])


def expandir_tabla(tabla) -> list[list[str]]:
    """Convierte la tabla HTML en una cuadrícula, repitiendo las celdas con rowspan."""
    pendientes: dict[int, tuple[int, str]] = {}  # columna -> (renglones que faltan, texto)
    cuadricula = []
    for tr in tabla.find("tbody").find_all("tr"):
        celdas = iter(tr.find_all("td"))
        renglon, col = [], 0
        while True:
            if col in pendientes:
                faltan, texto = pendientes[col]
                renglon.append(texto)
                if faltan > 1:
                    pendientes[col] = (faltan - 1, texto)
                else:
                    del pendientes[col]
                col += 1
                continue
            celda = next(celdas, None)
            if celda is None:
                break
            texto = limpiar(celda.get_text(" "))
            extension = int(celda.get("rowspan", 1))
            if extension > 1:
                pendientes[col] = (extension - 1, texto)
            renglon.append(texto)
            col += 1
        if renglon:
            cuadricula.append(renglon + [""] * (6 - len(renglon)))
    return cuadricula


def extraer(html: bytes, fecha: str) -> list[dict]:
    """Un renglón por tramo. Las columnas de tiempo se copian tal como están en la
    página: en algunas circulaciones (303 a 308 y 501 a 604) la página deja vacío
    «Tiempo de recorrido» y pone el tiempo del tramo en «Tiempo total»."""
    tabla = BeautifulSoup(html, "html.parser").find("table")
    filas, anterior, tramo = [], None, 0
    for circulacion, ruta, salida, llegada, recorrido, total in expandir_tabla(tabla):
        tramo = tramo + 1 if circulacion == anterior else 1
        anterior = circulacion
        origen, destino = separar_ruta(ruta)
        filas.append({
            "circulacion": circulacion, "tramo": tramo,
            "estacion_origen": origen, "estacion_destino": destino,
            "hora_salida": salida, "hora_llegada": llegada,
            "tiempo_recorrido": recorrido, "tiempo_total_circulacion": total,
            "tipo_servicio": NO_INDICADO, "dias": NO_INDICADO,
            "fecha_consulta": fecha, "url": URL,
        })
    return filas


def main() -> None:
    carpeta = comun.carpeta_fuente(TIPO, CARPETA)
    (carpeta / "paginas").mkdir(exist_ok=True)
    nombre = "paginas/horarios.html"
    ruta = comun.descargar(URL, carpeta, nombre, FICHA, nota="Tabla «Horario de Trenes».")
    fecha = next(a["descargado_utc"] for a in comun.leer_procedencia(carpeta)["archivos"]
                 if a["archivo"] == nombre)
    filas = extraer(ruta.read_bytes(), fecha)
    destino = comun.carpeta_fuente(TIPO, CARPETA, base=comun.PARA_ETL) / "horarios_tren_maya.csv"
    with open(destino, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS)
        escritor.writeheader()
        escritor.writerows(filas)
    print(f"  {len(filas)} tramos en {destino.relative_to(comun.RAIZ)}")


if __name__ == "__main__":
    main()
