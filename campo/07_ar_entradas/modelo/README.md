# Modelo virtual de silla de ruedas

Silla de ruedas manual a tamaño real: **0.70 m de ancho, 1.20 m de largo y 0.90 m de alto**. Es la medida que usa el protocolo de la prueba de realidad aumentada. El modelo es simple a propósito: lo que importa es el volumen que ocupa al pasar por una entrada.

| Archivo | Para |
|---|---|
| `silla_ruedas.glb` | Android (Scene Viewer) y navegadores |
| `silla_ruedas.usdz` | iPhone y iPad (Quick Look) |

Se genera con `python src/generar_modelo_silla.py`. El `.usdz` requiere `pip install usd-core`. El script comprueba las medidas antes de escribir los archivos.

## Cómo abrirlo en el celular

**Android:** abre este enlace en Chrome. `resizable=false` impide cambiarle el tamaño, así que siempre sale a escala real.

```
https://arvr.google.com/scene-viewer/1.0?file=https://raw.githubusercontent.com/ezraidenn/del-tren-a-la-calle/main/campo/07_ar_entradas/modelo/silla_ruedas.glb&mode=ar_only&resizable=false
```

**iPhone o iPad:**
1. Descarga `silla_ruedas.usdz` desde GitHub. En la página del archivo, toca **Download** o **View raw**.
2. Ábrelo desde la app Archivos y toca **AR**.
3. **No hagas zoom con dos dedos.** Si lo haces, Quick Look muestra el porcentaje; tiene que quedar en **100 %**.

## Comprobar la escala antes de cada sesión

1. Coloca el modelo junto a algo de medida conocida, como una puerta o una mesa.
2. Mide con la app Medida que el ancho de las llantas traseras sea de 0.70 m.

Si no coincide, mueve el celular para que vuelva a detectar el piso y coloca el modelo otra vez.
