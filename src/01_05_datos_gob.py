"""Descarga las fuentes de datos.gob.mx de los subtemas 1 y 5.1.

Usa la API oficial CKAN DataStore de datos.gob.mx. El servidor de archivos
(repodatos.atdt.gob.mx) rechaza las descargas automatizadas, así que cada
recurso se baja completo o filtrado por entidad desde la API y se guarda tal
cual la devuelve, en JSON.

Alcance territorial: los cinco estados del Tren Maya (Campeche 04, Chiapas 07,
Quintana Roo 23, Tabasco 27 y Yucatán 31) a nivel municipal, y Yucatán a
nivel AGEB y localidad.

Uso: python src/01_05_datos_gob.py
"""

import comun

ESTADOS_NUM = [4, 7, 23, 27, 31]
ESTADOS_TXT = ["4", "04", "7", "07", "23", "27", "31"]
LICENCIA = "CC-BY-4.0"

FUENTES = [
    {
        "tipo": "01_datos_gob", "carpeta": "1.1_conapo_marginacion",
        "ficha": {"id": "E8-01.1", "nombre": "CONAPO, Índices de marginación 2020",
                  "institucion": "Secretaría Técnica del Consejo Nacional de Población (CONAPO)",
                  "url_original": "https://www.datos.gob.mx/dataset/indices_marginacion",
                  "licencia": LICENCIA},
        "recursos": [
            ("551d8f48-5d0c-4d11-964a-e2911f732615", "imm_2020_municipal_5_estados.json",
             {"CVE_ENT": ESTADOS_NUM}, "Índice de marginación municipal 2020"),
            ("9600f414-c1ba-408a-8dd6-7f73d76601d4", "imu_2020_ageb_yucatan.json",
             {"ENT": 31}, "Índice de marginación urbana por AGEB 2020"),
        ],
    },
    {
        "tipo": "01_datos_gob", "carpeta": "1.2_conapo_proyecciones",
        "ficha": {"id": "E8-01.2", "nombre": "CONAPO, Proyecciones de población",
                  "institucion": "Secretaría Técnica del Consejo Nacional de Población (CONAPO)",
                  "url_original": "https://www.datos.gob.mx/dataset/proyecciones-de-poblacion",
                  "licencia": LICENCIA},
        "recursos": [
            ("3c3092be-583e-4490-8c23-67ef9a64b198", "pobproy_quinq_municipal_5_estados.json",
             {"CLAVE_ENT": ESTADOS_NUM}, "Población a mitad de año por municipio, sexo y grupo quinquenal"),
            ("e9160552-769b-41ee-88d1-afc765552608", "pobproy_inddemo_municipal_5_estados.json",
             {"CLAVE_ENT": ESTADOS_NUM}, "Indicadores demográficos municipales"),
        ],
    },
    {
        "tipo": "01_datos_gob", "carpeta": "1.3_conapo_accesibilidad",
        "ficha": {"id": "E8-01.3", "nombre": "CONAPO, Accesibilidad a centros urbanos",
                  "institucion": "Secretaría Técnica del Consejo Nacional de Población (CONAPO)",
                  "url_original": "https://www.datos.gob.mx/dataset/accesibilidad_centros_urbanos",
                  "licencia": LICENCIA},
        "recursos": [
            ("a1555b2e-a10c-477f-9327-662b56a5d45e", "acu_municipal_5_estados.json",
             {"ENT": ESTADOS_TXT}, "Accesibilidad a centros urbanos por municipio"),
            ("437bb9b4-b94a-4046-ab0a-61a76fcaa72c", "acu_localidad_yucatan.json",
             {"ENT": 31}, "Accesibilidad a centros urbanos por localidad"),
        ],
    },
    {
        "tipo": "05_solicitud_datos", "carpeta": "5.1_tren_maya_pasajeros",
        "ficha": {"id": "E8-05.1", "nombre": "Tren Maya, prestación del servicio ferroviario de pasajeros",
                  "institucion": "Tren Maya, S.A. de C.V.",
                  "url_original": "https://www.datos.gob.mx/dataset/prestacion_servicio_ferroviario_pasajeros",
                  "licencia": LICENCIA},
        "recursos": [
            ("0c27e6cc-14bb-4a95-a37f-e42994944af2", "pasajeros_2024.json", None, "Pasajeros transportados 2024"),
            ("6417a5ec-0cf7-4fd4-8840-f1a39c863873", "pasajeros_2025.json", None, "Pasajeros transportados 2025"),
            ("7da5f7f3-b469-42d0-9052-6a5f5943b6f3", "pasajeros_2026.json", None, "Pasajeros transportados 2026"),
            ("2037ce86-cfc0-43a4-8916-db7f6c1d1684", "boletos_2024.json", None, "Boletos vendidos 2024"),
            ("1b86eabc-f9aa-47fe-902e-61df6c54518f", "boletos_2025.json", None, "Boletos vendidos 2025"),
            ("98ebdbe0-086f-47a9-8ad9-038be965de79", "boletos_2026.json", None, "Boletos vendidos 2026"),
            ("24e21d49-740d-436b-b6a2-dc6838214038", "kilometros_2025.json", None, "Kilómetros recorridos 2025"),
            ("94b9259f-f011-41b6-80ae-b1bafbab8228", "kilometros_2026.json", None, "Kilómetros recorridos 2026"),
        ],
    },
]


def main() -> None:
    for f in FUENTES:
        print(f["ficha"]["id"], f["ficha"]["nombre"])
        carpeta = comun.carpeta_fuente(f["tipo"], f["carpeta"])
        paquete = comun.ckan_paquete(f["ficha"]["url_original"].rsplit("/", 1)[1])
        ficha = dict(f["ficha"], metadata_modified=paquete.get("metadata_modified"),
                     acceso="API CKAN DataStore de datos.gob.mx")
        recursos_por_id = {r["id"]: r for r in paquete["resources"]}
        for rid, nombre, filtros, nota in f["recursos"]:
            url_recurso = recursos_por_id.get(rid, {}).get("url", "")
            comun.ckan_datastore(rid, carpeta, nombre, ficha, filtros=filtros,
                                 nota=f"{nota}. Archivo del catálogo: {url_recurso}")


if __name__ == "__main__":
    main()
