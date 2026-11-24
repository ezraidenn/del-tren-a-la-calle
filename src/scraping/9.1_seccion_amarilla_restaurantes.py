"""Subtema 9, fuente 9.1: restaurantes de Mérida en Sección Amarilla.

Recorre el listado público
https://www.seccionamarilla.com.mx/resultados/restaurantes/yucatan/merida/<n>
página por página (máximo MAX_PAGINAS, con PAUSA segundos entre solicitudes),
guarda cada página HTML tal cual en datos/originales/09_scraping/<carpeta>/paginas/
y la registra en procedencia.json. Luego arma la tabla de negocios en
datos/para-etl/09_scraping/<carpeta>/restaurantes_merida.csv.

robots.txt del sitio (revisado el 2026-11-24) permite /resultados/. Los
términos y condiciones (https://www.seccionamarilla.com.mx/terminos-y-condiciones)
regulan la contratación de anuncios y no prohíben la consulta automatizada.

Privacidad: la tabla no guarda teléfonos, correos, sitios web ni nombres de
personas. Algunos anuncios están a nombre de una persona física; en esos casos
el nombre se deja vacío y la columna nombre_omitido vale 1. Las páginas HTML
crudas sí contienen los teléfonos publicados por los anunciantes.

Uso, desde la raíz del repositorio:
    python src/scraping/9.1_seccion_amarilla_restaurantes.py
"""

from __future__ import annotations

import csv
import re
import sys
import time
import unicodedata
from pathlib import Path

from bs4 import BeautifulSoup

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import comun  # noqa: E402

TIPO = "09_scraping"
CARPETA = "9.1_seccion_amarilla_restaurantes"
URL_BASE = "https://www.seccionamarilla.com.mx/resultados/restaurantes/yucatan/merida/{}"
MAX_PAGINAS = 20
PAUSA = 1.5
COLUMNAS = ["id_anuncio", "nombre", "nombre_omitido", "categoria", "direccion", "colonia",
            "municipio", "codigo_postal", "lat", "lon", "pagina", "url_ficha", "fecha_consulta"]

FICHA = {
    "id": "E8-09.1",
    "nombre": "Sección Amarilla, restaurantes de Mérida",
    "institucion": "Anuncios en Directorios S.A. de C.V. (Sección Amarilla)",
    "url_original": "https://www.seccionamarilla.com.mx/resultados/restaurantes/yucatan/merida/1",
    "licencia": "Sin licencia de datos abiertos. robots.txt permite /resultados/ "
                "(https://www.seccionamarilla.com.mx/robots.txt); los términos "
                "(https://www.seccionamarilla.com.mx/terminos-y-condiciones) no prohíben la "
                "consulta automatizada. Uso académico, sin fines comerciales.",
    "acceso": "Scraping del listado público con requests y BeautifulSoup, "
              f"máximo {MAX_PAGINAS} páginas y {PAUSA} s de pausa entre solicitudes.",
}

# Palabras que delatan un negocio. Si el nombre tiene alguna, no se trata
# como nombre de persona.
PALABRAS_NEGOCIO = set("""
RESTAURANTE RESTAURANTES RESTAURANT RISTORANTE REST CAFE CAFES CAFETERIA CAFETERIAS COCINA
COCINAS PIZZA PIZZAS PIZZERIA TACOS TAQUERIA LONCHERIA COMIDA COMIDAS BAR GRILL MARISCOS
MARISCO POLLO POLLOS SUSHI BURGER BURGERS HAMBURGUESAS SANBORNS VIPS PLAZA GRUPO SAPI CASA
CANTINA CENADURIA FONDA BISTRO BISTROT PANADERIA PASTELERIA HELADOS NEVERIA SORBETES DULCES
CARNES ASADERO ASADO BUFFET BANQUETES EXPRESS COMEDOR ANTOJITOS COCTELERIA PESCADOS TORTAS
SANDWICH SALADS KITCHEN FOOD COFFEE TEA JUGOS COCTELES SUCURSAL CENTRO MERIDA YUCATAN
INTERNACIONAL REGIONAL MEXICANA MEXICAN CUISINE GOURMET HOUSE HAUS HACIENDA MERCADO
COMERCIALIZADORA DISCOTECA PROYECTOS EVENTOS DISENOS GASTROPUB CERVECERIA CERVETECA
""".split())

# Conectores que pueden aparecer en nombres de persona («del Socorro», «de la Cruz»).
CONECTORES = {"DE", "DEL", "LA", "LAS", "LOS", "Y"}

# Nombres de pila y apellidos frecuentes en México y en Yucatán, más apellidos
# frecuentes de Asia oriental. Sirven para reconocer anuncios a nombre de una
# persona física; ante la duda se omite el nombre.
NOMBRES_PERSONA = set("""
AARON ABEL ABRAHAM ADALBERTO ADAN ADOLFO ADRIAN ADRIANA AGUSTIN ALAN ALBERTO ALEJANDRA
ALEJANDRO ALFONSO ALFREDO ALICIA ALINE ALMA ANA ANDREA ANDRES ANGEL ANGELICA ANTONIO ARACELI
ARACELLY ARMANDO ARTURO ASUNCION AURORA BEATRIZ BENJAMIN BERNARDO BERTHA BLANCA BRENDA CAMILO
CARLOS CARMEN CAROLINA CECILIA CESAR CLAUDIA CONSUELO CRISTINA CRISTIAN DANIEL DANIELA DAVID
DIANA DIEGO EDGAR EDUARDO ELENA ELIZABETH ELSA ELY EMILIO ENRIQUE ERIKA ERNESTO ESTEBAN ESTHER
EVA EVELIA FABIOLA FATIMA FELIPE FERNANDA FERNANDO FRANCISCO FREDDY FULGENCIO GABRIEL GABRIELA
GEORGE GERARDO GILBERTO GISELA GLORIA GRACIELA GUADALUPE GUILLERMO GUSTAVO HECTOR HUGO IGNACIO
IRMA ISAAC ISABEL IVAN JAIME JAVIER JESUS JOAQUIN JORGE JOSE JOSEFINA JOSUE JUAN JUANA JULIA
JULIO KARLA KARINA KARLO LAURA LETICIA LILIANA LORENA LOURDES LUCIA LUIS LUZ MA MANUEL MARCO
MARCOS MARGARITA MARIA MARIANA MARILU MARIO MARISOL MARTHA MARTIN MAURICIO MELINA MIGUEL MIRIAM
MONICA NANCY NICOLAS NINFA NOEMI NORMA OCTAVIO OLGA OMAR OSCAR PABLO PATRICIA PAULINA PEDRO
RAFAEL RAMON RAQUEL RAUL REBECA RICARDO ROBERTO RODRIGO ROSA ROSARIO RUBEN SAID SAIDA SALVADOR
SAMUEL SANDRA SANTIAGO SARA SERGIO SILVIA SOCORRO SOFIA SONIA SUSANA TERESA TOMAS VALENTINA
VALERIA VERONICA VICENTE VICTOR VICTORIA VIRGINIA WILBERT WILLIAM WILMER XIMENA YOLANDA
ACHACH ACOSTA AGUILAR AKE ALPUCHE ALVAREZ AMAYA AMBROSIO ARCE ARCEO ARELLANO AVILA BACELIS
BAQUEDANO BARRAGAN BASTARRACHEA BLANCO BRICENO BUENFIL CABALLERO CABRERA CALLEJAS CAMARA
CAMPOS CANCHE CANUL CARBAJAL CASARES CASTANEDA CASTELLANOS CASTILLO CASTRO CAUICH CEJAS CEN
CENTENO CERVERA CHAN CHEHADE CONCHA CONTRERAS CORREA COUOH CRUZ CUEVAS DELGADO DIAZ DORANTES
DURAN DZUL ESCALANTE FLORES GAMBOA GARCIA GOMEZ GONZALEZ GUEMEZ GUTIERREZ HERNANDEZ HERRERA
JIMENEZ LOPEZ LORIA MARTINEZ MEDINA MENDOZA MOGUEL MOLINA MORALES MORENO NOH ORTIZ PAVIA PECH
PENICHE PEREYRA PEREZ PONCE POOT QUIJANO RAMIREZ REYES RIVERO RODRIGUEZ ROMERO ROSADO RUIZ
SALAZAR SANCHEZ SILVA SOLIS TORRES TUN VARGAS VAZQUEZ XACUR
CAO CHEN GUO HUANG JEON KIM LEE LI LIANG LIU PARK WANG WU XU YANG ZHANG ZHAO ZHOU
""".split())


def sin_acentos(texto: str) -> str:
    base = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in base if not unicodedata.combining(c)).upper()


def parece_persona(nombre: str) -> bool:
    """True si el nombre del anuncio parece el de una persona física."""
    if re.search(r"[0-9&'.´`,/-]", nombre):
        return False
    palabras = re.findall(r"[A-Z]+", sin_acentos(nombre))
    if not 2 <= len(palabras) <= 6 or PALABRAS_NEGOCIO & set(palabras):
        return False
    return bool(NOMBRES_PERSONA & (set(palabras) - CONECTORES))


def separar_direccion(texto: str, municipio: str) -> dict:
    """Separa '33 505-A, ALCALA MARTIN, MERIDA, YUC, CP 97050' en sus partes."""
    vacio = {"direccion": "", "colonia": "", "municipio": municipio, "codigo_postal": ""}
    if not texto or "no disponible" in texto.lower():
        return vacio
    partes = [p.strip() for p in texto.split(",")]
    cp = ""
    if partes and re.fullmatch(r"CP\s*\d{5}", partes[-1]):
        cp = re.sub(r"\D", "", partes.pop())
    if partes and partes[-1].upper() in {"YUC", "YUCATAN", "YUCATÁN"}:
        partes.pop()
    if partes and municipio and partes[-1].upper() == municipio.upper():
        partes.pop()
    colonia = partes.pop() if len(partes) >= 2 else ""
    return {"direccion": ", ".join(partes), "colonia": colonia,
            "municipio": municipio, "codigo_postal": cp}


def extraer(html: bytes, pagina: int, fecha: str) -> list[dict]:
    sopa = BeautifulSoup(html, "html.parser")
    filas = []
    for art in sopa.select("article[data-dl-item-id]"):
        enlace = (art.select_one('a[data-item-category][href^="/informacion"]')
                  or art.select_one("a[data-item-category]"))
        nombre = (art.get("data-name") or "").strip()
        municipio = (enlace.get("data-business-city") if enlace else "") or ""
        omitir = parece_persona(nombre)
        fila = {
            "id_anuncio": art["data-dl-item-id"],
            "nombre": "" if omitir else nombre,
            "nombre_omitido": int(omitir),
            "categoria": (enlace.get("data-item-category") if enlace else "") or "",
            **separar_direccion(art.get("data-address", ""), municipio.strip()),
            "lat": art.get("data-lat", ""),
            "lon": art.get("data-lon", ""),
            "pagina": pagina,
            "url_ficha": ("https://www.seccionamarilla.com.mx" + enlace["href"])
            if enlace and enlace.get("href", "").startswith("/") and not omitir else "",
            "fecha_consulta": fecha,
        }
        filas.append(fila)
    return filas


def main() -> None:
    carpeta = comun.carpeta_fuente(TIPO, CARPETA)
    paginas = carpeta / "paginas"
    paginas.mkdir(exist_ok=True)
    vistos: set[str] = set()
    filas: list[dict] = []
    for n in range(1, MAX_PAGINAS + 1):
        nombre = f"paginas/restaurantes_merida_p{n:02d}.html"
        ruta = carpeta / nombre
        nueva = not ruta.exists()
        comun.descargar(URL_BASE.format(n), carpeta, nombre, FICHA,
                        nota=f"Página {n} del listado de restaurantes en Mérida.")
        fecha = next(a["descargado_utc"] for a in comun.leer_procedencia(carpeta)["archivos"]
                     if a["archivo"] == nombre)
        lote = [f for f in extraer(ruta.read_bytes(), n, fecha) if f["id_anuncio"] not in vistos]
        print(f"  página {n}: {len(lote)} negocios nuevos")
        if not lote:
            break
        vistos.update(f["id_anuncio"] for f in lote)
        filas.extend(lote)
        if nueva:
            time.sleep(PAUSA)

    destino = comun.carpeta_fuente(TIPO, CARPETA, base=comun.PARA_ETL) / "restaurantes_merida.csv"
    with open(destino, "w", encoding="utf-8", newline="") as f:
        escritor = csv.DictWriter(f, fieldnames=COLUMNAS)
        escritor.writeheader()
        escritor.writerows(filas)
    omitidos = sum(f["nombre_omitido"] for f in filas)
    print(f"  {len(filas)} negocios ({omitidos} con nombre omitido) en "
          f"{destino.relative_to(comun.RAIZ)}")


if __name__ == "__main__":
    main()
