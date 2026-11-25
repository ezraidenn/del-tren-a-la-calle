"""Descarga las fuentes del INEGI del subtema 3.

- 3.1 DENUE noviembre de 2019 y 3.2 DENUE mayo de 2025: un ZIP por estado del
  Tren Maya (Campeche 04, Chiapas 07, Quintana Roo 23, Tabasco 27, Yucatán 31).
  Son la entrada de procesamiento/03_denue_datamart.
- 3.3 Censo de Población y Vivienda 2020, resultados por AGEB y manzana urbana
  de Yucatán, y los polígonos de sus AGEB urbanas (Marco Geoestadístico).

Los ZIP se guardan sin descomprimir, tal como los publica el INEGI.

Uso: python src/03_inegi.py
"""

import comun

ESTADOS = ["04", "07", "23", "27", "31"]
LICENCIA = "Términos de libre uso de la información del INEGI"
URL_LICENCIA = "https://www.inegi.org.mx/inegi/terminos.html"
INSTITUCION = "Instituto Nacional de Estadística y Geografía (INEGI)"
URL_MG_AGEB = "https://gaia.inegi.org.mx/wscatgeo/v2/geo/agebu/31"


def denue(carpeta_nombre: str, ident: str, nombre: str, edicion: str, sufijo: str) -> None:
    carpeta = comun.carpeta_fuente("03_inegi", carpeta_nombre)
    ficha = {"id": ident, "nombre": nombre, "institucion": INSTITUCION,
             "url_original": f"https://www.inegi.org.mx/contenidos/masiva/denue/{edicion}/denue_31_{sufijo}_csv.zip",
             "licencia": LICENCIA, "url_licencia": URL_LICENCIA,
             "acceso": "Descarga masiva del DENUE, un ZIP por entidad"}
    print(ident, nombre)
    for ent in ESTADOS:
        archivo = f"denue_{ent}_{sufijo}_csv.zip"
        url = f"https://www.inegi.org.mx/contenidos/masiva/denue/{edicion}/{archivo}"
        comun.descargar(url, carpeta, archivo, ficha, nota=f"Entidad {ent}")


def main() -> None:
    denue("3.1_denue_2019_11", "E8-03.1", "INEGI, DENUE noviembre 2019", "2019_11", "1119")
    denue("3.2_denue_2025_05", "E8-03.2", "INEGI, DENUE mayo 2025", "2025_05", "0525")

    carpeta = comun.carpeta_fuente("03_inegi", "3.3_censo_2020_ageb")
    url = ("https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/"
           "ageb_manzana/ageb_mza_urbana_31_cpv2020_csv.zip")
    ficha = {"id": "E8-03.3", "nombre": "INEGI, Censo 2020, AGEB y manzana urbana (Yucatán)",
             "institucion": INSTITUCION, "url_original": url,
             "licencia": LICENCIA, "url_licencia": URL_LICENCIA,
             "acceso": "Datos abiertos del Censo de Población y Vivienda 2020"}
    print(ficha["id"], ficha["nombre"])
    comun.descargar(url, carpeta, "ageb_mza_urbana_31_cpv2020_csv.zip", ficha, nota="Entidad 31")
    # Polígonos de las AGEB urbanas: permiten asignar cvegeo_ageb a cualquier punto.
    comun.descargar(URL_MG_AGEB, carpeta, "mg_ageb_urbana_31.geojson", ficha,
                    nota=("Polígonos de AGEB urbanas de Yucatán, servicio web del Catálogo Único de Claves "
                          "Geoestadísticas del INEGI (Marco Geoestadístico de diciembre de 2025, población del "
                          "Censo 2020), EPSG:4326"))


if __name__ == "__main__":
    main()
