# Del tren a la calle

**¿Qué tan al alcance están las oportunidades alrededor del Tren Maya?**

Equipo: Raúl Cetina, Ricardo Horta, Damián Novelo. Grupo 9B, Ingeniería de Datos, UPY.

Este repositorio documenta las 27 fuentes del equipo: 9 subtemas, un tipo de fuente por subtema y 3 fuentes por tipo. Las fuentes externas se enlazan a su origen. Las fuentes que levanta el equipo (LiDAR, realidad aumentada y datos autoproducidos) se guardan aquí, una carpeta por fuente, con su protocolo y su plantilla de captura.

## Fuentes

| Subtema | Tipo | Fuente | Enlace |
|---|---|---|---|
| 1. El territorio antes de la conexión | Datos.gob.mx | CONAPO, Índices de marginación 2020 | https://www.datos.gob.mx/dataset/indices_marginacion |
| | | CONAPO, Proyecciones de población | https://www.datos.gob.mx/dataset/proyecciones-de-poblacion |
| | | Accesibilidad a centros urbanos | https://www.datos.gob.mx/dataset/accesibilidad_centros_urbanos |
| 2. La llegada de viajeros | SIEGY | Boletín Día de la Aviación Civil, dic 2025 | https://datos.yucatan.gob.mx/storage/boletines/archivos/2025/Boletin_2025_12.pdf |
| | | Boletín Día Mundial del Turismo, sep 2025 | https://datos.yucatan.gob.mx/storage/boletines/archivos/2025/Boletin_2025_09.pdf |
| | | Boletín Día Mundial de la Resiliencia del Turismo, feb 2025 | https://datos.yucatan.gob.mx/storage/boletines/archivos/2025/Boletin_2025_02.pdf |
| 3. Los negocios que encuentra esa demanda | INEGI | DENUE noviembre 2019 | https://www.inegi.org.mx/contenidos/masiva/denue/2019_11/denue_31_1119_csv.zip |
| | | DENUE mayo 2025 | https://www.inegi.org.mx/contenidos/masiva/denue/2025_05/denue_31_0525_csv.zip |
| | | Censo 2020, AGEB y manzana urbana | https://www.inegi.org.mx/contenidos/programas/ccpv/2020/datosabiertos/ageb_manzana/ageb_mza_urbana_31_cpv2020_csv.zip |
| 4. Una ciudad preparada para recibirlos | Geoportal de Mérida | Unidades deportivas | https://geoportal.merida.gob.mx/unidadesdeportivas |
| | | Centros de Desarrollo Integral | https://geoportal.merida.gob.mx/cdi |
| | | Paraderos y Circuito Enlace | https://geoportal.merida.gob.mx/paraderos |
| 5. Llegar del transporte al negocio | Solicitud de datos | Tren Maya: pasajeros por estación y mes | https://www.datos.gob.mx/dataset/prestacion_servicio_ferroviario_pasajeros |
| | | ATY: ruta R901 IE-TRAM La Plancha – Teya | https://transporteyucatan.org.mx/rutas/R901 |
| | | Ayuntamiento de Mérida: capas de vialidades, banquetas y paraderos | https://geoportal.merida.gob.mx/paraderos |
| 6. Los últimos metros a pie | LiDAR | Tramo de banqueta 1 | https://github.com/ezraidenn/del-tren-a-la-calle/tree/main/fuentes/06_lidar_banquetas/6.1_tramo_1 |
| | | Tramo de banqueta 2 | https://github.com/ezraidenn/del-tren-a-la-calle/tree/main/fuentes/06_lidar_banquetas/6.2_tramo_2 |
| | | Tramo de banqueta 3 | https://github.com/ezraidenn/del-tren-a-la-calle/tree/main/fuentes/06_lidar_banquetas/6.3_tramo_3 |
| 7. Encontrar un negocio no siempre significa poder entrar | Realidad aumentada | Entrada del negocio 1 | https://github.com/ezraidenn/del-tren-a-la-calle/tree/main/fuentes/07_ar_entradas/7.1_entrada_1 |
| | | Entrada del negocio 2 | https://github.com/ezraidenn/del-tren-a-la-calle/tree/main/fuentes/07_ar_entradas/7.2_entrada_2 |
| | | Entrada del negocio 3 | https://github.com/ezraidenn/del-tren-a-la-calle/tree/main/fuentes/07_ar_entradas/7.3_entrada_3 |
| 8. Permanecer también importa | Autoproducidos | Inventario de bancas y sombra | https://github.com/ezraidenn/del-tren-a-la-calle/tree/main/fuentes/08_autoproducidos_permanencia/8.1_inventario_bancas |
| | | Conteo de ocupación de bancas | https://github.com/ezraidenn/del-tren-a-la-calle/tree/main/fuentes/08_autoproducidos_permanencia/8.2_ocupacion_bancas |
| | | Entrevistas breves sobre espera y descanso | https://github.com/ezraidenn/del-tren-a-la-calle/tree/main/fuentes/08_autoproducidos_permanencia/8.3_entrevistas |
| 9. Hacer visibles las oportunidades | Scraping | Sección Amarilla, negocios de Mérida | https://www.seccionamarilla.com.mx/resultados/restaurantes/yucatan/merida/1 |
| | | Tren Maya, horarios oficiales | https://www.trenmaya.gob.mx/horarios.php |
| | | Guía de la estación Teya-Mérida | https://rutatrenmaya.mx/estacion-teya-merida-en-el-tren-maya/ |

Los enlaces del INEGI son de Yucatán (clave 31). Para Campeche, Quintana Roo, Chiapas y Tabasco se cambia 31 por 04, 23, 07 o 27.

## Claves para cruzar datos

Toda tabla levantada por el equipo lleva fecha, hora, latitud y longitud en WGS84 (EPSG:4326) y la clave de AGEB del INEGI (`cvegeo_ageb`). Así se puede cruzar con el DENUE, el Censo y las fuentes de los demás equipos.

## Estado

Las carpetas de los subtemas 6, 7 y 8 tienen protocolo y plantilla. Los datos se cargan después del levantamiento en campo.
