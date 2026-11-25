# Gráficas del equipo E8 para el dashboard-libro

`graficas_e8.csv` lista las gráficas propuestas para el capítulo del equipo. Hay una fila por gráfica, con estas columnas:

| Columna | Qué trae |
|---|---|
| `tabla_gold` | Tabla de la que salen los datos, registrada en [`catalogo_tablas.csv`](../catalogo_tablas.csv) |
| `tipo_grafica`, `x`, `y` | Tipo de gráfica y columnas de cada eje |
| `conclusion` | La lectura de la gráfica, en una frase que se puede verificar con los datos de la tabla |
| `fuente`, `url` | Nota de fuente con su enlace |
| `simulado` | «sí» si la gráfica usa datos simulados |

Reglas:
- **Datos simulados.** Una gráfica con `simulado = sí` lleva la marca SIMULADO visible en la imagen y en su conclusión. Nunca se mezcla con datos reales sin rotular.
- **Formato visual.** Paleta, tipografía, tamaño y plantilla los define la coordinación de TI cuando se elija el diseño del sitio. Este archivo solo fija qué se grafica y qué dice cada gráfica.
- **Cifras.** Si se regeneran los datos (`python src/pipeline.py`), hay que revisar que las cifras de cada conclusión sigan siendo ciertas.
