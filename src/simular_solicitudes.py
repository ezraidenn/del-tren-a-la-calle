"""Genera las respuestas SIMULADAS a las 3 solicitudes de acceso a la información.

Las solicitudes 5.1 (Tren Maya), 5.2 (ATY, ruta R901) y 5.3 (Ayuntamiento de
Mérida, banquetas del Centro) piden datos que no son públicos. Mientras llega
la respuesta real, este script genera tablas con la forma y el nivel de detalle
que pide cada solicitud, calibradas con los datos reales del repositorio:

- 5.1: el total mensual de pasajeros de toda la red (datos.gob.mx) se reparte
  entre las 34 estaciones; las corridas de Teya salen de los horarios
  oficiales (9.2) y los destinos y tiempos de viaje de la guía de Teya (9.3).
- 5.2: las corridas, paradas y tarifas de la R901 salen del GTFS oficial de la
  ATY y de la página del IE-TRAM; el aforo se deriva de los pasajeros
  simulados de Teya.
- 5.3: el costo por m² se calibra con las 101 obras de banquetas del
  Ayuntamiento en el SRFT de la SHCP; las calles siguen la retícula del Centro.

Todo lo que se genera es SIMULADO y así se marca en todas partes:
carpeta datos/simulados/, prefijo SIMULADO_ en cada archivo, tablas sim_*,
columna origen_dato = "SIMULADO", id de fuente E8-05.N-SIM, capa «simulado»
en el catálogo y un LEEME_SIMULADO.md por carpeta con el método. Los
identificadores de obra empiezan con SIM- y no imitan folios oficiales.

La semilla es fija: dos corridas dan archivos idénticos. Cada tabla se
concilia contra el total real que la calibra (reportes/conciliacion.csv).

Uso: python src/simular_solicitudes.py
"""

from __future__ import annotations

import calendar
import sys
from pathlib import Path

import numpy as np
import pandas as pd

import curar

RAIZ = curar.RAIZ
ETL = RAIZ / "datos" / "para-etl"
SIM = RAIZ / "datos" / "simulados" / "05_solicitud_datos"
SEMILLA = 2026
MARCA = "SIMULADO"
RESPONSABLE = curar.tablas.RESPONSABLE
DIAS = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]

conciliacion: list[dict] = []
catalogo: list[dict] = []
diccionario: list[dict] = []
perfiles: list[pd.DataFrame] = []


# --- Utilidades --------------------------------------------------------------

def repartir(total: int, pesos, rng: np.random.Generator | None = None, ruido: float = 0.0) -> np.ndarray:
    """Reparte un total entero según pesos (resto mayor). La suma es exacta."""
    p = np.asarray(pesos, dtype=float)
    if rng is not None and ruido:
        p = p * rng.lognormal(0.0, ruido, size=len(p))
    if total <= 0 or p.sum() <= 0:
        return np.zeros(len(p), dtype=int)
    cuota = total * p / p.sum()
    base = np.floor(cuota).astype(int)
    faltan = total - base.sum()
    base[np.argsort(-(cuota - base), kind="stable")[:faltan]] += 1
    return base


def dias_del_mes(anio: int, mes: int) -> list[int]:
    """Día de la semana (0 = lunes) de cada día del mes."""
    return [calendar.weekday(anio, mes, d) for d in range(1, calendar.monthrange(anio, mes)[1] + 1)]


def control(tabla: str, ident: str, real: int, simulado: int, nota: str) -> None:
    ok = int(real) == int(simulado)
    conciliacion.append({
        "capa": "simulado", "tabla": tabla, "id_fuente": ident, "filas_original": int(real),
        "filas_para_etl": "", "filas_curado": int(simulado), "filas_rechazadas": "",
        "cuadra_original_para_etl": "", "cuadra_para_etl_curado": ok, "nota": nota,
    })
    print(f"[{'OK' if ok else 'REVISAR'}] {tabla}: {nota}")


SOLICITUDES = {
    "E8-05.1-SIM": ("5.1_tren_maya_pasajeros", "Tren Maya, S.A. de C.V.",
                    "campo/05_solicitud_datos/5.1_tren_maya_pasajeros/solicitud.md"),
    "E8-05.2-SIM": ("5.2_aty_ruta_r901", "Agencia de Transporte de Yucatán (ATY)",
                    "campo/05_solicitud_datos/5.2_aty_ruta_r901/solicitud.md"),
    "E8-05.3-SIM": ("5.3_ayuntamiento_banquetas", "Ayuntamiento de Mérida",
                    "campo/05_solicitud_datos/5.3_ayuntamiento_banquetas/solicitud.md"),
}
URL_REPO = "https://github.com/ezraidenn/del-tren-a-la-calle/blob/main/"


def guardar(df: pd.DataFrame, ident: str, tabla: str, clave: list[str], granularidad: str,
            territorio: str, cobertura, unidad: str, calibracion: str, descripciones: dict) -> None:
    """Escribe Parquet y CSV y registra la tabla en catálogo, diccionario y perfil."""
    carpeta, sujeto, solicitud = SOLICITUDES[ident]
    df = df.copy()
    df.insert(0, "origen_dato", MARCA)
    if df.duplicated(clave).any():
        raise SystemExit(f"{tabla}: la clave {clave} se repite")
    destino = SIM / carpeta
    destino.mkdir(parents=True, exist_ok=True)
    nombre = f"SIMULADO_{tabla.removeprefix('sim_')}"
    spec = {
        "tabla": tabla, "id_fuente": ident, "formato": "tabular", "clave": clave,
        "granularidad": granularidad, "territorio": territorio, "cobertura": cobertura, "unidad": unidad,
        "version_fuente": f"Simulación determinista, semilla {SEMILLA}; calibrada con {calibracion}",
        "responsable": RESPONSABLE, "_parquet": destino / f"{nombre}.parquet", "_csv": destino / f"{nombre}.csv",
    }
    df.to_parquet(spec["_parquet"], index=False)
    curar.escribir_csv(df, spec["_csv"])
    ficha = curar.ficha_catalogo(spec, df, "simulado", {})
    ficha["fuente"] = (f"SIMULADO: respuesta simulada a la solicitud de acceso a la información dirigida a "
                       f"{sujeto}; no es dato oficial")
    ficha["url_original"] = URL_REPO + solicitud
    ficha["licencia"] = "CC-BY-4.0 (datos simulados del equipo)"
    catalogo.append(ficha)
    comunes = {"origen_dato": ("Marca fija «SIMULADO»: el registro no es dato oficial", "texto")}
    for col in df.columns:
        desc, uni = {**comunes, **descripciones}[col]
        diccionario.append({
            "capa": "simulado", "tabla": tabla, "columna": col, "tipo": str(df[col].dtype),
            "es_clave": col in clave, "descripcion": desc, "unidad": uni,
            "nulos_pct": round(100 * df[col].isna().mean(), 2) if len(df) else 0,
            "origen_descripcion": "src/simular_solicitudes.py",
        })
    perfiles.append(curar.perfil_columnas(df, tabla, "simulado"))


# --- 5.1 Tren Maya -----------------------------------------------------------

# Peso relativo de cada estación en ascensos (supuesto de la simulación): las
# terminales aeroportuarias y las ciudades turísticas pesan más.
PESO_ESTACION = {
    "Cancún Aeropuerto": 14, "Mérida Teya": 12, "Playa del Carmen": 10, "Valladolid": 7, "Tulum": 6,
    "San Fco. Campeche": 6, "Chichén Itzá": 5, "Palenque": 5, "Tulum Aeropuerto": 3, "Bacalar": 3,
    "Izamal": 2.5, "Chetumal Aeropuerto": 2.5, "Escárcega": 2, "Puerto Morelos": 1.8,
    "Felipe Carrillo Puerto": 1.5, "Leona Vicario": 1.0, "Nuevo Xcán": 0.9, "Calkiní": 0.9, "Maxcanú": 0.8,
    "Umán": 0.9, "Hecelchakán": 0.7, "Tenabo": 0.6, "Tixkokob": 0.8, "Edzná": 0.6, "Xpujil": 1.0,
    "Calakmul": 0.6, "Candelaria": 0.6, "Tenosique": 0.8, "Boca del Cerro": 0.5, "Triunfo": 0.4,
    "Carrillo Puerto Camp.": 0.5, "Chacchoben": 0.5, "Kohunlich": 0.4, "Centenario": 0.4,
}
# Mes de apertura por tramo (supuesto de la simulación, por tramos del sistema).
APERTURA = {
    "2023-12": ["San Fco. Campeche", "Tenabo", "Hecelchakán", "Calkiní", "Maxcanú", "Umán", "Mérida Teya",
                "Tixkokob", "Izamal", "Chichén Itzá", "Valladolid", "Nuevo Xcán", "Leona Vicario",
                "Cancún Aeropuerto"],
    "2024-02": ["Puerto Morelos", "Playa del Carmen"],
    "2024-03": ["Palenque", "Boca del Cerro", "Tenosique", "Triunfo", "Candelaria", "Escárcega",
                "Carrillo Puerto Camp.", "Edzná", "Tulum", "Tulum Aeropuerto"],
    "2024-12": ["Felipe Carrillo Puerto", "Chacchoben", "Bacalar", "Chetumal Aeropuerto", "Kohunlich",
                "Xpujil", "Calakmul", "Centenario"],
}
TEYA = "Mérida Teya"
PESO_DIA = [0.85, 0.80, 0.85, 0.95, 1.15, 1.20, 1.15]
TARIFAS_TM = {  # tipo de tarifa: (participación base, participación en temporada alta internacional)
    "Nacional": (0.48, 0.44),
    "Internacional": (0.16, 0.24),
    "Local (residentes de la península)": (0.24, 0.20),
    "Especial (estudiantes, docentes, personas adultas mayores y con discapacidad)": (0.12, 0.12),
}


def tren_maya(rng: np.random.Generator) -> pd.DataFrame:
    ident = "E8-05.1-SIM"
    real = pd.read_csv(ETL / "05_solicitud_datos/5.1_tren_maya_pasajeros/servicio_tren_maya_mensual.csv")
    piv = real.pivot_table(index="periodo_inicio", columns="variable", values="valor", aggfunc="sum")
    piv.index = pd.to_datetime(piv.index).strftime("%Y-%m")
    pasajeros = piv["pasajeros_transportados"].dropna().astype(int)
    boletos = piv.get("boletos_vendidos", pd.Series(dtype=float)).dropna().astype(int)

    guia = pd.read_csv(ETL / "09_scraping/9.3_guia_estacion_teya/tarifas_desde_teya.csv")
    guia = guia[guia["tabla"].str.contains("Nacional") & (guia["tipo_tarifa"] == "Clase Turista")]
    minutos = dict(zip(guia["estacion_destino"], guia["duracion_min"]))
    estaciones = list(PESO_ESTACION)
    apertura = {e: m for m, lista in APERTURA.items() for e in lista}
    faltan = set(estaciones) - set(apertura) - {TEYA} | (set(minutos) - set(estaciones))
    if faltan:
        raise SystemExit(f"estaciones sin peso o apertura: {sorted(faltan)}")

    # Pasajeros por estación y mes.
    filas = []
    for mes, total in pasajeros.items():
        abiertas = [e for e in estaciones if apertura[e] <= mes]
        pesos = [PESO_ESTACION[e] for e in abiertas]
        asc = repartir(int(total), pesos, rng, 0.10)
        desc = repartir(int(total), pesos, rng, 0.10)
        filas += [{"mes": mes, "estacion": e, "ascensos": int(a), "descensos": int(d)}
                  for e, a, d in zip(abiertas, asc, desc)]
    est = pd.DataFrame(filas)
    control("sim_tm_pasajeros_estacion_mes", ident, pasajeros.sum(), est["ascensos"].sum(),
            f"ascensos de todas las estaciones = pasajeros transportados de datos.gob.mx en "
            f"{len(pasajeros)} meses ({pasajeros.sum():,})")
    guardar(est, ident, "sim_tm_pasajeros_estacion_mes", ["mes", "estacion"], "Estación y mes",
            "Red del Tren Maya (34 estaciones)", "mes", "pasajeros",
            "pasajeros transportados por mes de datos.gob.mx (E8-05.1)", {
                "mes": ("Mes de operación (AAAA-MM)", "mes"),
                "estacion": ("Estación del Tren Maya, con el nombre de la guía de la estación Teya", "texto"),
                "ascensos": ("Pasajeros que abordaron en la estación en el mes", "pasajeros"),
                "descensos": ("Pasajeros que descendieron en la estación en el mes", "pasajeros"),
            })

    # Teya por día de la semana y corrida (circulaciones que paran en Teya).
    hor = pd.read_csv(ETL / "09_scraping/9.2_tren_maya_horarios/horarios_tren_maya.csv", dtype=str)
    salen = hor[hor["estacion_origen"] == TEYA][["circulacion", "estacion_destino", "hora_salida"]]
    corridas = salen.rename(columns={"estacion_destino": "hacia", "hora_salida": "hora_salida_teya"})
    if corridas["circulacion"].duplicated().any():
        raise SystemExit("una circulación sale de Teya más de una vez en los horarios")
    corridas["hora_salida_teya"] = pd.to_datetime(corridas["hora_salida_teya"], format="%H:%M").dt.strftime("%H:%M")
    corridas = corridas.sort_values("hora_salida_teya").reset_index(drop=True)
    teya = est[est["estacion"] == TEYA].set_index("mes")
    filas = []
    for mes, fila in teya.iterrows():
        anio, m = map(int, mes.split("-"))
        dias = dias_del_mes(anio, m)
        if mes == "2023-12":  # inicio de operaciones el 16 de diciembre
            dias = dias[15:]
        peso_dia = [PESO_DIA[d] * dias.count(d) for d in range(7)]
        for col in ("ascensos", "descensos"):
            por_dia = repartir(int(fila[col]), peso_dia, rng, 0.05)
            for d, n in enumerate(por_dia):
                for c, v in zip(corridas.itertuples(), repartir(int(n), [1] * len(corridas), rng, 0.20)):
                    filas.append({"mes": mes, "dia_semana": DIAS[d], "circulacion": c.circulacion,
                                  "hacia": c.hacia, "hora_salida_teya": c.hora_salida_teya, col: int(v)})
    franja = (pd.DataFrame(filas).groupby(["mes", "dia_semana", "circulacion", "hacia", "hora_salida_teya"],
                                          sort=False, as_index=False)[["ascensos", "descensos"]].sum())
    franja[["ascensos", "descensos"]] = franja[["ascensos", "descensos"]].astype(int)
    control("sim_tm_teya_dia_corrida", ident, teya["ascensos"].sum() + teya["descensos"].sum(),
            franja["ascensos"].sum() + franja["descensos"].sum(),
            "ascensos + descensos por día y corrida = los de Teya en sim_tm_pasajeros_estacion_mes")
    guardar(franja, ident, "sim_tm_teya_dia_corrida", ["mes", "dia_semana", "circulacion"],
            "Mes, día de la semana y corrida en la estación Teya-Mérida", "Estación Teya-Mérida", "mes",
            "pasajeros", "horarios oficiales del Tren Maya (E8-09.2)", {
                "mes": ("Mes de operación (AAAA-MM)", "mes"),
                "dia_semana": ("Día de la semana (suma de todos los días de ese tipo en el mes)", "texto"),
                "circulacion": ("Número de circulación del horario oficial", "código"),
                "hacia": ("Siguiente estación terminal de la corrida al salir de Teya", "texto"),
                "hora_salida_teya": ("Hora programada de salida de Teya (hora local, HH:MM)", "hora"),
                "ascensos": ("Pasajeros que abordaron en Teya en esa corrida y día de la semana, en el mes",
                             "pasajeros"),
                "descensos": ("Pasajeros que descendieron en Teya en esa corrida y día de la semana, en el mes",
                              "pasajeros"),
            })

    # Origen-destino con Teya: gravedad con el peso del destino y su tiempo de viaje.
    filas = []
    for mes, fila in teya.iterrows():
        otras = [e for e in estaciones if e != TEYA and apertura[e] <= mes]
        # Sin tiempo publicado (tramos 6 y 7) se supone un viaje largo de 5 horas.
        pesos = [PESO_ESTACION[e] / (1 + (m / 150) ** 1.3)
                 for e, m in ((e, minutos.get(e)) for e in otras) for m in [m if pd.notna(m) else 300]]
        for sentido, total in (("sale", fila["ascensos"]), ("llega", fila["descensos"])):
            for e, n in zip(otras, repartir(int(total), pesos, rng, 0.12)):
                o, d = (TEYA, e) if sentido == "sale" else (e, TEYA)
                filas.append({"mes": mes, "estacion_origen": o, "estacion_destino": d, "boletos": int(n),
                              "tiempo_viaje_min": minutos.get(e)})
    od = pd.DataFrame(filas)
    control("sim_tm_origen_destino_teya", ident, teya["ascensos"].sum() + teya["descensos"].sum(),
            od["boletos"].sum(), "boletos con origen o destino Teya = ascensos + descensos de Teya")
    guardar(od, ident, "sim_tm_origen_destino_teya", ["mes", "estacion_origen", "estacion_destino"],
            "Mes y par origen-destino con Teya", "Red del Tren Maya, viajes desde o hacia Teya", "mes",
            "boletos", "tiempos de viaje de la guía de la estación Teya (E8-09.3)", {
                "mes": ("Mes del viaje (AAAA-MM)", "mes"),
                "estacion_origen": ("Estación donde inicia el viaje", "texto"),
                "estacion_destino": ("Estación donde termina el viaje", "texto"),
                "boletos": ("Boletos vendidos para ese par de estaciones en el mes", "boletos"),
                "tiempo_viaje_min": ("Tiempo de viaje publicado entre Teya y la otra estación; vacío si la guía "
                                     "no lo publica", "minutos"),
            })

    # Boletos por tipo de tarifa, en Teya y en el sistema.
    filas = []
    for mes in pasajeros.index:
        alta = int(mes[5:]) in (12, 1, 2, 3)
        pesos = [v[1] if alta else v[0] for v in TARIFAS_TM.values()]
        total_sis = int(boletos.get(mes, pasajeros[mes]))
        for ambito, total in (("Sistema", total_sis), (TEYA, int(teya.loc[mes, "ascensos"]))):
            for t, n in zip(TARIFAS_TM, repartir(total, pesos, rng, 0.06)):
                filas.append({"mes": mes, "ambito": ambito, "tipo_tarifa": t, "boletos": int(n),
                              "base_del_total": "boletos vendidos" if ambito == "Sistema" and mes in boletos.index
                              else "pasajeros transportados" if ambito == "Sistema" else "ascensos en Teya"})
    tar = pd.DataFrame(filas)
    esperado = sum(int(boletos.get(m, pasajeros[m])) for m in pasajeros.index) + int(teya["ascensos"].sum())
    control("sim_tm_boletos_tarifa", ident, esperado, tar["boletos"].sum(),
            "boletos del sistema = boletos vendidos reales (pasajeros donde no se publican) y de Teya = ascensos")
    guardar(tar, ident, "sim_tm_boletos_tarifa", ["mes", "ambito", "tipo_tarifa"],
            "Mes, ámbito y tipo de tarifa", "Estación Teya-Mérida y red completa", "mes", "boletos",
            "boletos vendidos por mes de datos.gob.mx (E8-05.1)", {
                "mes": ("Mes de venta (AAAA-MM)", "mes"),
                "ambito": ("«Sistema» para toda la red o el nombre de la estación", "texto"),
                "tipo_tarifa": ("Tipo de tarifa del boleto", "texto"),
                "boletos": ("Boletos vendidos en el mes", "boletos"),
                "base_del_total": ("Cifra real con la que cuadra el total del mes", "texto"),
            })
    return teya


# --- 5.2 ATY, ruta R901 ------------------------------------------------------

PARTICIPACION_R901 = 0.085   # parte de los pasajeros de Teya que usan la R901 (supuesto)
LOCALES_DIA = 38              # viajes diarios entre paradas urbanas sin pasar por el tren (supuesto)
TARIFA_R901 = {"turistas": 0.36, "general con tarjeta Va-y-Ven": 0.42,
               "estudiantes y adultos mayores": 0.17, "personas con discapacidad": 0.05}
TIPO_DIA = {"L-V": range(0, 5), "Sabado": [5], "Domingo": [6]}
# Probabilidad de bajar en cada parada intermedia de los que van a bordo.
BAJA_INTERMEDIA = {0: [0.0, 0.06, 0.05, 0.12], 1: [0.0, 0.20, 0.18, 0.25]}
SUBE = {0: [0.50, 0.14, 0.09, 0.27, 0.0], 1: [0.80, 0.08, 0.07, 0.05, 0.0]}


def r901(rng: np.random.Generator, teya: pd.DataFrame) -> None:
    ident = "E8-05.2-SIM"
    base = ETL / "05_solicitud_datos/5.2_aty_ruta_r901"
    viajes = pd.read_csv(base / "r901_viajes_gtfs.csv", dtype=str)
    paradas = pd.read_csv(base / "r901_paradas.csv", dtype={"stop_id": str})
    tarifas = pd.read_csv(base / "r901_tarifas.csv").set_index("tipo_usuario")["tarifa_mxn"]
    inicio = pd.to_datetime(viajes["vigencia_inicio"].min(), format="%Y%m%d").strftime("%Y-%m")
    meses = [m for m in teya.index if m >= inicio]

    aforo, corr, parada_f, salida_f = [], [], [], []
    for mes in meses:
        anio, m = map(int, mes.split("-"))
        dias = dias_del_mes(anio, m)
        n_tipo = {t: sum(dias.count(d) for d in ds) for t, ds in TIPO_DIA.items()}
        tren = int(round((teya.loc[mes, "ascensos"] + teya.loc[mes, "descensos"]) * PARTICIPACION_R901))
        total = tren + LOCALES_DIA * len(dias) + int(rng.integers(-150, 150))
        for t, n in zip(TARIFA_R901, repartir(total, list(TARIFA_R901.values()), rng, 0.05)):
            aforo.append({"mes": mes, "tipo_tarifa": t, "tarifa_mxn": float(tarifas[t]), "validaciones": int(n),
                          "ingreso_mxn": round(float(tarifas[t]) * int(n), 2)})
        for t, n in n_tipo.items():
            prog = int((viajes["service_id"] == t).sum()) * n
            fallas = int(rng.binomial(prog, 0.012))
            corr.append({"mes": mes, "tipo_dia": t, "dias": n, "corridas_programadas": prog,
                         "corridas_realizadas": prog - fallas, "cumplimiento_pct": round(100 * (prog - fallas) / prog, 2)})
        # A Teya va algo más gente en la mañana y de Teya en la tarde; el total por sentido cuadra con el aforo.
        por_sentido = repartir(total, [0.52, 0.48], rng, 0.03)
        for sentido, n_sentido in enumerate(por_sentido):
            ps = paradas[paradas["direction_id"] == sentido].sort_values("orden")
            sube = repartir(int(n_sentido), SUBE[sentido], rng, 0.05)
            a_bordo, bajan = 0, []
            for k in range(len(ps)):
                if k == len(ps) - 1:
                    bajan.append(a_bordo + sube[k])
                else:
                    b = int(round(a_bordo * BAJA_INTERMEDIA[sentido][k]))
                    bajan.append(b)
                    a_bordo += sube[k] - b
            for (_, p), s, b in zip(ps.iterrows(), sube, bajan):
                parada_f.append({"mes": mes, "sentido": p["sentido"], "orden": int(p["orden"]),
                                 "stop_id": p["stop_id"], "parada": p["nombre"], "ascensos": int(s),
                                 "descensos": int(b)})
            # Por corrida: el peso de cada salida sigue la llegada de trenes a Teya y las horas pico.
            vs = viajes[(viajes["direction_id"] == str(sentido)) & viajes["service_id"].isin(TIPO_DIA)]
            hora = pd.to_datetime(vs["salida"], format="%H:%M:%S").dt.hour + \
                pd.to_datetime(vs["salida"], format="%H:%M:%S").dt.minute / 60
            pico = np.exp(-((hora - (8.0 if sentido == 0 else 13.5)) / 3.0) ** 2) + 0.35
            peso = pico.to_numpy() * vs["service_id"].map(n_tipo).to_numpy() * \
                vs["service_id"].map({"L-V": 1.0, "Sabado": 1.25, "Domingo": 1.2}).to_numpy()
            for v, n in zip(vs.itertuples(), repartir(int(n_sentido), peso, rng, 0.15)):
                salida_f.append({"mes": mes, "tipo_dia": v.service_id, "sentido": v.sentido,
                                 "trip_id": v.trip_id, "salida": v.salida[:5], "validaciones": int(n)})

    aforo, corr = pd.DataFrame(aforo), pd.DataFrame(corr)
    parada_f, salida_f = pd.DataFrame(parada_f), pd.DataFrame(salida_f)
    total = int(aforo["validaciones"].sum())
    control("sim_r901_validaciones_tarifa", ident, total, parada_f["ascensos"].sum(),
            "validaciones por tarifa = ascensos por parada")
    control("sim_r901_validaciones_corrida", ident, total, salida_f["validaciones"].sum(),
            "validaciones por tarifa = validaciones por corrida")
    control("sim_r901_parada_sentido", ident, parada_f["ascensos"].sum(), parada_f["descensos"].sum(),
            "ascensos = descensos en cada sentido (nadie se queda a bordo)")
    prog = int(corr["corridas_programadas"].sum())
    esperado = sum(int((viajes["service_id"] == t).sum()) * corr.loc[corr["tipo_dia"] == t, "dias"].sum()
                   for t in TIPO_DIA)
    control("sim_r901_corridas_mes", ident, esperado, prog,
            "corridas programadas = viajes del GTFS por tipo de día × días del mes")

    meses_txt = "mes"
    guardar(aforo, ident, "sim_r901_validaciones_tarifa", ["mes", "tipo_tarifa"], "Mes y tipo de tarifa",
            "Ruta R901 IE-TRAM La Plancha – Teya", meses_txt, "validaciones",
            "tarifas del IE-TRAM y pasajeros simulados de Teya", {
                "mes": ("Mes (AAAA-MM)", "mes"),
                "tipo_tarifa": ("Tipo de usuario de la tarifa publicada por el IE-TRAM", "texto"),
                "tarifa_mxn": ("Tarifa vigente del tipo de usuario", "pesos (MXN)"),
                "validaciones": ("Validaciones de pago o de tarjeta en el mes", "validaciones"),
                "ingreso_mxn": ("Validaciones por tarifa", "pesos (MXN)"),
            })
    guardar(corr, ident, "sim_r901_corridas_mes", ["mes", "tipo_dia"], "Mes y tipo de día",
            "Ruta R901 IE-TRAM La Plancha – Teya", meses_txt, "corridas",
            "viajes programados del GTFS oficial de la ATY (E8-05.2)", {
                "mes": ("Mes (AAAA-MM)", "mes"),
                "tipo_dia": ("Tipo de día del GTFS (L-V, Sabado, Domingo)", "texto"),
                "dias": ("Días de ese tipo en el mes", "días"),
                "corridas_programadas": ("Viajes del GTFS para ese tipo de día por los días del mes", "corridas"),
                "corridas_realizadas": ("Corridas que sí salieron", "corridas"),
                "cumplimiento_pct": ("Corridas realizadas entre programadas", "porcentaje"),
            })
    guardar(parada_f, ident, "sim_r901_parada_sentido", ["mes", "sentido", "orden"], "Mes, sentido y parada",
            "Ruta R901 IE-TRAM La Plancha – Teya", meses_txt, "pasajeros",
            "paradas de la R901 en el GTFS oficial de la ATY (E8-05.2)", {
                "mes": ("Mes (AAAA-MM)", "mes"),
                "sentido": ("Sentido de la ruta según el GTFS", "texto"),
                "orden": ("Orden de la parada en el sentido", "número"),
                "stop_id": ("Identificador de la parada en el GTFS de la ATY", "código"),
                "parada": ("Nombre de la parada en el GTFS", "texto"),
                "ascensos": ("Pasajeros que suben en la parada en el mes", "pasajeros"),
                "descensos": ("Pasajeros que bajan en la parada en el mes", "pasajeros"),
            })
    guardar(salida_f, ident, "sim_r901_validaciones_corrida", ["mes", "trip_id"], "Mes y corrida del GTFS",
            "Ruta R901 IE-TRAM La Plancha – Teya", meses_txt, "validaciones",
            "horarios de la R901 en el GTFS oficial de la ATY (E8-05.2)", {
                "mes": ("Mes (AAAA-MM)", "mes"),
                "tipo_dia": ("Tipo de día del GTFS", "texto"),
                "sentido": ("Sentido de la ruta según el GTFS", "texto"),
                "trip_id": ("Identificador del viaje en el GTFS de la ATY", "código"),
                "salida": ("Hora de salida de la terminal (HH:MM)", "hora"),
                "validaciones": ("Validaciones en esa corrida, sumando todos los días del tipo en el mes",
                                 "validaciones"),
            })


# --- 5.3 Ayuntamiento, banquetas del Centro ---------------------------------

PLAZA = (20.96705, -89.62386)   # Plaza Grande, entre calles 60, 61, 62 y 63
CUADRA_LAT, CUADRA_LON = 0.00115, 0.00112
# Perímetro A aproximado: calles pares 54-68 e impares 53-73; el B lo rodea.
PARES_A, IMPARES_A = range(54, 70, 2), range(53, 75, 2)
PARES_B, IMPARES_B = range(46, 78, 2), range(45, 81, 2)
ACCIONES = {
    "Rehabilitación de banquetas y guarniciones": (0.40, 1.55),
    "Construcción de banquetas": (0.15, 1.35),
    "Ampliación de banquetas": (0.12, 1.70),
    "Construcción de rampas y cruces peatonales accesibles": (0.18, 1.90),
    "Mejoramiento de banquetas con piedra de recinto": (0.15, 2.10),
}
FINANCIAMIENTO = {"Recursos propios": 0.68, "FORTAMUN": 0.22, "Recursos estatales convenidos": 0.10}
DEPENDENCIA = {"Dirección de Obras Públicas": 0.82, "Dirección de Desarrollo Urbano": 0.18}


def lat_impar(calle: int) -> float:
    return PLAZA[0] - (calle - 62) / 2 * CUADRA_LAT


def lon_par(calle: int) -> float:
    return PLAZA[1] - (calle - 61) / 2 * CUADRA_LON


def obras_centro(rng: np.random.Generator) -> None:
    ident = "E8-05.3-SIM"
    srft = pd.read_csv(ETL / "05_solicitud_datos/5.3_ayuntamiento_banquetas/obras_banquetas_merida.csv")
    srft = srft[srft["metros_cuadrados"] > 0]
    m2_srft = srft["monto_aprobado_mxn"] / srft["metros_cuadrados"]
    mediana = float(m2_srft.median())

    obras = [{"anio": 2026, "calle": 52, "entre": (69, 71), "accion": "Rehabilitación de banquetas y guarniciones",
              "inicio": "2026-05-18", "nota": "Obra difundida por el Ayuntamiento el 29 de junio de 2026"}]
    usados = {(52, 69, 71)}
    por_anio = {2023: 7, 2024: 9, 2025: 9, 2026: 7}
    for anio, n in por_anio.items():
        while sum(o["anio"] == anio for o in obras) < n:
            if rng.random() < 0.5:
                calle = int(rng.choice(list(PARES_B)))
                i = int(rng.choice(list(IMPARES_B)[:-1]))
                entre = (i, i + 2)
            else:
                calle = int(rng.choice(list(IMPARES_B)))
                p = int(rng.choice(list(PARES_B)[:-1]))
                entre = (p, p + 2)
            if (calle, *entre) in usados:
                continue
            usados.add((calle, *entre))
            mes = int(rng.integers(1, 11 if anio == 2026 else 13))
            accion = str(rng.choice(list(ACCIONES), p=[v[0] for v in ACCIONES.values()]))
            obras.append({"anio": anio, "calle": calle, "entre": entre, "accion": accion,
                          "inicio": f"{anio}-{mes:02d}-{int(rng.integers(1, 28)):02d}", "nota": ""})

    filas = []
    consecutivo: dict[int, int] = {}
    for o in sorted(obras, key=lambda x: x["inicio"]):
        anio = o["anio"]
        consecutivo[anio] = consecutivo.get(anio, 0) + 1
        par = o["calle"] % 2 == 0
        if par:
            lat = (lat_impar(o["entre"][0]) + lat_impar(o["entre"][1])) / 2
            lon = lon_par(o["calle"])
        else:
            lat = lat_impar(o["calle"])
            lon = (lon_par(o["entre"][0]) + lon_par(o["entre"][1])) / 2
        en_a = (o["calle"] in PARES_A if par else o["calle"] in IMPARES_A) and \
            all((e in IMPARES_A) if par else (e in PARES_A) for e in o["entre"])
        lados = 2 if rng.random() < 0.55 else 1
        ml = round(float(rng.uniform(95, 125)) * lados, 2)
        ancho = float(rng.uniform(1.1, 1.8 if en_a else 2.2))
        m2 = round(ml * ancho, 2)
        accion = o["accion"]
        rampas = int(rng.integers(2, 5)) * (2 if "rampas" in accion else 1) if rng.random() < 0.8 or "rampas" in accion else 0
        cruces = int(rng.integers(1, 3)) if "cruces" in accion else int(rng.random() < 0.15)
        factor = ACCIONES[accion][1] * (1.15 if en_a else 1.0)
        contratado = round(m2 * mediana * factor * float(rng.lognormal(0, 0.08)) + rampas * 14_500 + cruces * 42_000, 2)
        inicio = pd.Timestamp(o["inicio"])
        dur = int(rng.integers(35, 120))
        fin = inicio + pd.Timedelta(days=dur)
        corte = pd.Timestamp("2026-11-20")
        terminada = fin <= corte
        ejercido = round(contratado * float(rng.uniform(0.94, 1.03)) if terminada
                         else contratado * float(rng.uniform(0.3, 0.7)), 2)
        filas.append({
            "numero_obra": f"SIM-OP-{anio}-{consecutivo[anio]:03d}",
            "descripcion": f"{accion} en calle {o['calle']} entre {o['entre'][0]} y {o['entre'][1]}, Centro Histórico",
            "tipo_accion": accion, "calle": o["calle"], "entre_calle_1": o["entre"][0],
            "entre_calle_2": o["entre"][1], "perimetro": "A" if en_a else "B",
            "lat": round(lat, 6), "lon": round(lon, 6), "metros_lineales": ml, "metros_cuadrados": m2,
            "rampas": rampas, "cruces_peatonales": cruces, "monto_contratado_mxn": contratado,
            "monto_ejercido_mxn": ejercido, "monto_por_m2_mxn": round(contratado / m2, 2),
            "fuente_financiamiento": str(rng.choice(list(FINANCIAMIENTO), p=list(FINANCIAMIENTO.values()))),
            "fecha_inicio": inicio.strftime("%Y-%m-%d"),
            "fecha_termino": fin.strftime("%Y-%m-%d") if terminada else None,
            "fecha_termino_programada": fin.strftime("%Y-%m-%d"),
            "estatus": "Terminada" if terminada else "En proceso",
            "dependencia": str(rng.choice(list(DEPENDENCIA), p=list(DEPENDENCIA.values()))),
            "nota": o["nota"] or None,
        })
    df = pd.DataFrame(filas)
    fuera = ~df["lat"].between(20.955, 20.980) | ~df["lon"].between(-89.640, -89.605)
    control("sim_obras_banquetas_centro", ident, len(df), int((~fuera).sum()),
            "todas las obras caen dentro del Centro Histórico (20.955-20.980 N, 89.605-89.640 O)")
    mediana_sim = float(df["monto_por_m2_mxn"].median())
    control("sim_obras_banquetas_centro", ident, 1, int(mediana <= mediana_sim <= 3 * mediana),
            f"costo mediano por m² simulado ({mediana_sim:,.0f}) entre 1 y 3 veces el del SRFT ({mediana:,.0f})")
    guardar(df, ident, "sim_obras_banquetas_centro", ["numero_obra"], "Obra",
            "Centro Histórico de Mérida, perímetros A y B", "fecha_inicio", "obras",
            "costo por m² de las obras de banquetas del SRFT (E8-05.3)", {
                "numero_obra": ("Identificador de la obra en la simulación (SIM-OP-año-consecutivo); no es un "
                                "número de contrato real", "código"),
                "descripcion": ("Nombre o descripción de la obra", "texto"),
                "tipo_accion": ("Tipo de acción sobre la banqueta", "texto"),
                "calle": ("Calle intervenida (nomenclatura numérica de Mérida)", "número de calle"),
                "entre_calle_1": ("Primer cruzamiento", "número de calle"),
                "entre_calle_2": ("Segundo cruzamiento", "número de calle"),
                "perimetro": ("Perímetro de la zona de monumentos (A o B), aproximado", "texto"),
                "lat": ("Latitud del punto medio del tramo, WGS84", "grados decimales (EPSG:4326)"),
                "lon": ("Longitud del punto medio del tramo, WGS84", "grados decimales (EPSG:4326)"),
                "metros_lineales": ("Metros lineales de banqueta intervenidos", "m"),
                "metros_cuadrados": ("Metros cuadrados de banqueta intervenidos", "m²"),
                "rampas": ("Rampas construidas", "rampas"),
                "cruces_peatonales": ("Cruces peatonales construidos", "cruces"),
                "monto_contratado_mxn": ("Monto contratado", "pesos (MXN)"),
                "monto_ejercido_mxn": ("Monto ejercido al corte", "pesos (MXN)"),
                "monto_por_m2_mxn": ("Monto contratado entre metros cuadrados", "pesos por m²"),
                "fuente_financiamiento": ("Origen de los recursos", "texto"),
                "fecha_inicio": ("Fecha de inicio de la obra", "fecha"),
                "fecha_termino": ("Fecha de término; vacía si sigue en proceso", "fecha"),
                "fecha_termino_programada": ("Fecha de término programada", "fecha"),
                "estatus": ("Terminada o En proceso al corte del 20 de noviembre de 2026", "texto"),
                "dependencia": ("Dependencia municipal responsable", "texto"),
                "nota": ("Observación; vacía si no hay", "texto"),
            })


# --- Documentación -----------------------------------------------------------

def main() -> int:
    rng = np.random.default_rng(SEMILLA)
    teya = tren_maya(rng)
    r901(rng, teya)
    obras_centro(rng)

    curar.actualizar(RAIZ / "catalogo_tablas.csv", pd.DataFrame(catalogo), "simulado")
    curar.actualizar(RAIZ / "diccionario_columnas.csv", pd.DataFrame(diccionario), "simulado")
    curar.actualizar(curar.REPORTES / "calidad_columnas.csv", pd.concat(perfiles, ignore_index=True), "simulado")
    curar.actualizar(curar.REPORTES / "conciliacion.csv", pd.DataFrame(conciliacion), "simulado")
    malos = [c for c in conciliacion if not c["cuadra_para_etl_curado"]]
    print(f"{len(catalogo)} tablas simuladas en datos/simulados/; {len(conciliacion)} controles, "
          f"{len(malos)} sin cuadrar")
    return 1 if malos else 0


if __name__ == "__main__":
    sys.exit(main())
