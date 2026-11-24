# Licencias y créditos

Cada fuente conserva la licencia de quien la publica. Al usar estos datos hay que citar a la institución de origen. La licencia de cada fuente también está en `fuentes.csv` y en el `procedencia.json` de su carpeta.

| Fuentes | Quién la publica | Licencia o términos | Cómo citar |
|---|---|---|---|
| 1.1, 1.2, 1.3 | Consejo Nacional de Población (CONAPO), vía datos.gob.mx | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es) | «Fuente: CONAPO, datos.gob.mx» |
| 2.1, 2.2, 2.3 | Gobierno del Estado de Yucatán, SIEGY ([datos.yucatan.gob.mx](https://datos.yucatan.gob.mx/)) | El portal no publica licencia ni términos de uso (revisado el 2026-11-24). Son publicaciones oficiales de acceso público. Cada indicador cita su fuente primaria (SICT, ASUR, DATATUR, INAH, SEMAR) | «Fuente: SIEGY, Gobierno de Yucatán, boletín <mes año>» |
| 3.1, 3.2, 3.3 | Instituto Nacional de Estadística y Geografía (INEGI) | [Términos de libre uso de la información del INEGI](https://www.inegi.org.mx/inegi/terminos.html) | «Fuente: INEGI, DENUE <edición>» o «INEGI, Censo de Población y Vivienda 2020» |
| 4.1, 4.2 | Ayuntamiento de Mérida, Geoportal | Por confirmar al exportar cada capa | «Fuente: Geoportal del Ayuntamiento de Mérida» |
| 4.3, 5.2 | Agencia de Transporte de Yucatán (ATY): GTFS del Sistema Va y Ven y sitio [transporteyucatan.org.mx](https://transporteyucatan.org.mx/) | Sin licencia explícita. El GTFS se publica para su uso en aplicaciones de terceros. Uso académico con atribución | «Fuente: Agencia de Transporte de Yucatán, GTFS del Sistema Va y Ven» |
| 5.1 | Tren Maya, S.A. de C.V., vía datos.gob.mx | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es) | «Fuente: Tren Maya, S.A. de C.V., datos.gob.mx» |
| 5.3 | Secretaría de Hacienda y Crédito Público (SHCP), Transparencia Presupuestaria, SRFT | Datos abiertos del Gobierno de México, [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es). De la nota de prensa del Ayuntamiento solo se guardan los metadatos | «Fuente: SHCP, Transparencia Presupuestaria, SRFT» |
| 6.1 a 8.3 | Equipo «Del tren a la calle» (levantamiento propio) | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es) | «Fuente: levantamiento propio, equipo Del tren a la calle, UPY» |
| 9.1 | Sección Amarilla (listado público de negocios) | Sin licencia de datos abiertos. Su `robots.txt` permite consultar los resultados. Se publican solo datos de negocios, sin teléfonos ni nombres de personas | «Fuente: Sección Amarilla, consulta del <fecha>» |
| 9.2 | Tren Maya, S.A. de C.V. ([trenmaya.gob.mx](https://www.trenmaya.gob.mx/horarios.php)) | El sitio oficial no publica licencia ni términos de uso | «Fuente: Tren Maya, horarios oficiales, consulta del <fecha>» |
| 9.3 | rutatrenmaya.mx (sitio privado) | Todos los derechos reservados. Se publican solo las tablas de tarifas y conexiones, que son datos de hecho. La página completa no se publica | «Fuente: rutatrenmaya.mx, consulta del <fecha>» |

## Lo que no se publica en este repositorio

Hay páginas crudas de scraping que no se suben al repositorio público:

- las 20 páginas de Sección Amarilla, porque traen los teléfonos de los anunciantes y nombres de personas físicas;
- la página de rutatrenmaya.mx, porque tiene todos los derechos reservados.

Están listadas en `externos.csv` con su motivo y su SHA-256. Se entregan al servidor del proyecto por un canal privado.
