"""Genera el modelo virtual de silla de ruedas para la prueba de realidad aumentada (subtema 7).

Medidas totales: 0.70 m de ancho, 1.20 m de largo y 0.90 m de alto, las del
protocolo de campo/07_ar_entradas. El modelo es simple a propósito: lo que
importa es el volumen que ocupa al pasar por una entrada, no el detalle.

Salidas en campo/07_ar_entradas/modelo/:
- silla_ruedas.glb: glTF 2.0 binario (Android, Scene Viewer y navegadores).
- silla_ruedas.usdz: para Quick Look en iPhone y iPad. Requiere el paquete
  usd-core (pip install usd-core); si no está, solo se genera el .glb.

Ejes: x = ancho, y = alto, z = largo (hacia el frente). Unidades en metros.

Uso: python src/generar_modelo_silla.py
"""

from __future__ import annotations

import json
import struct
from pathlib import Path

import numpy as np

DESTINO = Path(__file__).resolve().parents[1] / "campo" / "07_ar_entradas" / "modelo"
COLORES = {  # nombre: RGBA lineal
    "armazon": (0.20, 0.22, 0.25, 1.0),
    "asiento": (0.05, 0.25, 0.55, 1.0),
    "llanta": (0.03, 0.03, 0.03, 1.0),
}


def caja(x0, x1, y0, y1, z0, z1):
    v = np.array([[x, y, z] for x in (x0, x1) for y in (y0, y1) for z in (z0, z1)], dtype=np.float32)
    caras = [(0, 1, 3, 2), (4, 6, 7, 5), (0, 4, 5, 1), (2, 3, 7, 6), (0, 2, 6, 4), (1, 5, 7, 3)]
    normales = [(-1, 0, 0), (1, 0, 0), (0, -1, 0), (0, 1, 0), (0, 0, -1), (0, 0, 1)]
    pos, nor, idx = [], [], []
    for cara, n in zip(caras, normales):
        base = len(pos)
        pos += [v[i] for i in cara]
        nor += [n] * 4
        idx += [base, base + 1, base + 2, base, base + 2, base + 3]
    return np.array(pos, np.float32), np.array(nor, np.float32), np.array(idx, np.uint32)


def rueda(cx, cy, cz, radio, grosor, lados=40):
    """Cilindro con eje en x."""
    ang = np.linspace(0, 2 * np.pi, lados, endpoint=False)
    y, z = np.cos(ang) * radio + cy, np.sin(ang) * radio + cz
    pos, nor, idx = [], [], []
    for sx in (-1, 1):  # tapas
        centro = len(pos)
        pos.append((cx + sx * grosor / 2, cy, cz))
        nor.append((sx, 0, 0))
        for k in range(lados):
            pos.append((cx + sx * grosor / 2, y[k], z[k]))
            nor.append((sx, 0, 0))
        for k in range(lados):
            a, b = centro + 1 + k, centro + 1 + (k + 1) % lados
            idx += [centro, a, b] if sx > 0 else [centro, b, a]
    base = len(pos)
    for k in range(lados):  # banda
        n = (0, np.cos(ang[k]), np.sin(ang[k]))
        pos += [(cx - grosor / 2, y[k], z[k]), (cx + grosor / 2, y[k], z[k])]
        nor += [n, n]
    for k in range(lados):
        a, b = base + 2 * k, base + 2 * ((k + 1) % lados)
        idx += [a, b, a + 1, a + 1, b, b + 1]
    return np.array(pos, np.float32), np.array(nor, np.float32), np.array(idx, np.uint32)


def piezas() -> dict[str, list]:
    armazon = [
        caja(-0.245, -0.225, 0.44, 0.47, -0.30, 0.45), caja(0.225, 0.245, 0.44, 0.47, -0.30, 0.45),  # largueros
        caja(-0.245, -0.225, 0.08, 0.47, 0.38, 0.42), caja(0.225, 0.245, 0.08, 0.47, 0.38, 0.42),    # patas
        caja(-0.245, -0.225, 0.47, 0.90, -0.33, -0.30), caja(0.225, 0.245, 0.47, 0.90, -0.33, -0.30),  # postes
        caja(-0.20, 0.20, 0.10, 0.13, 0.42, 0.60),                                                    # reposapiés
        caja(-0.25, -0.22, 0.60, 0.63, -0.30, 0.10), caja(0.22, 0.25, 0.60, 0.63, -0.30, 0.10),      # descansabrazos
    ]
    asiento = [caja(-0.225, 0.225, 0.47, 0.51, -0.30, 0.15), caja(-0.225, 0.225, 0.51, 0.88, -0.33, -0.31)]
    llantas = [rueda(-0.335, 0.30, -0.30, 0.30, 0.03), rueda(0.335, 0.30, -0.30, 0.30, 0.03),
               rueda(-0.235, 0.08, 0.40, 0.08, 0.03), rueda(0.235, 0.08, 0.40, 0.08, 0.03)]
    return {"armazon": armazon, "asiento": asiento, "llanta": llantas}


def unir(partes):
    pos, nor, idx, base = [], [], [], 0
    for p, n, i in partes:
        pos.append(p)
        nor.append(n)
        idx.append(i + base)
        base += len(p)
    return np.concatenate(pos), np.concatenate(nor), np.concatenate(idx).astype(np.uint32)


def escribir_glb(mallas: dict[str, tuple], ruta: Path) -> None:
    binario = bytearray()
    vistas, accesorios, primitivas, materiales = [], [], [], []

    def agregar(arr: np.ndarray, objetivo: int, tipo: str, componente: int, minmax: bool = False) -> int:
        while len(binario) % 4:
            binario.append(0)
        vistas.append({"buffer": 0, "byteOffset": len(binario), "byteLength": arr.nbytes, "target": objetivo})
        binario.extend(arr.tobytes())
        acc = {"bufferView": len(vistas) - 1, "componentType": componente, "count": len(arr), "type": tipo}
        if minmax:
            acc["min"] = arr.min(axis=0).tolist()
            acc["max"] = arr.max(axis=0).tolist()
        accesorios.append(acc)
        return len(accesorios) - 1

    for m, (nombre, (pos, nor, idx)) in enumerate(mallas.items()):
        materiales.append({"name": nombre, "pbrMetallicRoughness": {
            "baseColorFactor": list(COLORES[nombre]), "metallicFactor": 0.1 if nombre != "armazon" else 0.6,
            "roughnessFactor": 0.7}})
        primitivas.append({"attributes": {"POSITION": agregar(pos, 34962, "VEC3", 5126, True),
                                          "NORMAL": agregar(nor, 34962, "VEC3", 5126)},
                           "indices": agregar(idx, 34963, "SCALAR", 5125), "material": m})
    while len(binario) % 4:
        binario.append(0)
    gltf = {
        "asset": {"version": "2.0", "generator": "src/generar_modelo_silla.py"},
        "scene": 0, "scenes": [{"nodes": [0]}],
        "nodes": [{"mesh": 0, "name": "silla_ruedas_0.70x1.20x0.90m"}],
        "meshes": [{"name": "silla_ruedas", "primitives": primitivas}],
        "materials": materiales, "buffers": [{"byteLength": len(binario)}],
        "bufferViews": vistas, "accessors": accesorios,
    }
    js = json.dumps(gltf, separators=(",", ":")).encode()
    js += b" " * (-len(js) % 4)
    total = 12 + 8 + len(js) + 8 + len(binario)
    with open(ruta, "wb") as f:
        f.write(struct.pack("<III", 0x46546C67, 2, total))
        f.write(struct.pack("<II", len(js), 0x4E4F534A) + js)
        f.write(struct.pack("<II", len(binario), 0x004E4942) + bytes(binario))


def escribir_usdz(mallas: dict[str, tuple], ruta: Path) -> bool:
    try:
        from pxr import Gf, Sdf, Usd, UsdGeom, UsdShade, UsdUtils, Vt
    except ImportError:
        print("  usd-core no está instalado: no se genera el .usdz (pip install usd-core)")
        return False
    usdc = ruta.with_suffix(".usdc")
    etapa = Usd.Stage.CreateNew(str(usdc))
    UsdGeom.SetStageUpAxis(etapa, UsdGeom.Tokens.y)
    UsdGeom.SetStageMetersPerUnit(etapa, 1.0)
    raiz = UsdGeom.Xform.Define(etapa, "/silla_ruedas")
    etapa.SetDefaultPrim(raiz.GetPrim())
    for nombre, (pos, nor, idx) in mallas.items():
        malla = UsdGeom.Mesh.Define(etapa, f"/silla_ruedas/{nombre}")
        malla.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(pos))
        malla.CreateFaceVertexCountsAttr(Vt.IntArray([3] * (len(idx) // 3)))
        malla.CreateFaceVertexIndicesAttr(Vt.IntArray(idx.astype(int).tolist()))
        malla.CreateNormalsAttr(Vt.Vec3fArray.FromNumpy(nor))
        malla.SetNormalsInterpolation(UsdGeom.Tokens.vertex)
        malla.CreateSubdivisionSchemeAttr(UsdGeom.Tokens.none)
        malla.CreateExtentAttr(Vt.Vec3fArray([Gf.Vec3f(*pos.min(axis=0).tolist()), Gf.Vec3f(*pos.max(axis=0).tolist())]))
        material = UsdShade.Material.Define(etapa, f"/silla_ruedas/materiales/{nombre}")
        sombreador = UsdShade.Shader.Define(etapa, f"/silla_ruedas/materiales/{nombre}/pbr")
        sombreador.CreateIdAttr("UsdPreviewSurface")
        sombreador.CreateInput("diffuseColor", Sdf.ValueTypeNames.Color3f).Set(Gf.Vec3f(*COLORES[nombre][:3]))
        sombreador.CreateInput("roughness", Sdf.ValueTypeNames.Float).Set(0.7)
        sombreador.CreateInput("metallic", Sdf.ValueTypeNames.Float).Set(0.6 if nombre == "armazon" else 0.1)
        material.CreateSurfaceOutput().ConnectToSource(sombreador.ConnectableAPI(), "surface")
        UsdShade.MaterialBindingAPI.Apply(malla.GetPrim()).Bind(material)
    etapa.GetRootLayer().Save()
    del etapa
    ok = UsdUtils.CreateNewARKitUsdzPackage(Sdf.AssetPath(str(usdc)), str(ruta))
    usdc.unlink()
    return bool(ok)


def main() -> None:
    DESTINO.mkdir(parents=True, exist_ok=True)
    mallas = {nombre: unir(partes) for nombre, partes in piezas().items()}
    todo = np.concatenate([m[0] for m in mallas.values()])
    medidas = todo.max(axis=0) - todo.min(axis=0)
    esperado = np.array([0.70, 0.90, 1.20])
    if not np.allclose(medidas, esperado, atol=0.005):
        raise SystemExit(f"las medidas {medidas.round(3)} no son {esperado}")
    escribir_glb(mallas, DESTINO / "silla_ruedas.glb")
    usdz = escribir_usdz(mallas, DESTINO / "silla_ruedas.usdz")
    print(f"Modelo: {medidas[0]:.2f} m de ancho, {medidas[2]:.2f} m de largo y {medidas[1]:.2f} m de alto. "
          f"Escrito silla_ruedas.glb{' y silla_ruedas.usdz' if usdz else ''}")


if __name__ == "__main__":
    main()
