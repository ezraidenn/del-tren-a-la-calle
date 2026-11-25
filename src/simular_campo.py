"""Levantamiento de campo SIMULADO de los subtemas 6, 7 y 8.

Genera las 9 fuentes de campo con las mismas columnas de las plantillas de
campo/, sobre el recorrido de campo/RECORRIDO.md (calle 62 x 57 a calle 58 x
59, Centro de Mérida):

- 6.1 a 6.3 LiDAR: mediciones de 3 tramos de banqueta y una nube de puntos
  sintética (.ply) por tramo, construida con esas mismas medidas.
- 7.1 a 7.3 realidad aumentada: prueba de la silla de ruedas virtual en la
  entrada de 3 restaurantes de Sección Amarilla (fuente 9.1).
- 8.1 inventario de bancas, 8.2 conteo de ocupación por franja y 8.3
  entrevistas breves.

Valores de referencia:
- coordenadas de las paradas del GTFS (4.3) y de los restaurantes (9.1);
- AGEB asignada con los polígonos del Marco Geoestadístico (src/ageb.py);
- medidas típicas de las banquetas, accesos y mobiliario del Centro;
- temperatura de fines de noviembre en Mérida.

Todo es SIMULADO y así se marca:
- carpeta datos/simulados/ y prefijo SIMULADO_;
- estado «simulado» en fuentes.csv y columna origen_dato = SIMULADO;
- comentario en la cabecera de cada .ply;
- campo/LEEME_SIMULADO.md.

Las plantillas vacías de campo/ quedan para un levantamiento real.

No se corre solo: lo llama src/simular_solicitudes.py, que reúne todas las
tablas simuladas en el catálogo.
"""

from __future__ import annotations

import struct

import numpy as np
import pandas as pd

import ageb
import validar_campo

SEMILLA_CAMPO = 2027
FECHA = "2026-11-24"
URL_CAMPO = "https://github.com/ezraidenn/del-tren-a-la-calle/tree/main/campo/"
SCRIPT = "src/simular_campo.py"

PARADAS = {  # parada del GTFS de la ATY: (lat, lon)
    "950 La Chaya Maya": (20.970100, -89.624310),
    "2792 Palacio de la Música": (20.969063, -89.621562),
}

FUENTES_CAMPO = {
    "E8-06.1": ("06_lidar_banquetas/6.1_tramo_1", "LiDAR, tramo de banqueta 1"),
    "E8-06.2": ("06_lidar_banquetas/6.2_tramo_2", "LiDAR, tramo de banqueta 2"),
    "E8-06.3": ("06_lidar_banquetas/6.3_tramo_3", "LiDAR, tramo de banqueta 3"),
    "E8-07.1": ("07_ar_entradas/7.1_entrada_1", "realidad aumentada, entrada 1"),
    "E8-07.2": ("07_ar_entradas/7.2_entrada_2", "realidad aumentada, entrada 2"),
    "E8-07.3": ("07_ar_entradas/7.3_entrada_3", "realidad aumentada, entrada 3"),
    "E8-08.1": ("08_autoproducidos_permanencia/8.1_inventario_bancas", "inventario de bancas"),
    "E8-08.2": ("08_autoproducidos_permanencia/8.2_ocupacion_bancas", "conteo de ocupación de bancas"),
    "E8-08.3": ("08_autoproducidos_permanencia/8.3_entrevistas", "entrevistas breves"),
}


def distancia_m(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, (lat1, lon1, lat2, lon2))
    a = np.sin((lat2 - lat1) / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin((lon2 - lon1) / 2) ** 2
    return 6_371_008.8 * 2 * np.arcsin(np.sqrt(a))


def parada_mas_cercana(lat: float, lon: float) -> float:
    return round(min(float(distancia_m(lat, lon, p[0], p[1])) for p in PARADAS.values()), 1)


# --- 6. LiDAR ----------------------------------------------------------------

TRAMOS = {
    "T1": {"ident": "E8-06.1", "lat": 20.969060, "lon": -89.623850, "hora": "07:42",
           "largo": 2.80, "ancho": 1.42, "libre": 1.31, "pendiente": 1.2, "guarnicion": 0.18,
           "obstaculos": [],
           "obs": "Banqueta de concreto en buen estado, sin obstáculos. El ancho libre descuenta la guarnición "
                  "redondeada de 0.11 m."},
    "T2": {"ident": "E8-06.2", "lat": 20.969030, "lon": -89.622450, "hora": "07:58",
           "largo": 2.60, "ancho": 1.18, "libre": 0.71, "pendiente": 0.8, "guarnicion": 0.20,
           "obstaculos": [("poste de concreto (red eléctrica)", 0.30, 0.30, 2.50, 1.30, 0.71),
                          ("registro con tapa desnivelada", 0.60, 0.45, 0.03, 2.05, 0.20)],
           "obs": "El poste deja 0.71 m de paso entre la fachada y el poste; la tapa del registro sobresale 3 cm."},
    "T3": {"ident": "E8-06.3", "lat": 20.968930, "lon": -89.623220, "hora": "08:13",
           "largo": 2.40, "ancho": 1.35, "libre": 1.05, "pendiente": 10.8, "guarnicion": 0.13,
           "obstaculos": [("rampa de esquina", 1.20, 1.00, 0.13, 1.20, 0.35),
                          ("desnivel en la arista de la guarnición", 0.40, 0.20, 0.06, 0.60, 1.15)],
           "obs": "Rampa de esquina hacia el cruce con la calle 60; pendiente de 10.8 %, mayor que el 8 % "
                  "que suelen pedir los manuales de accesibilidad."},
}


def nube_tramo(t: dict, rng: np.random.Generator) -> tuple[np.ndarray, np.ndarray]:
    """Nube sintética: banqueta, guarnición, arroyo, fachada y obstáculos, con ruido de 3 mm."""
    L, W, g = t["largo"], t["ancho"], t["guarnicion"]
    pend = t["pendiente"] / 100 if t["ident"] != "E8-06.3" else 0.012
    pts, col = [], []

    def agregar(xyz, rgb, var=12):
        n = len(xyz)
        pts.append(xyz + rng.normal(0, 0.003, (n, 3)))
        c = np.clip(np.array(rgb) + rng.normal(0, var, (n, 3)), 0, 255)
        col.append(c.astype(np.uint8))

    n = int(L * W * 9000)
    x, y = rng.uniform(0, L, n), rng.uniform(0, W, n)
    z = x * pend
    if t["ident"] == "E8-06.3":  # la rampa baja hacia la esquina en el último 1.20 m, en el lado del arroyo
        en_rampa = (x > L - 1.20) & (y > W - 1.00)
        z = np.where(en_rampa, z - (x - (L - 1.20)) / 1.20 * g, z)
    agregar(np.c_[x, y, z], (168, 164, 156))
    n = int(L * g * 9000)
    x, zc = rng.uniform(0, L, n), rng.uniform(-g, 0, n)
    agregar(np.c_[x, np.full(n, W), zc + x * pend], (150, 146, 140))
    n = int(L * 0.9 * 6000)
    x, y = rng.uniform(0, L, n), rng.uniform(W, W + 0.9, n)
    agregar(np.c_[x, y, x * pend - g], (62, 62, 66), 8)
    n = int(L * 2.4 * 5000)
    x, zf = rng.uniform(0, L, n), rng.uniform(0, 2.4, n)
    agregar(np.c_[x, np.full(n, -0.02), zf + x * pend], (214, 176, 112), 10)  # fachada ocre
    for tipo, largo, ancho, alto, x0, y0 in t["obstaculos"]:
        if alto > 0.5:  # poste: cuatro caras
            n = 6000
            cara = rng.integers(0, 4, n)
            u, zz = rng.uniform(0, 1, n), rng.uniform(0, alto, n)
            xx = np.where(cara < 2, x0 + u * largo, x0 + (cara == 3) * largo)
            yy = np.where(cara < 2, y0 + (cara == 1) * ancho, y0 + u * ancho)
            agregar(np.c_[xx, yy, zz + x0 * pend], (138, 138, 134))
        elif tipo.startswith("registro") or tipo.startswith("desnivel"):
            n = 2500
            xx, yy = rng.uniform(x0, x0 + largo, n), rng.uniform(y0, y0 + ancho, n)
            agregar(np.c_[xx, yy, xx * pend + alto], (96, 92, 88))
    return np.vstack(pts).astype(np.float32), np.vstack(col)


def escribir_ply(ruta, xyz: np.ndarray, rgb: np.ndarray, tramo: str) -> None:
    cab = (f"ply\nformat binary_little_endian 1.0\n"
           f"comment SIMULADO: nube de puntos sintética del tramo {tramo}, generada por {SCRIPT}; "
           f"no es una captura real\ncomment unidades: metros; x a lo largo del tramo, y de la fachada "
           f"a la guarnición, z hacia arriba\nelement vertex {len(xyz)}\nproperty float x\nproperty float y\n"
           f"property float z\nproperty uchar red\nproperty uchar green\nproperty uchar blue\nend_header\n")
    registro = np.empty(len(xyz), dtype=[("x", "<f4"), ("y", "<f4"), ("z", "<f4"),
                                         ("r", "u1"), ("g", "u1"), ("b", "u1")])
    registro["x"], registro["y"], registro["z"] = xyz[:, 0], xyz[:, 1], xyz[:, 2]
    registro["r"], registro["g"], registro["b"] = rgb[:, 0], rgb[:, 1], rgb[:, 2]
    with open(ruta, "wb") as f:
        f.write(cab.encode("utf-8"))
        f.write(registro.tobytes())


def lidar(guardar, control, agebs, rng) -> None:
    for i, (tramo, t) in enumerate(TRAMOS.items(), start=1):
        clave = agebs.asignar([t["lat"]], [t["lon"]])[0]
        archivo = f"SIMULADO_captura_{tramo}.ply"
        filas = []
        obstaculos = t["obstaculos"] or [("ninguno", None, None, None, None, None)]
        for k, (tipo, largo, ancho, alto, _, _) in enumerate(obstaculos, start=1):
            filas.append({
                "id_captura": f"C-{tramo}-{k:02d}", "id_tramo": tramo, "fecha": FECHA, "hora": t["hora"],
                "lat": t["lat"], "lon": t["lon"], "cvegeo_ageb": clave, "dispositivo": "iPhone 13 Pro",
                "app": "3d Scanner App, modo LiDAR", "archivo_captura": archivo, "largo_tramo_m": t["largo"],
                "ancho_total_m": t["ancho"], "ancho_libre_m": t["libre"], "obstaculo_tipo": tipo,
                "obstaculo_largo_m": largo, "obstaculo_ancho_m": ancho, "obstaculo_alto_m": alto,
                "pendiente_pct": t["pendiente"], "observaciones": t["obs"] if k == 1 else None,
            })
        df = pd.DataFrame(filas)
        control(f"sim_campo_lidar_tramo_{i}", t["ident"], len(df), int((df["ancho_libre_m"] <= df["ancho_total_m"]).sum()),
                "el ancho libre no supera el ancho total en ninguna medición")
        carpeta = guardar_csv(guardar, df, t["ident"], f"sim_campo_lidar_tramo_{i}", ["id_captura"],
                              "Obstáculo medido en el tramo (una fila si no hay obstáculos)", "mediciones", {
                                  **DESC_COMUNES,
                                  "id_captura": ("Identificador de la medición: tramo y número de obstáculo", "clave"),
                                  "id_tramo": ("Tramo de banqueta (T1 a T3)", "clave"),
                                  "dispositivo": ("Celular o tableta con sensor LiDAR", "texto"),
                                  "app": ("Aplicación de escaneo", "texto"),
                                  "archivo_captura": ("Nube de puntos del tramo, en la misma carpeta", "archivo"),
                                  "largo_tramo_m": ("Largo del tramo escaneado", "m"),
                                  "ancho_total_m": ("Ancho de la banqueta, de la fachada a la orilla de la guarnición", "m"),
                                  "ancho_libre_m": ("Ancho mínimo de paso libre en el tramo", "m"),
                                  "obstaculo_tipo": ("Tipo de obstáculo; «ninguno» si no hay", "texto"),
                                  "obstaculo_largo_m": ("Largo del obstáculo en el sentido de la calle", "m"),
                                  "obstaculo_ancho_m": ("Ancho del obstáculo hacia el arroyo", "m"),
                                  "obstaculo_alto_m": ("Alto del obstáculo sobre la banqueta", "m"),
                                  "pendiente_pct": ("Pendiente longitudinal del tramo (en T3, la de la rampa)", "porcentaje"),
                                  "observaciones": ("Notas de quien midió", "texto"),
                              })
        xyz, rgb = nube_tramo(t, rng)
        escribir_ply(carpeta / archivo, xyz, rgb, tramo)
        medido = float(xyz[:, 1][xyz[:, 1] > 0.05].max() - 0.9)  # la banqueta llega hasta W; el arroyo sigue 0.9 m
        dentro = abs(medido - t["ancho"]) <= 0.01
        control(f"sim_campo_lidar_tramo_{i}", t["ident"], round(t["ancho"] * 100),
                round(t["ancho"] * 100) if dentro else round(medido * 100),
                f"la nube {archivo} ({len(xyz):,} puntos) reproduce el ancho medido de {t['ancho']:.2f} m (±1 cm)")


# --- 7. Realidad aumentada ---------------------------------------------------

ENTRADAS = [
    {"ident": "E8-07.1", "id": "998900181", "hora": "10:05", "ancho": 1.52, "escalon": 0.24, "intentos": 2,
     "tiempo": 118, "obs": "Portón de casona con escalón de piedra; la silla cabe de ancho pero no sube el escalón."},
    {"ident": "E8-07.2", "id": "3593856", "hora": "10:31", "ancho": 0.86, "escalon": 0.02, "intentos": 1,
     "tiempo": 64, "obs": "Puerta de una hoja al nivel de la banqueta; quedan 8 cm por lado."},
    {"ident": "E8-07.3", "id": "996034481", "hora": "10:52", "ancho": 0.78, "escalon": 0.17, "intentos": 3,
     "tiempo": 141, "obs": "Una hoja abierta y una mesa junto al acceso; la segunda hoja estaba fija."},
]


def resultado_ar(ancho: float, escalon: float) -> tuple[str, str]:
    """Regla del protocolo: 0.80 m de paso (0.70 de la silla + manos) y escalón de 2 cm como máximo."""
    if ancho < 0.80:
        ajuste = "abrir la segunda hoja o ampliar el acceso a 0.80 m"
        if escalon > 0.02:
            ajuste += f"; rampa para un escalón de {escalon:.2f} m"
        return "no cabe", ajuste
    if escalon > 0.02:
        return "cabe con ajustes", f"rampa portátil para un escalón de {escalon:.2f} m (unos {escalon / 0.08:.1f} m de largo al 8 %)"
    return "cabe", "ninguno"


def realidad_aumentada(guardar, control, agebs, restaurantes: pd.DataFrame) -> None:
    for i, e in enumerate(ENTRADAS, start=1):
        r = restaurantes.loc[restaurantes["id_anuncio"].astype(str) == e["id"]].iloc[0]
        resultado, ajustes = resultado_ar(e["ancho"], e["escalon"])
        df = pd.DataFrame([{
            "id_sesion": f"AR-{i:02d}", "id_tarea": "silla_en_entrada", "id_establecimiento": f"SA-{e['id']}",
            "nombre_establecimiento": r["nombre"], "fecha": FECHA, "hora": e["hora"],
            "lat": round(float(r["lat"]), 6), "lon": round(float(r["lon"]), 6),
            "cvegeo_ageb": agebs.asignar([r["lat"]], [r["lon"]])[0], "dispositivo": "Samsung Galaxy S23",
            "herramienta": "Scene Viewer (ARCore)", "modelo_virtual": "silla_ruedas.glb", "ancho_modelo_m": 0.70,
            "largo_modelo_m": 1.20, "ancho_libre_entrada_m": e["ancho"], "altura_escalon_m": e["escalon"],
            "resultado": resultado, "ajustes_necesarios": ajustes, "num_intentos": e["intentos"],
            "tiempo_s": e["tiempo"], "archivo_video": None,
            "observaciones": e["obs"] + " Simulación: sin video.",
        }])
        control(f"sim_campo_ar_entrada_{i}", e["ident"], 1, int(df["cvegeo_ageb"].notna().sum()),
                f"el restaurante {r['nombre']} (Sección Amarilla {e['id']}) cae en una AGEB urbana")
        guardar_csv(guardar, df, e["ident"], f"sim_campo_ar_entrada_{i}", ["id_sesion"], "Prueba en una entrada",
                    "registro", {
                        **DESC_COMUNES,
                        "id_sesion": ("Identificador de la prueba", "clave"),
                        "id_tarea": ("Tarea del protocolo", "texto"),
                        "id_establecimiento": ("Identificador del anuncio en Sección Amarilla (fuente 9.1)", "clave"),
                        "nombre_establecimiento": ("Nombre comercial del negocio", "texto"),
                        "dispositivo": ("Celular usado", "texto"), "herramienta": ("Visor de realidad aumentada", "texto"),
                        "modelo_virtual": ("Archivo del modelo, en campo/07_ar_entradas/modelo/", "archivo"),
                        "ancho_modelo_m": ("Ancho del modelo de silla de ruedas", "m"),
                        "largo_modelo_m": ("Largo del modelo de silla de ruedas", "m"),
                        "ancho_libre_entrada_m": ("Ancho libre del acceso, medido con la app Medida", "m"),
                        "altura_escalon_m": ("Altura del escalón de la entrada", "m"),
                        "resultado": ("cabe, cabe con ajustes o no cabe, según 0.80 m de paso y 2 cm de escalón", "texto"),
                        "ajustes_necesarios": ("Lo que haría falta para que la silla entre", "texto"),
                        "num_intentos": ("Veces que se colocó el modelo hasta alinearlo", "intentos"),
                        "tiempo_s": ("Duración de la prueba", "segundos"),
                        "archivo_video": ("Grabación de pantalla; vacía en la simulación", "archivo"),
                        "observaciones": ("Notas de quien hizo la prueba", "texto"),
                    })


# --- 8. Permanencia ----------------------------------------------------------

BANCAS = [  # id, lat, lon, tipo, material, largo, alto, prof, respaldo, brazos, sombra, estado, nota
    ("B01", 20.968840, -89.623480, "silla confidente", "concreto", 1.15, 0.42, 0.48, "sí", "no", "total", "bueno",
     "Bajo laurel"),
    ("B02", 20.968790, -89.623520, "silla confidente", "concreto", 1.15, 0.42, 0.48, "sí", "no", "total", "regular",
     "Pintura desgastada"),
    ("B03", 20.968720, -89.623430, "silla confidente", "concreto", 1.15, 0.42, 0.48, "sí", "no", "parcial", "bueno", None),
    ("B04", 20.968650, -89.623500, "silla confidente", "concreto", 1.15, 0.42, 0.48, "sí", "no", "parcial", "bueno", None),
    ("B05", 20.968610, -89.623400, "silla confidente", "concreto", 1.15, 0.42, 0.48, "sí", "no", "ninguna", "regular",
     "Al sol desde las 11:00"),
    ("B06", 20.968560, -89.623470, "silla confidente", "concreto", 1.15, 0.42, 0.48, "sí", "no", "ninguna", "malo",
     "Respaldo despostillado"),
    ("B07", 20.968760, -89.623610, "banca", "hierro fundido y madera", 1.80, 0.44, 0.50, "sí", "sí", "parcial",
     "bueno", None),
    ("B08", 20.968600, -89.623620, "banca", "hierro fundido y madera", 1.80, 0.44, 0.50, "sí", "sí", "total",
     "regular", "Falta un listón del asiento"),
    ("B09", 20.970060, -89.624250, "escalón de fachada (lugar informal)", "piedra", 3.40, 0.21, 0.35, "no", "no",
     "ninguna", "regular", "No hay banca en la parada; la gente se sienta en el escalón de la casa vecina"),
    ("B10", 20.970140, -89.624360, "jardinera (lugar informal)", "concreto", 1.60, 0.46, 0.25, "no", "no",
     "parcial", "regular", "Borde angosto de la jardinera junto al poste de la parada"),
    ("B11", 20.969150, -89.621760, "banca", "concreto", 2.00, 0.45, 0.45, "no", "no", "parcial", "bueno",
     "Plazoleta frente al Palacio de la Música"),
    ("B12", 20.969190, -89.621690, "banca", "concreto", 2.00, 0.45, 0.45, "no", "no", "ninguna", "bueno", None),
    ("B13", 20.969230, -89.621620, "banca", "concreto", 2.00, 0.45, 0.45, "no", "no", "parcial", "bueno", None),
    ("B14", 20.969040, -89.621510, "banca de parabús", "lámina perforada", 1.50, 0.46, 0.38, "sí", "no", "total",
     "bueno", "Bajo el techo del parabús; caben 3 personas"),
]

CONTEOS = {  # banca: [(sentadas, de pie, sentadas en otro lugar, nota) por franja mañana, mediodía, tarde]
    "B01": [(1, 0, 0, None), (2, 0, 0, None), (2, 0, 1, "Pareja comparte la confidente; una persona en el borde")],
    "B05": [(1, 0, 0, None), (0, 0, 0, "Al sol; nadie la usa"), (2, 0, 0, None)],
    "B07": [(2, 0, 0, None), (3, 0, 0, None), (3, 1, 0, None)],
    "B09": [(3, 6, 2, "Esperan el camión; dos se sientan en la banqueta"), (2, 4, 1, None),
            (4, 9, 2, "Hora pico de salida del trabajo")],
    "B12": [(0, 0, 0, None), (0, 0, 0, "Sin sombra a mediodía"), (3, 0, 0, "Grupo de turistas descansa")],
    "B14": [(3, 2, 0, None), (3, 1, 0, None), (3, 5, 0, "Banca llena; los demás esperan de pie")],
}
FRANJAS = [("mañana", "08:15", "08:30", 22.5), ("mediodía", "13:10", "13:25", 31.0), ("tarde", "18:20", "18:35", 27.5)]

ENTREVISTAS = [  # hora, punto, perfil, edad, motivo, minutos, asiento, necesidad, comodidad, comentario
    ("08:22", "B09", "trabaja aquí", "30-44", "esperar el camión", 15, "no", "asiento", 2,
     "Siempre me toca parada; el escalón es de la casa y a veces nos corren."),
    ("08:35", "B09", "vive aquí", "60 o más", "esperar el camión", 20, "sí", "sombra", 3,
     "Me siento en el escalón porque no aguanto tanto parada."),
    ("08:48", "B14", "trabaja aquí", "18-29", "esperar el camión", 10, "sí", "información", 4,
     "No hay letrero de a qué hora pasa; uno nada más espera."),
    ("09:05", "B01", "vive aquí", "60 o más", "descansar", 30, "sí", "baño", 4,
     "Vengo al parque todas las mañanas; falta un baño cerca."),
    ("09:20", "B07", "de visita", "30-44", "descansar", 15, "sí", "información", 4,
     "Turista nacional. Preguntó cómo llegar al Tren Maya; no sabía que hay un camión a Teya."),
    ("12:58", "B03", "de visita", "45-59", "descansar", 20, "sí", "sombra", 3,
     "Turista extranjera; respondió en inglés. Las banquetas son muy angostas para caminar con calma."),
    ("13:12", "B09", "trabaja aquí", "18-29", "esperar el camión", 10, "no", "sombra", 1,
     "A esta hora el sol pega directo y no hay dónde ponerse."),
    ("13:27", "B14", "vive aquí", "45-59", "esperar el camión", 15, "sí", "sombra", 3,
     "El techo del parabús ayuda, pero la lámina se calienta."),
    ("13:40", "B11", "trabaja aquí", "30-44", "comer", 25, "sí", "sombra", 3,
     "Como aquí mi lonche; si hubiera más árboles vendría más gente."),
    ("13:55", "B05", "de visita", "18-29", "esperar a alguien", 10, "no lo necesitaba", "otro", 2,
     "Turista nacional. Pidió bebederos de agua."),
    ("17:50", "B12", "de visita", "30-44", "descansar", 15, "sí", "información", 4,
     "Grupo de turistas. Les gustaría un mapa con restaurantes y paradas."),
    ("18:05", "B09", "trabaja aquí", "30-44", "esperar el camión", 25, "no", "asiento", 2,
     "En la tarde se junta mucha gente y no cabemos en la banqueta."),
    ("18:12", "B09", "vive aquí", "18-29", "esperar el camión", 20, "no", "información", 2,
     "Pasan varias rutas y no sabes cuál viene; una pantalla ayudaría."),
    ("18:24", "B14", "trabaja aquí", "45-59", "esperar el camión", 15, "no", "asiento", 2,
     "La banca es para tres y siempre está llena."),
    ("18:37", "B07", "vive aquí", "60 o más", "descansar", 40, "sí", "baño", 4,
     "El parque está bonito de noche, pero hay poca luz en las banquetas."),
    ("18:49", "B08", "de visita", "60 o más", "esperar a alguien", 20, "sí", "otro", 3,
     "Turista extranjero; respondió en inglés. Los escalones de las entradas son altos para su silla de ruedas plegable."),
    ("19:02", "B01", "trabaja aquí", "18-29", "descansar", 10, "sí", "sombra", 4, None),
    ("19:15", "B13", "de visita", "45-59", "esperar a alguien", 15, "sí", "información", 4,
     "Turista nacional. Le costó encontrar la parada del camión al aeropuerto."),
]


def permanencia(guardar, control, agebs, rng) -> None:
    filas = []
    for b in BANCAS:
        lat, lon = b[1], b[2]
        filas.append({
            "id_banca": b[0], "fecha": FECHA, "lat": lat, "lon": lon,
            "cvegeo_ageb": agebs.asignar([lat], [lon])[0], "tipo": b[3], "material": b[4], "largo_m": b[5],
            "alto_asiento_m": b[6], "profundidad_m": b[7], "respaldo": b[8], "descansabrazos": b[9],
            "sombra": b[10], "distancia_parada_m": parada_mas_cercana(lat, lon), "estado": b[11],
            "archivo_foto": None, "observaciones": b[12],
        })
    inv = pd.DataFrame(filas)
    control("sim_campo_inventario_bancas", "E8-08.1", len(inv), int(inv["cvegeo_ageb"].notna().sum()),
            "todas las bancas caen en una AGEB urbana de Mérida")
    guardar_csv(guardar, inv, "E8-08.1", "sim_campo_inventario_bancas", ["id_banca"], "Banca o lugar para sentarse",
                "inventario_bancas", {
                    **DESC_COMUNES,
                    "id_banca": ("Identificador de la banca en el recorrido", "clave"),
                    "tipo": ("Tipo de asiento; «lugar informal» si no es mobiliario urbano", "texto"),
                    "material": ("Material del asiento", "texto"), "largo_m": ("Largo del asiento", "m"),
                    "alto_asiento_m": ("Altura del asiento sobre el piso", "m"),
                    "profundidad_m": ("Profundidad del asiento", "m"),
                    "respaldo": ("Tiene respaldo (sí o no)", "texto"),
                    "descansabrazos": ("Tiene descansabrazos (sí o no)", "texto"),
                    "sombra": ("Sombra a mediodía: total, parcial o ninguna", "texto"),
                    "distancia_parada_m": ("Distancia en línea recta a la parada del recorrido más cercana", "m"),
                    "estado": ("Estado físico: bueno, regular o malo", "texto"),
                    "archivo_foto": ("Foto sin personas; vacía en la simulación", "archivo"),
                    "observaciones": ("Notas de quien levantó el inventario", "texto"),
                })

    filas, n = [], 0
    for banca, valores in CONTEOS.items():
        for (franja, ini, fin, temp), (sent, pie, otro, nota) in zip(FRANJAS, valores):
            n += 1
            filas.append({
                "id_conteo": f"O{n:02d}", "id_banca": banca, "fecha": FECHA, "franja": franja, "hora_inicio": ini,
                "hora_fin": fin, "personas_sentadas": sent, "personas_esperando_de_pie": pie,
                "personas_sentadas_en_otro_lugar": otro,
                "temperatura_c": round(temp + float(rng.normal(0, 0.4)), 1), "observaciones": nota,
            })
    ocu = pd.DataFrame(filas)
    control("sim_campo_ocupacion_bancas", "E8-08.2", len(ocu), int(ocu["id_banca"].isin(inv["id_banca"]).sum()),
            "cada conteo corresponde a una banca del inventario 8.1")
    guardar_csv(guardar, ocu, "E8-08.2", "sim_campo_ocupacion_bancas", ["id_conteo"], "Conteo de 15 minutos por banca y franja",
                "conteo_ocupacion", {
                    **DESC_COMUNES,
                    "id_conteo": ("Identificador del conteo", "clave"),
                    "id_banca": ("Banca del inventario 8.1", "clave"),
                    "franja": ("mañana, mediodía o tarde", "texto"),
                    "hora_inicio": ("Inicio del conteo (HH:MM)", "hora"), "hora_fin": ("Fin del conteo (HH:MM)", "hora"),
                    "personas_sentadas": ("Personas sentadas en la banca durante el conteo (máximo observado)", "personas"),
                    "personas_esperando_de_pie": ("Personas esperando de pie junto a la banca", "personas"),
                    "personas_sentadas_en_otro_lugar": ("Personas sentadas en escalones, jardineras o la banqueta", "personas"),
                    "temperatura_c": ("Temperatura del aire al inicio del conteo", "°C"),
                    "observaciones": ("Notas de quien contó", "texto"),
                })

    punto = {b[0]: (b[1], b[2]) for b in BANCAS}
    filas = []
    for k, (hora, b, perfil, edad, motivo, minutos, asiento, necesidad, comodidad, comentario) in enumerate(ENTREVISTAS, 1):
        lat, lon = punto[b]
        lat += float(rng.normal(0, 0.00002))
        lon += float(rng.normal(0, 0.00002))
        filas.append({
            "id_respuesta": f"E{k:02d}", "fecha": FECHA if k <= 10 else "2026-11-25", "hora": hora,
            "lat": round(lat, 6), "lon": round(lon, 6), "cvegeo_ageb": agebs.asignar([lat], [lon])[0],
            "perfil": perfil, "rango_edad": edad, "motivo_espera": motivo, "tiempo_espera_min": minutos,
            "encontro_asiento": asiento, "necesidad_expresada": necesidad, "comodidad_1a5": comodidad,
            "comentario": comentario,
        })
    ent = pd.DataFrame(filas)
    control("sim_campo_entrevistas", "E8-08.3", len(ent), int(ent["comodidad_1a5"].between(1, 5).sum()),
            "todas las respuestas usan la escala de comodidad de 1 a 5")
    guardar_csv(guardar, ent, "E8-08.3", "sim_campo_entrevistas", ["id_respuesta"], "Persona entrevistada",
                "respuestas", {
                    **DESC_COMUNES,
                    "id_respuesta": ("Identificador anónimo de la respuesta", "clave"),
                    "perfil": ("vive aquí, trabaja aquí o de visita", "texto"),
                    "rango_edad": ("Rango de edad estimado por quien entrevista, sin preguntarlo", "texto"),
                    "motivo_espera": ("Qué espera o por qué se detuvo", "texto"),
                    "tiempo_espera_min": ("Tiempo que suele esperar en ese punto", "minutos"),
                    "encontro_asiento": ("sí, no o no lo necesitaba", "texto"),
                    "necesidad_expresada": ("Lo que le haría más cómoda la espera", "texto"),
                    "comodidad_1a5": ("Qué tan cómodo es esperar ahí, de 1 a 5", "escala 1-5"),
                    "comentario": ("Comentario libre, resumido por quien entrevista; sin datos personales", "texto"),
                })


# --- Utilidades --------------------------------------------------------------

DESC_COMUNES = {
    "fecha": ("Fecha del levantamiento simulado (AAAA-MM-DD)", "fecha"),
    "hora": ("Hora local (HH:MM)", "hora"),
    "lat": ("Latitud, WGS84", "grados decimales EPSG:4326"),
    "lon": ("Longitud, WGS84", "grados decimales EPSG:4326"),
    "cvegeo_ageb": ("AGEB urbana donde cae el punto (Marco Geoestadístico 2025, src/ageb.py)", "clave"),
}


def guardar_csv(guardar, df, ident, tabla, clave, granularidad, archivo, descripciones):
    guardar(df, ident, tabla, clave, granularidad, "Centro de Mérida, recorrido de campo/RECORRIDO.md",
            ("2026-11-24", "2026-11-25") if "fecha" in df and df["fecha"].nunique() > 1 else (FECHA, FECHA),
            "según columna", "paradas del GTFS (4.3), restaurantes de Sección Amarilla (9.1) y AGEB del Marco "
            "Geoestadístico (3.3)", descripciones, archivo=archivo, script=SCRIPT)
    return validar_campo.RAIZ / "datos" / "simulados" / FUENTES_CAMPO[ident][0]


def generar(guardar, control, fuentes_sim: dict) -> None:
    for ident, (carpeta, nombre) in FUENTES_CAMPO.items():
        fuentes_sim[ident] = (carpeta, f"SIMULADO: levantamiento de campo simulado ({nombre}); no es una "
                                       "medición real", URL_CAMPO + carpeta)
    rng = np.random.default_rng(SEMILLA_CAMPO)
    agebs = ageb.Agebs()
    restaurantes = pd.read_parquet(next((validar_campo.RAIZ / "datos" / "curados").rglob(
        "seccion_amarilla_restaurantes_merida.parquet")))
    lidar(guardar, control, agebs, rng)
    realidad_aumentada(guardar, control, agebs, restaurantes)
    permanencia(guardar, control, agebs, rng)

    # Las tablas simuladas deben pasar las mismas revisiones que una captura real.
    agebs_censo = set(pd.read_csv(validar_campo.CENSO, usecols=["cvegeo_ageb"], dtype=str)["cvegeo_ageb"])
    antes = len(validar_campo.errores)
    revisadas = 0
    for carpeta, _ in FUENTES_CAMPO.values():
        for ruta in sorted((validar_campo.RAIZ / "datos" / "simulados" / carpeta).glob("SIMULADO_*.csv")):
            revisadas += validar_campo.revisar(ruta, agebs_censo)
    nuevos = validar_campo.errores[antes:]
    for e in nuevos:
        print("ERROR de campo:", e)
    control("sim_campo_entrevistas", "E8-08.3", revisadas, revisadas - len(nuevos),
            f"las {revisadas} filas simuladas de campo pasan src/validar_campo.py (fechas, coordenadas, AGEB, "
            "rangos, archivos y datos personales)")
