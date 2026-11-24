"""Subtema 2, SIEGY: boletines estadísticos del Gobierno de Yucatán.

Baja los tres boletines en PDF tal cual a datos/originales/02_siegy/ y pasa
sus indicadores numéricos a una tabla larga en datos/para-etl/02_siegy/.

Los boletines son infografías de una sola página. Cada indicador de la lista
INDICADORES lleva el fragmento de texto del PDF que lo respalda; el script
comprueba con PyMuPDF que ese fragmento aparece en la página indicada antes
de escribirlo. Si un fragmento no aparece, se detiene: así ningún valor entra
a la tabla sin estar en el documento. Las barras de las gráficas que no
tienen etiqueta numérica no se leen ni se estiman.

Uso, desde la raíz del repositorio:
    python src/02_siegy.py
"""

from __future__ import annotations

import csv
import re
import sys
from pathlib import Path

import fitz  # PyMuPDF

sys.path.insert(0, str(Path(__file__).resolve().parent))
import comun  # noqa: E402

TIPO = "02_siegy"
BASE_URL = "https://datos.yucatan.gob.mx/storage/boletines/archivos/2025/"
COLUMNAS = ["indicador", "valor", "unidad", "periodo", "territorio", "pagina", "fuente_archivo"]

FICHA_COMUN = {
    "institucion": "Gobierno del Estado de Yucatán, Secretaría de Planeación (SEPLAN), "
                   "Sistema de Información Estadística y Geográfica del Estado de Yucatán (SIEGY)",
    "licencia": "Sin licencia explícita publicada en datos.yucatan.gob.mx (revisado el 2026-11-24); "
                "publicación oficial de acceso público. Se cita la fuente primaria de cada dato.",
    "acceso": "Descarga directa del PDF desde https://datos.yucatan.gob.mx/boletines",
}

# (carpeta, archivo, id, nombre)
BOLETINES = [
    ("2.1_boletin_aviacion_2025_12", "Boletin_2025_12.pdf", "E8-02.1",
     "SIEGY, Boletín 12 2025: Día de la Aviación Civil"),
    ("2.2_boletin_turismo_2025_09", "Boletin_2025_09.pdf", "E8-02.2",
     "SIEGY, Boletín 9 2025: Día Mundial del Turismo"),
    ("2.3_boletin_resiliencia_turismo_2025_02", "Boletin_2025_02.pdf", "E8-02.3",
     "SIEGY, Boletín 2 2025: Día Mundial de la Resiliencia del Turismo"),
]

# Por boletín: (indicador, valor, unidad, periodo, territorio, página, fragmento del PDF).
# El valor se transcribe tal como aparece; solo se quitan separadores de miles.
INDICADORES = {
    "Boletin_2025_12.pdf": [
        ("Pasajeros aéreos", 191.2, "millones de pasajeros", "2025", "México", 1,
         "191.2"),
        ("Carga aérea", 1.23, "millones de toneladas", "2025", "México", 1,
         "1.23"),
        ("Pasajeros del aeropuerto (cifra redondeada del recuadro)", 3.9, "millones de pasajeros",
         "2025", "Mérida, aeropuerto", 1, "3.9"),
        ("Pasajeros acumulados del aeropuerto (etiqueta de la gráfica)", 3951827, "pasajeros",
         "ene-dic 2025", "Mérida, aeropuerto", 1, "3,951,827"),
        ("Pasajeros del aeropuerto en el mes de mayor afluencia", 379993, "pasajeros",
         "dic 2025", "Mérida, aeropuerto", 1, "379,993 pasajeros"),
        ("Variación anual de pasajeros del aeropuerto", 11.6, "por ciento",
         "dic 2025 vs dic 2024", "Mérida, aeropuerto", 1, "incremento de 11.6%"),
        ("Lugar del aeropuerto por mayor incremento anual de pasajeros", 1, "lugar",
         "dic 2024 a dic 2025", "Mérida, aeropuerto", 1, "Primer lugar"),
        ("Carga aérea del aeropuerto", 25438, "toneladas", "2025", "Mérida, aeropuerto", 1,
         "25,438\nToneladas"),
        ("Carga aérea acumulada del aeropuerto (etiqueta de la gráfica)", 25438.7, "toneladas",
         "ene-dic 2025", "Mérida, aeropuerto", 1, "25,438.7"),
        ("Carga aérea del aeropuerto en el mes de mayor carga", 2485, "toneladas",
         "oct 2025", "Mérida, aeropuerto", 1, "2,485 toneladas"),
        ("Variación anual de carga aérea del aeropuerto", 20.7, "por ciento",
         "oct 2025 vs oct 2024", "Mérida, aeropuerto", 1, "incremento de 20.7%"),
    ],
    "Boletin_2025_09.pdf": [
        ("Posición nacional de Mérida en los premios Travel + Leisure World's Best Awards", 3,
         "lugar", "2025", "Mérida", 1, "tercera posición"),
        ("Turistas con pernocta", 1543105, "turistas", "ene-jul 2025", "Yucatán", 1,
         "1 millón 543 mil 105"),
        ("Variación anual de turistas con pernocta", 11, "por ciento",
         "ene-jul 2025 vs ene-jul 2024", "Yucatán", 1, "incremento de 11%"),
        ("Pasajeros aéreos del Aeropuerto Internacional de Mérida", 2562355, "pasajeros",
         "ene-ago 2025", "Mérida, aeropuerto", 1, "2 millones \n562 mil 355"),
        ("Pasajeros de cruceros", 281242, "pasajeros", "ene-jul 2025",
         "Yucatán, puerto de Progreso", 1, "281 mil 242"),
        ("Variación anual de pasajeros de cruceros", 84, "por ciento",
         "ene-jul 2025 vs ene-jul 2024", "Yucatán, puerto de Progreso", 1, "incremento \nanual de 84%"),
        ("Lugar en el ranking de crecimiento de pasajeros de cruceros en el Golfo", 1, "lugar",
         "ene-jul 2025", "Yucatán", 1, "primer lugar del ranking"),
        ("Visitantes a zonas arqueológicas", 1767318, "visitantes", "ene-jul 2025", "Yucatán", 1,
         "1 millón 767 mil 318"),
        ("Lugar nacional en visitantes a zonas arqueológicas", 1, "lugar", "ene-jul 2025",
         "Yucatán", 1, "en el primer lugar con \nmayores visitantes"),
        ("Años consecutivos en primer lugar nacional en visitantes a zonas arqueológicas", 6,
         "años", "ene-jul 2025", "Yucatán", 1, "por sexto año \nconsecutivo"),
        ("Participación de Chichén Itzá en los visitantes a zonas arqueológicas del estado", 77.3,
         "por ciento", "ene-jul 2025", "Yucatán, Chichén Itzá", 1, "77.3%"),
    ],
    "Boletin_2025_02.pdf": [
        ("Posición nacional de Mérida en los premios Travel + Leisure World's Best Awards", 4,
         "lugar", "2024", "Mérida", 1, "cuarta posición"),
        ("Años consecutivos de Mérida entre las ciudades más importantes de México "
         "(Travel + Leisure)", 7, "años", "2024", "Mérida", 1, "séptimo año consecutivo"),
        ("Turistas con pernocta", 2162320, "turistas", "ene-nov 2024", "Yucatán", 1,
         "2 millones \n162 mil 320"),
        ("Turistas con pernocta nacionales (participación)", 80.1, "por ciento", "ene-nov 2024",
         "Yucatán", 1, "80.1%"),
        ("Turistas con pernocta extranjeros (participación)", 19.9, "por ciento", "ene-nov 2024",
         "Yucatán", 1, "19.9%"),
        ("Turistas con pernocta (etiqueta de la gráfica, máximo antes de 2020)", 1862786,
         "turistas", "ene-nov 2019", "Yucatán", 1, "1,862,786"),
        ("Turistas con pernocta (etiqueta de la gráfica, mínimo)", 696191, "turistas",
         "ene-nov 2020", "Yucatán", 1, "696,191"),
        ("Turistas con pernocta (etiqueta de la gráfica)", 2162320, "turistas", "ene-nov 2024",
         "Yucatán", 1, "2,162,320"),
        ("Pasajeros aéreos del Aeropuerto Internacional de Mérida", 3716588, "pasajeros", "2024",
         "Mérida, aeropuerto", 1, "3 millones 716 mil 588"),
        ("Pasajeros de cruceros", 317514, "pasajeros", "2024", "Yucatán, puerto de Progreso", 1,
         "317 mil 514"),
        ("Variación anual de pasajeros de cruceros", 21.7, "por ciento", "2024 vs 2023",
         "Yucatán, puerto de Progreso", 1, "incremento anual de 21.7%"),
        ("Lugar en el ranking de crecimiento de pasajeros de cruceros", 7, "lugar", "2024",
         "Yucatán", 1, "séptimo lugar del \nranking"),
        ("Visitantes a zonas arqueológicas", 2551454, "visitantes", "ene-nov 2024", "Yucatán", 1,
         "2 millones 551 mil \n454"),
        ("Visitantes a zonas arqueológicas (etiqueta de la gráfica por entidad)", 2551454,
         "visitantes", "ene-nov 2024", "Yucatán", 1, "2,551,454"),
        ("Visitantes a zonas arqueológicas, promedio nacional por entidad (etiqueta de la gráfica)",
         283332, "visitantes", "ene-nov 2024", "México, promedio por entidad", 1, "283,332"),
        ("Visitantes a zonas arqueológicas, entidad con menos visitantes (etiqueta de la gráfica)",
         1042, "visitantes", "ene-nov 2024", "Sonora", 1, "1,042"),
        ("Lugar nacional en visitantes a zonas arqueológicas", 1, "lugar", "ene-nov 2024",
         "Yucatán", 1, "en el primer lugar con \nmayores visitantes"),
        ("Años consecutivos en primer lugar nacional en visitantes a zonas arqueológicas", 5,
         "años", "ene-nov 2024", "Yucatán", 1, "por quinto año \nconsecutivo"),
        ("Participación de Chichén Itzá en los visitantes a zonas arqueológicas del estado", 79.1,
         "por ciento", "ene-nov 2024", "Yucatán, Chichén Itzá", 1, "79.1%"),
        ("Participación de Uxmal en los visitantes a zonas arqueológicas del estado", 9.4,
         "por ciento", "ene-nov 2024", "Yucatán, Uxmal", 1, "9.4%"),
        ("Participación de Ek Balam en los visitantes a zonas arqueológicas del estado", 5.1,
         "por ciento", "ene-nov 2024", "Yucatán, Ek Balam", 1, "5.1%"),
        ("Visitantes en Chichén Itzá", 2018184, "visitantes", "ene-nov 2024",
         "Yucatán, Chichén Itzá", 1, "2, 018,184"),
        ("Visitantes en Uxmal", 239558, "visitantes", "ene-nov 2024", "Yucatán, Uxmal", 1,
         "239,558"),
        ("Visitantes en Ek Balam", 130515, "visitantes", "ene-nov 2024", "Yucatán, Ek Balam", 1,
         "130, 515"),
    ],
}


def normalizar(texto: str) -> str:
    """Compacta espacios y saltos para comparar fragmentos con el texto del PDF."""
    return re.sub(r"\s+", " ", texto).strip()


def extraer(pdf: Path, filas: list[tuple]) -> list[dict]:
    doc = fitz.open(pdf)
    paginas = {i + 1: normalizar(p.get_text()) for i, p in enumerate(doc)}
    salida = []
    for indicador, valor, unidad, periodo, territorio, pagina, fragmento in filas:
        if normalizar(fragmento) not in paginas.get(pagina, ""):
            raise ValueError(f"{pdf.name}: no aparece «{fragmento}» en la página {pagina}")
        salida.append({
            "indicador": indicador, "valor": valor, "unidad": unidad, "periodo": periodo,
            "territorio": territorio, "pagina": pagina, "fuente_archivo": pdf.name,
        })
    return salida


def main() -> None:
    for carpeta_nombre, archivo, ident, nombre in BOLETINES:
        url = BASE_URL + archivo
        print(f"{ident} {nombre}")
        ficha = {"id": ident, "nombre": nombre, "url_original": url, **FICHA_COMUN}
        carpeta = comun.carpeta_fuente(TIPO, carpeta_nombre)
        pdf = comun.descargar(url, carpeta, archivo, ficha,
                              nota="Infografía de una página publicada por el SIEGY.")
        filas = extraer(pdf, INDICADORES[archivo])
        destino = comun.carpeta_fuente(TIPO, carpeta_nombre, base=comun.PARA_ETL) / "indicadores.csv"
        with open(destino, "w", encoding="utf-8", newline="") as f:
            escritor = csv.DictWriter(f, fieldnames=COLUMNAS)
            escritor.writeheader()
            escritor.writerows(filas)
        print(f"  {len(filas)} indicadores en {destino.relative_to(comun.RAIZ)}")


if __name__ == "__main__":
    main()
