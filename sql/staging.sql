-- Esquema staging del equipo E8. Generado por src/cargar_staging.py --solo-sql.
-- Una tabla por cada renglón de catalogo_tablas.csv.

CREATE SCHEMA IF NOT EXISTS e8_staging;
CREATE TABLE IF NOT EXISTS e8_staging._cargas (
    tabla text NOT NULL,
    capa text NOT NULL,
    archivo text NOT NULL,
    sha256 char(64) NOT NULL,
    filas bigint NOT NULL,
    cargado_utc timestamptz NOT NULL,
    PRIMARY KEY (tabla, sha256)
);

-- gold: dim_ageb
CREATE TABLE IF NOT EXISTS e8_staging.dim_ageb (
    cvegeo_ageb text,
    cvegeo_mun text,
    nom_mun text,
    cve_loc text,
    nom_loc text,
    cve_ageb text,
    PRIMARY KEY (cvegeo_ageb)
);
COMMENT ON TABLE e8_staging.dim_ageb IS 'AGEB urbana; Yucatán; cobertura 2020 a 2020; fuente E8-03.3';

-- gold: dim_estacion
CREATE TABLE IF NOT EXISTS e8_staging.dim_estacion (
    station_id text,
    estacion text,
    estado text,
    municipio text,
    lat double precision,
    lon double precision,
    PRIMARY KEY (station_id)
);
COMMENT ON TABLE e8_staging.dim_estacion IS 'estación; Red del Tren Maya; cobertura 2025 a 2025; fuente E8-03.2';

-- gold: dim_municipio
CREATE TABLE IF NOT EXISTS e8_staging.dim_municipio (
    cvegeo_mun text,
    cve_ent text,
    nom_ent text,
    cve_mun text,
    nom_mun text,
    PRIMARY KEY (cvegeo_mun)
);
COMMENT ON TABLE e8_staging.dim_municipio IS 'municipio; 5 estados del Tren Maya; cobertura 2020 a 2020; fuente E8-01.1';

-- gold: dim_tiempo
CREATE TABLE IF NOT EXISTS e8_staging.dim_tiempo (
    fecha_mes date,
    anio bigint,
    mes bigint,
    trimestre bigint,
    nombre_mes text,
    PRIMARY KEY (fecha_mes)
);
COMMENT ON TABLE e8_staging.dim_tiempo IS 'mes; no aplica; cobertura 2019-01-01 a 2026-12-01; fuente no aplica';

-- gold: ind_ageb_entorno_merida
CREATE TABLE IF NOT EXISTS e8_staging.ind_ageb_entorno_merida (
    cvegeo_ageb text,
    en_censo_2020 boolean,
    pob_total bigint,
    total_viviendas_habitadas bigint,
    area_km2 double precision,
    paradas_transporte bigint,
    restaurantes_seccion_amarilla bigint,
    instalaciones_deportivas bigint,
    estacionamientos_bicicleta bigint,
    instalaciones_deportivas_publicas bigint,
    km_ciclovia double precision,
    densidad_hab_km2 double precision,
    paradas_por_km2 double precision,
    deportivas_publicas_por_10mil_hab double precision,
    km_ciclovia_por_10mil_hab double precision,
    restaurantes_por_10mil_hab double precision,
    PRIMARY KEY (cvegeo_ageb)
);
COMMENT ON TABLE e8_staging.ind_ageb_entorno_merida IS 'AGEB urbana; Municipio de Mérida; cobertura 2020 a 2026; fuente E8-03.3;E8-04.1;E8-04.2;E8-04.3;E8-09.1';

-- gold: ind_municipio_contexto
CREATE TABLE IF NOT EXISTS e8_staging.ind_municipio_contexto (
    cvegeo_mun text,
    nom_ent text,
    nom_mun text,
    poblacion_2020 bigint,
    im_2020 double precision,
    gm_2020 text,
    gacu text,
    poblacion_2025 bigint,
    establecimientos_2019 bigint,
    establecimientos_2025 bigint,
    establecimientos_por_1000_hab_2025 double precision,
    variacion_pct_2019_2025 double precision,
    PRIMARY KEY (cvegeo_mun)
);
COMMENT ON TABLE e8_staging.ind_municipio_contexto IS 'municipio; 5 estados del Tren Maya; cobertura 2019 a 2025; fuente E8-01.1;E8-01.2;E8-01.3;E8-03.1;E8-03.2';

-- gold: ind_negocios_ageb_merida
CREATE TABLE IF NOT EXISTS e8_staging.ind_negocios_ageb_merida (
    cvegeo_ageb text,
    nom_loc text,
    pobtot bigint,
    establecimientos_2019 bigint,
    establecimientos_2025 bigint,
    establecimientos_por_1000_hab_2025 double precision,
    variacion_pct_2019_2025 double precision,
    im_2020 double precision,
    gm_2020 text,
    PRIMARY KEY (cvegeo_ageb)
);
COMMENT ON TABLE e8_staging.ind_negocios_ageb_merida IS 'AGEB urbana; Municipio de Mérida; cobertura 2019 a 2025; fuente E8-03.1;E8-03.2;E8-03.3;E8-01.1';

-- gold: ind_obras_banquetas_anual
CREATE TABLE IF NOT EXISTS e8_staging.ind_obras_banquetas_anual (
    anio_inicio text,
    obras bigint,
    metros_cuadrados double precision,
    monto_aprobado_mxn double precision,
    pagado_mxn double precision,
    monto_aprobado_por_m2_mxn double precision,
    PRIMARY KEY (anio_inicio)
);
COMMENT ON TABLE e8_staging.ind_obras_banquetas_anual IS 'año de inicio de obra; Municipio de Mérida; cobertura 2022 a 2026; fuente E8-05.3';

-- gold: ind_restaurantes_transporte
CREATE TABLE IF NOT EXISTS e8_staging.ind_restaurantes_transporte (
    id_anuncio text,
    nombre text,
    categoria text,
    colonia_normalizada text,
    lat double precision,
    lon double precision,
    parada_cercana_id text,
    parada_cercana text,
    distancia_parada_m double precision,
    paradas_a_400_m bigint,
    a_400_m_de_parada boolean,
    cvegeo_ageb text,
    PRIMARY KEY (id_anuncio)
);
COMMENT ON TABLE e8_staging.ind_restaurantes_transporte IS 'restaurante; Municipio de Mérida; cobertura 2026-11-24 a 2026-11-24; fuente E8-09.1;E8-04.3';

-- gold: ind_tren_maya_mensual
CREATE TABLE IF NOT EXISTS e8_staging.ind_tren_maya_mensual (
    fecha_mes date,
    boletos_vendidos double precision,
    boletos_vendidos_estaciones double precision,
    boletos_vendidos_puntos_venta double precision,
    kilometros_recorridos double precision,
    pasajeros_transportados double precision,
    pasajeros_por_km double precision,
    pasajeros_por_boleto double precision,
    variacion_anual_pasajeros_pct double precision,
    PRIMARY KEY (fecha_mes)
);
COMMENT ON TABLE e8_staging.ind_tren_maya_mensual IS 'mes; Red completa del Tren Maya; cobertura 2025-01-01 a 2026-09-01; fuente E8-05.1';

-- silver: aty_paraderos
CREATE TABLE IF NOT EXISTS e8_staging.aty_paraderos (
    stop_id text,
    nombre text,
    lat double precision,
    lon double precision,
    accesible_silla_ruedas text,
    num_rutas bigint,
    rutas text,
    fuente text,
    version_gtfs double precision,
    PRIMARY KEY (stop_id)
);
COMMENT ON TABLE e8_staging.aty_paraderos IS 'parada; Zona metropolitana de Mérida; cobertura 2026-11-24 a 2026-11-24; fuente E8-04.3';

-- silver: aty_r901_horario_publicado
CREATE TABLE IF NOT EXISTS e8_staging.aty_r901_horario_publicado (
    sentido text,
    corrida text,
    salida text,
    llegada text,
    texto_salida text,
    texto_llegada text,
    columna_salida text,
    columna_llegada text,
    nota text,
    PRIMARY KEY (sentido, corrida)
);
COMMENT ON TABLE e8_staging.aty_r901_horario_publicado IS 'corrida por sentido; Ruta R901 La Plancha – Teya; cobertura 2026-11-24 a 2026-11-24; fuente E8-05.2';

-- silver: aty_r901_paradas
CREATE TABLE IF NOT EXISTS e8_staging.aty_r901_paradas (
    direction_id text,
    sentido text,
    orden text,
    stop_id text,
    nombre text,
    lat double precision,
    lon double precision,
    min_desde_salida bigint,
    distancia_m double precision,
    accesible_silla_ruedas text,
    PRIMARY KEY (direction_id, orden)
);
COMMENT ON TABLE e8_staging.aty_r901_paradas IS 'parada por sentido; Ruta R901 La Plancha – Teya; cobertura 2026-11-24 a 2026-11-24; fuente E8-05.2';

-- silver: aty_r901_tarifas
CREATE TABLE IF NOT EXISTS e8_staging.aty_r901_tarifas (
    tipo_usuario text,
    tarifa_mxn bigint,
    condicion text,
    fuente text,
    texto_publicado text,
    PRIMARY KEY (tipo_usuario, fuente)
);
COMMENT ON TABLE e8_staging.aty_r901_tarifas IS 'tarifa por tipo de usuario; Ruta R901; cobertura 2026-11-24 a 2026-11-24; fuente E8-05.2';

-- silver: aty_r901_viajes
CREATE TABLE IF NOT EXISTS e8_staging.aty_r901_viajes (
    trip_id text,
    service_id text,
    dias text,
    vigencia_inicio date,
    vigencia_fin date,
    direction_id bigint,
    shape_id text,
    sentido text,
    salida text,
    llegada text,
    duracion_min bigint,
    num_paradas bigint,
    PRIMARY KEY (trip_id)
);
COMMENT ON TABLE e8_staging.aty_r901_viajes IS 'viaje programado; Ruta R901 La Plancha – Teya; cobertura 2026-01-01 a 2026-11-27; fuente E8-05.2';

-- silver: conapo_accesibilidad_localidad_yucatan
CREATE TABLE IF NOT EXISTS e8_staging.conapo_accesibilidad_localidad_yucatan (
    cvegeo_loc text,
    cvegeo_mun text,
    lat double precision,
    lon double precision,
    cve_geo text,
    ent text,
    nom_ent text,
    mun text,
    nom_mun text,
    loc text,
    nom_loc text,
    longitud_texto text,
    latitud_texto text,
    altitud bigint,
    pobtot bigint,
    vivtot bigint,
    tvivhab bigint,
    tamloc bigint,
    clocori text,
    clocda bigint,
    nlocda text,
    tpvlda bigint,
    dvlda bigint,
    clocdb bigint,
    nlocdb text,
    tpvldb bigint,
    dvldb bigint,
    clocdc bigint,
    nlocdc text,
    tpvldc bigint,
    dvldc bigint,
    clocdd bigint,
    nlocdd text,
    tpvldd bigint,
    dvldd bigint,
    tcvcu bigint,
    gacu text,
    entidad text,
    longitud double precision,
    latitud double precision,
    fn_altitud bigint,
    PRIMARY KEY (cvegeo_loc)
);
COMMENT ON TABLE e8_staging.conapo_accesibilidad_localidad_yucatan IS 'localidad; Yucatán; cobertura 2020 a 2020; fuente E8-01.3';

-- silver: conapo_accesibilidad_municipal
CREATE TABLE IF NOT EXISTS e8_staging.conapo_accesibilidad_municipal (
    cvegeo_mun text,
    cve_geo text,
    ent text,
    nom_ent text,
    mun text,
    nom_mun text,
    pobtot bigint,
    vivtot bigint,
    tvivhab bigint,
    tpvlda bigint,
    tpvldb bigint,
    tpvldc bigint,
    tpvldd bigint,
    tcvcu bigint,
    gacu text,
    entidad text,
    PRIMARY KEY (cvegeo_mun)
);
COMMENT ON TABLE e8_staging.conapo_accesibilidad_municipal IS 'municipio; 5 estados del Tren Maya; cobertura 2020 a 2020; fuente E8-01.3';

-- silver: conapo_indicadores_demograficos_municipal
CREATE TABLE IF NOT EXISTS e8_staging.conapo_indicadores_demograficos_municipal (
    cvegeo_mun text,
    clave text,
    clave_ent text,
    nom_ent text,
    nom_mun text,
    ano text,
    hom_mit_ano bigint,
    muj_mit_ano bigint,
    pob_mit_mun bigint,
    muj_00_014 bigint,
    hom_00_014 bigint,
    pob_00_014 bigint,
    muj_015_64 bigint,
    hom_015_64 bigint,
    pob_015_64 bigint,
    muj_60_mas bigint,
    hom_60_mas bigint,
    pob_60_mas bigint,
    muj_65_mas bigint,
    hom_65_mas bigint,
    pob_65_mas bigint,
    pob_mit_ent bigint,
    edad_med bigint,
    por_mun double precision,
    ind_env_60 double precision,
    ind_env_65 double precision,
    rhm double precision,
    raz_dep_adu double precision,
    raz_dep_inf double precision,
    raz_dep double precision,
    fecha date,
    nom_ent_etq text,
    PRIMARY KEY (cvegeo_mun, ano)
);
COMMENT ON TABLE e8_staging.conapo_indicadores_demograficos_municipal IS 'municipio por año; 5 estados del Tren Maya; cobertura 1990 a 2040; fuente E8-01.2';

-- silver: conapo_marginacion_ageb_yucatan_2020
CREATE TABLE IF NOT EXISTS e8_staging.conapo_marginacion_ageb_yucatan_2020 (
    cvegeo_ageb text,
    cvegeo_mun text,
    cve_ageb text,
    ent text,
    nom_ent text,
    mun text,
    nom_mun text,
    loc text,
    nom_loc text,
    ageb text,
    pob_total bigint,
    p6a14nae double precision,
    sbasc double precision,
    psdss double precision,
    ovsde double precision,
    ovsee double precision,
    ovsae double precision,
    ovpt double precision,
    ovsref double precision,
    ovsint double precision,
    ovscel double precision,
    ovhac double precision,
    im_2020 double precision,
    gm_2020 text,
    imn_2020 double precision,
    fn_cve_ageb bigint,
    fn_ageb bigint,
    nom_ent_etq text,
    PRIMARY KEY (cvegeo_ageb)
);
COMMENT ON TABLE e8_staging.conapo_marginacion_ageb_yucatan_2020 IS 'AGEB urbana; Yucatán; cobertura 2020 a 2020; fuente E8-01.1';

-- silver: conapo_marginacion_municipal_2020
CREATE TABLE IF NOT EXISTS e8_staging.conapo_marginacion_municipal_2020 (
    cvegeo_mun text,
    cve_ent text,
    nom_ent text,
    cve_mun text,
    nom_mun text,
    pob_tot bigint,
    analf double precision,
    sbasc double precision,
    ovsde double precision,
    ovsee double precision,
    ovsae double precision,
    ovpt double precision,
    vhac double precision,
    pl_5000 double precision,
    po2sm double precision,
    im_2020 double precision,
    gm_2020 text,
    imn_2020 double precision,
    PRIMARY KEY (cvegeo_mun)
);
COMMENT ON TABLE e8_staging.conapo_marginacion_municipal_2020 IS 'municipio; 5 estados del Tren Maya; cobertura 2020 a 2020; fuente E8-01.1';

-- silver: conapo_poblacion_quinquenal_municipal
CREATE TABLE IF NOT EXISTS e8_staging.conapo_poblacion_quinquenal_municipal (
    cvegeo_mun text,
    clave text,
    clave_ent text,
    nom_ent text,
    nom_mun text,
    sexo text,
    ano text,
    pob_total bigint,
    pob_00_04 bigint,
    pob_05_09 bigint,
    pob_010_014 bigint,
    pob_015_019 bigint,
    pob_20_24 bigint,
    pob_25_29 bigint,
    pob_30_34 bigint,
    pob_35_39 bigint,
    pob_40_44 bigint,
    pob_45_49 bigint,
    pob_50_54 bigint,
    pob_55_59 bigint,
    pob_60_64 bigint,
    pob_65_69 bigint,
    pob_70_74 bigint,
    pob_75_79 bigint,
    pob_80_84 bigint,
    pob_85_mm bigint,
    fecha date,
    etiqueta_estado text,
    PRIMARY KEY (cvegeo_mun, sexo, ano)
);
COMMENT ON TABLE e8_staging.conapo_poblacion_quinquenal_municipal IS 'municipio por sexo y año; 5 estados del Tren Maya; cobertura 1990 a 2040; fuente E8-01.2';

-- silver: inegi_censo_2020_ageb_yucatan
CREATE TABLE IF NOT EXISTS e8_staging.inegi_censo_2020_ageb_yucatan (
    cvegeo_ageb text,
    cvegeo_mun text,
    entidad text,
    nom_ent text,
    mun text,
    nom_mun text,
    loc text,
    nom_loc text,
    ageb text,
    mza text,
    pobtot bigint,
    pobfem bigint,
    pobmas bigint,
    p_0a2 bigint,
    p_0a2_f bigint,
    p_0a2_m bigint,
    p_3ymas bigint,
    p_3ymas_f bigint,
    p_3ymas_m bigint,
    p_5ymas bigint,
    p_5ymas_f bigint,
    p_5ymas_m bigint,
    p_12ymas bigint,
    p_12ymas_f bigint,
    p_12ymas_m bigint,
    p_15ymas bigint,
    p_15ymas_f bigint,
    p_15ymas_m bigint,
    p_18ymas bigint,
    p_18ymas_f bigint,
    p_18ymas_m bigint,
    p_3a5 bigint,
    p_3a5_f bigint,
    p_3a5_m bigint,
    p_6a11 bigint,
    p_6a11_f bigint,
    p_6a11_m bigint,
    p_8a14 bigint,
    p_8a14_f bigint,
    p_8a14_m bigint,
    p_12a14 bigint,
    p_12a14_f bigint,
    p_12a14_m bigint,
    p_15a17 bigint,
    p_15a17_f bigint,
    p_15a17_m bigint,
    p_18a24 bigint,
    p_18a24_f bigint,
    p_18a24_m bigint,
    p_15a49_f bigint,
    p_60ymas bigint,
    p_60ymas_f bigint,
    p_60ymas_m bigint,
    rel_h_m double precision,
    pob0_14 bigint,
    pob15_64 bigint,
    pob65_mas bigint,
    prom_hnv double precision,
    pnacent bigint,
    pnacent_f bigint,
    pnacent_m bigint,
    pnacoe bigint,
    pnacoe_f bigint,
    pnacoe_m bigint,
    pres2015 bigint,
    pres2015_f bigint,
    pres2015_m bigint,
    presoe15 bigint,
    presoe15_f bigint,
    presoe15_m bigint,
    p3ym_hli bigint,
    p3ym_hli_f bigint,
    p3ym_hli_m bigint,
    p3hlinhe bigint,
    p3hlinhe_f bigint,
    p3hlinhe_m bigint,
    p3hli_he bigint,
    p3hli_he_f bigint,
    p3hli_he_m bigint,
    p5_hli bigint,
    p5_hli_nhe bigint,
    p5_hli_he bigint,
    phog_ind bigint,
    pob_afro bigint,
    pob_afro_f bigint,
    pob_afro_m bigint,
    pcon_disc bigint,
    pcdisc_mot bigint,
    pcdisc_vis bigint,
    pcdisc_leng bigint,
    pcdisc_aud bigint,
    pcdisc_mot2 bigint,
    pcdisc_men bigint,
    pcon_limi bigint,
    pclim_csb bigint,
    pclim_vis bigint,
    pclim_haco bigint,
    pclim_oaud bigint,
    pclim_mot2 bigint,
    pclim_re_co bigint,
    pclim_pmen bigint,
    psind_lim bigint,
    p3a5_noa bigint,
    p3a5_noa_f bigint,
    p3a5_noa_m bigint,
    p6a11_noa bigint,
    p6a11_noaf bigint,
    p6a11_noam bigint,
    p12a14noa bigint,
    p12a14noaf bigint,
    p12a14noam bigint,
    p15a17a bigint,
    p15a17a_f bigint,
    p15a17a_m bigint,
    p18a24a bigint,
    p18a24a_f bigint,
    p18a24a_m bigint,
    p8a14an bigint,
    p8a14an_f bigint,
    p8a14an_m bigint,
    p15ym_an bigint,
    p15ym_an_f bigint,
    p15ym_an_m bigint,
    p15ym_se bigint,
    p15ym_se_f bigint,
    p15ym_se_m bigint,
    p15pri_in bigint,
    p15pri_inf bigint,
    p15pri_inm bigint,
    p15pri_co bigint,
    p15pri_cof bigint,
    p15pri_com bigint,
    p15sec_in bigint,
    p15sec_inf bigint,
    p15sec_inm bigint,
    p15sec_co bigint,
    p15sec_cof bigint,
    p15sec_com bigint,
    p18ym_pb bigint,
    p18ym_pb_f bigint,
    p18ym_pb_m bigint,
    graproes double precision,
    graproes_f double precision,
    graproes_m double precision,
    pea bigint,
    pea_f bigint,
    pea_m bigint,
    pe_inac bigint,
    pe_inac_f bigint,
    pe_inac_m bigint,
    pocupada bigint,
    pocupada_f bigint,
    pocupada_m bigint,
    pdesocup bigint,
    pdesocup_f bigint,
    pdesocup_m bigint,
    psinder bigint,
    pder_ss bigint,
    pder_imss bigint,
    pder_iste bigint,
    pder_istee bigint,
    pafil_pdom bigint,
    pder_segp bigint,
    pder_imssb bigint,
    pafil_ipriv bigint,
    pafil_otrai bigint,
    p12ym_solt bigint,
    p12ym_casa bigint,
    p12ym_sepa bigint,
    pcatolica bigint,
    pro_crieva bigint,
    potras_rel bigint,
    psin_relig bigint,
    tothog bigint,
    hogjef_f bigint,
    hogjef_m bigint,
    pobhog bigint,
    phogjef_f bigint,
    phogjef_m bigint,
    vivtot bigint,
    tvivhab bigint,
    tvivpar bigint,
    vivpar_hab bigint,
    vivparh_cv bigint,
    tvivparhab bigint,
    vivpar_des bigint,
    vivpar_ut bigint,
    ocupvivpar bigint,
    prom_ocup double precision,
    pro_ocup_c double precision,
    vph_pisodt bigint,
    vph_pisoti bigint,
    vph_1dor bigint,
    vph_2ymasd bigint,
    vph_1cuart bigint,
    vph_2cuart bigint,
    vph_3ymasc bigint,
    vph_c_elec bigint,
    vph_s_elec bigint,
    vph_aguadv bigint,
    vph_aeasp bigint,
    vph_aguafv bigint,
    vph_tinaco bigint,
    vph_cister bigint,
    vph_excsa bigint,
    vph_letr bigint,
    vph_drenaj bigint,
    vph_nodren bigint,
    vph_c_serv bigint,
    vph_ndeaed bigint,
    vph_dsadma bigint,
    vph_ndacmm bigint,
    vph_snbien bigint,
    vph_refri bigint,
    vph_lavad bigint,
    vph_hmicro bigint,
    vph_autom bigint,
    vph_moto bigint,
    vph_bici bigint,
    vph_radio bigint,
    vph_tv bigint,
    vph_pc bigint,
    vph_telef bigint,
    vph_cel bigint,
    vph_inter bigint,
    vph_stvp bigint,
    vph_spmvpi bigint,
    vph_cvj bigint,
    vph_sinrtv bigint,
    vph_sinltc bigint,
    vph_sincint bigint,
    vph_sintic bigint,
    PRIMARY KEY (cvegeo_ageb)
);
COMMENT ON TABLE e8_staging.inegi_censo_2020_ageb_yucatan IS 'AGEB urbana; Yucatán; cobertura 2020 a 2020; fuente E8-03.3';

-- silver: inegi_mg_ageb_urbana_yucatan
CREATE TABLE IF NOT EXISTS e8_staging.inegi_mg_ageb_urbana_yucatan (
    cvegeo_ageb text,
    cvegeo_mun text,
    cvegeo_loc text,
    nom_mun text,
    cve_ageb text,
    en_censo_2020 boolean,
    pob_total bigint,
    total_viviendas_habitadas bigint,
    area_km2 double precision,
    lat double precision,
    lon double precision,
    PRIMARY KEY (cvegeo_ageb)
);
COMMENT ON TABLE e8_staging.inegi_mg_ageb_urbana_yucatan IS 'AGEB urbana; Yucatán; cobertura 2025-12 a 2025-12; fuente E8-03.3';

-- silver: osm_infraestructura_ciclista
CREATE TABLE IF NOT EXISTS e8_staging.osm_infraestructura_ciclista (
    osm_id text,
    categoria text,
    nombre text,
    tipo_via text,
    tipo_carril text,
    superficie text,
    segregada text,
    iluminado text,
    capacidad bigint,
    longitud_m double precision,
    lat double precision,
    lon double precision,
    fuente text,
    version_osm text,
    PRIMARY KEY (osm_id)
);
COMMENT ON TABLE e8_staging.osm_infraestructura_ciclista IS 'tramo de ciclovía o carril, o estacionamiento de bicicletas; Municipio de Mérida; cobertura 2026-11-25 a 2026-11-25; fuente E8-04.2';

-- silver: osm_unidades_deportivas
CREATE TABLE IF NOT EXISTS e8_staging.osm_unidades_deportivas (
    osm_id text,
    nombre text,
    tipo text,
    deporte text,
    acceso text,
    operador text,
    superficie text,
    iluminado text,
    acceso_publico_probable boolean,
    lat double precision,
    lon double precision,
    fuente text,
    version_osm text,
    PRIMARY KEY (osm_id)
);
COMMENT ON TABLE e8_staging.osm_unidades_deportivas IS 'instalación deportiva; Municipio de Mérida; cobertura 2026-11-25 a 2026-11-25; fuente E8-04.1';

-- silver: rutatrenmaya_conexiones_teya
CREATE TABLE IF NOT EXISTS e8_staging.rutatrenmaya_conexiones_teya (
    servicio text,
    origen text,
    destino text,
    costo_mxn bigint,
    duracion_min bigint,
    ruta text,
    fecha_consulta date,
    url text,
    PRIMARY KEY (servicio, origen, destino)
);
COMMENT ON TABLE e8_staging.rutatrenmaya_conexiones_teya IS 'conexión de transporte; Estación Teya-Mérida; cobertura 2026-11-24 a 2026-11-24; fuente E8-09.3';

-- silver: rutatrenmaya_tarifas_teya
CREATE TABLE IF NOT EXISTS e8_staging.rutatrenmaya_tarifas_teya (
    tabla text,
    estacion_origen text,
    estacion_destino text,
    tipo_tarifa text,
    precio_mxn double precision,
    disponible bigint,
    duracion_texto text,
    duracion_min bigint,
    horario text,
    fecha_consulta date,
    url text,
    PRIMARY KEY (tabla, estacion_origen, estacion_destino, tipo_tarifa)
);
COMMENT ON TABLE e8_staging.rutatrenmaya_tarifas_teya IS 'tarifa por destino y tipo; Desde la estación Teya-Mérida; cobertura 2026-11-24 a 2026-11-24; fuente E8-09.3';

-- silver: seccion_amarilla_restaurantes_merida
CREATE TABLE IF NOT EXISTS e8_staging.seccion_amarilla_restaurantes_merida (
    id_anuncio text,
    nombre text,
    nombre_omitido bigint,
    categoria text,
    direccion text,
    colonia text,
    municipio text,
    codigo_postal text,
    lat double precision,
    lon double precision,
    pagina bigint,
    url_ficha text,
    fecha_consulta date,
    coordenada_descartada boolean,
    municipio_imputado boolean,
    ubicacion_verificada boolean,
    colonia_normalizada text,
    PRIMARY KEY (id_anuncio)
);
COMMENT ON TABLE e8_staging.seccion_amarilla_restaurantes_merida IS 'anuncio de negocio; Municipio de Mérida; cobertura 2026-11-24 a 2026-11-24; fuente E8-09.1';

-- silver: siegy_aviacion_2025_12
CREATE TABLE IF NOT EXISTS e8_staging.siegy_aviacion_2025_12 (
    indicador text,
    valor double precision,
    unidad text,
    periodo text,
    territorio text,
    pagina bigint,
    fuente_archivo text,
    PRIMARY KEY (indicador, periodo, territorio)
);
COMMENT ON TABLE e8_staging.siegy_aviacion_2025_12 IS 'indicador por periodo y territorio; México, Yucatán y aeropuerto de Mérida; cobertura 2024 a 2025; fuente E8-02.1';

-- silver: siegy_resiliencia_turismo_2025_02
CREATE TABLE IF NOT EXISTS e8_staging.siegy_resiliencia_turismo_2025_02 (
    indicador text,
    valor double precision,
    unidad text,
    periodo text,
    territorio text,
    pagina bigint,
    fuente_archivo text,
    PRIMARY KEY (indicador, periodo, territorio)
);
COMMENT ON TABLE e8_staging.siegy_resiliencia_turismo_2025_02 IS 'indicador por periodo y territorio; Yucatán y zonas arqueológicas; cobertura 2019 a 2024; fuente E8-02.3';

-- silver: siegy_turismo_2025_09
CREATE TABLE IF NOT EXISTS e8_staging.siegy_turismo_2025_09 (
    indicador text,
    valor double precision,
    unidad text,
    periodo text,
    territorio text,
    pagina bigint,
    fuente_archivo text,
    PRIMARY KEY (indicador, periodo, territorio)
);
COMMENT ON TABLE e8_staging.siegy_turismo_2025_09 IS 'indicador por periodo y territorio; Yucatán; cobertura 2024 a 2025; fuente E8-02.2';

-- silver: srft_obras_banquetas_merida
CREATE TABLE IF NOT EXISTS e8_staging.srft_obras_banquetas_merida (
    folio text,
    ciclo_reporte text,
    trimestre_reporte bigint,
    nombre_obra text,
    tipo_obra text,
    colonia_o_localidad text,
    ejecutor text,
    ejecuta_ayuntamiento boolean,
    clasificacion text,
    monto_aprobado_mxn double precision,
    comprometido_mxn double precision,
    devengado_mxn double precision,
    ejercido_mxn double precision,
    pagado_mxn double precision,
    fecha_inicio date,
    fecha_estimada_termino date,
    estatus text,
    meta_unidad text,
    meta double precision,
    avance_fisico double precision,
    metros_cuadrados double precision,
    metros_lineales text,
    lat double precision,
    lon double precision,
    direccion text,
    num_puntos bigint,
    distancia_plaza_grande_km double precision,
    en_centro_historico boolean,
    fuente text,
    PRIMARY KEY (folio)
);
COMMENT ON TABLE e8_staging.srft_obras_banquetas_merida IS 'obra (proyecto SRFT); Municipio de Mérida; cobertura 2022-04-18 a 2026-09-28; fuente E8-05.3';

-- silver: tren_maya_horarios
CREATE TABLE IF NOT EXISTS e8_staging.tren_maya_horarios (
    circulacion text,
    tramo text,
    estacion_origen text,
    estacion_destino text,
    hora_salida text,
    hora_llegada text,
    tiempo_recorrido text,
    tiempo_total_circulacion text,
    tipo_servicio text,
    dias text,
    fecha_consulta date,
    url text,
    PRIMARY KEY (circulacion, tramo)
);
COMMENT ON TABLE e8_staging.tren_maya_horarios IS 'tramo de circulación; Red del Tren Maya; cobertura 2026-11-24 a 2026-11-24; fuente E8-09.2';

-- silver: tren_maya_servicio_mensual
CREATE TABLE IF NOT EXISTS e8_staging.tren_maya_servicio_mensual (
    territorio text,
    periodo_inicio date,
    periodo_fin date,
    variable text,
    valor double precision,
    archivo_origen text,
    PRIMARY KEY (variable, periodo_inicio)
);
COMMENT ON TABLE e8_staging.tren_maya_servicio_mensual IS 'variable por mes (2024: por periodo publicado); Red completa del Tren Maya; cobertura 2023-12-12 a 2026-09-01; fuente E8-05.1';

-- simulado: sim_campo_ar_entrada_1
CREATE TABLE IF NOT EXISTS e8_staging.sim_campo_ar_entrada_1 (
    origen_dato text,
    id_sesion text,
    id_tarea text,
    id_establecimiento text,
    nombre_establecimiento text,
    fecha date,
    hora text,
    lat double precision,
    lon double precision,
    cvegeo_ageb text,
    dispositivo text,
    herramienta text,
    modelo_virtual text,
    ancho_modelo_m double precision,
    largo_modelo_m double precision,
    ancho_libre_entrada_m double precision,
    altura_escalon_m double precision,
    resultado text,
    ajustes_necesarios text,
    num_intentos bigint,
    tiempo_s bigint,
    archivo_video text,
    observaciones text,
    PRIMARY KEY (id_sesion)
);
COMMENT ON TABLE e8_staging.sim_campo_ar_entrada_1 IS 'Prueba en una entrada; Centro de Mérida, recorrido de campo/RECORRIDO.md; cobertura 2026-11-24 a 2026-11-24; fuente E8-07.1';

-- simulado: sim_campo_ar_entrada_2
CREATE TABLE IF NOT EXISTS e8_staging.sim_campo_ar_entrada_2 (
    origen_dato text,
    id_sesion text,
    id_tarea text,
    id_establecimiento text,
    nombre_establecimiento text,
    fecha date,
    hora text,
    lat double precision,
    lon double precision,
    cvegeo_ageb text,
    dispositivo text,
    herramienta text,
    modelo_virtual text,
    ancho_modelo_m double precision,
    largo_modelo_m double precision,
    ancho_libre_entrada_m double precision,
    altura_escalon_m double precision,
    resultado text,
    ajustes_necesarios text,
    num_intentos bigint,
    tiempo_s bigint,
    archivo_video text,
    observaciones text,
    PRIMARY KEY (id_sesion)
);
COMMENT ON TABLE e8_staging.sim_campo_ar_entrada_2 IS 'Prueba en una entrada; Centro de Mérida, recorrido de campo/RECORRIDO.md; cobertura 2026-11-24 a 2026-11-24; fuente E8-07.2';

-- simulado: sim_campo_ar_entrada_3
CREATE TABLE IF NOT EXISTS e8_staging.sim_campo_ar_entrada_3 (
    origen_dato text,
    id_sesion text,
    id_tarea text,
    id_establecimiento text,
    nombre_establecimiento text,
    fecha date,
    hora text,
    lat double precision,
    lon double precision,
    cvegeo_ageb text,
    dispositivo text,
    herramienta text,
    modelo_virtual text,
    ancho_modelo_m double precision,
    largo_modelo_m double precision,
    ancho_libre_entrada_m double precision,
    altura_escalon_m double precision,
    resultado text,
    ajustes_necesarios text,
    num_intentos bigint,
    tiempo_s bigint,
    archivo_video text,
    observaciones text,
    PRIMARY KEY (id_sesion)
);
COMMENT ON TABLE e8_staging.sim_campo_ar_entrada_3 IS 'Prueba en una entrada; Centro de Mérida, recorrido de campo/RECORRIDO.md; cobertura 2026-11-24 a 2026-11-24; fuente E8-07.3';

-- simulado: sim_campo_entrevistas
CREATE TABLE IF NOT EXISTS e8_staging.sim_campo_entrevistas (
    origen_dato text,
    id_respuesta text,
    fecha date,
    hora text,
    lat double precision,
    lon double precision,
    cvegeo_ageb text,
    perfil text,
    rango_edad text,
    motivo_espera text,
    tiempo_espera_min bigint,
    encontro_asiento text,
    necesidad_expresada text,
    comodidad_1a5 bigint,
    comentario text,
    PRIMARY KEY (id_respuesta)
);
COMMENT ON TABLE e8_staging.sim_campo_entrevistas IS 'Persona entrevistada; Centro de Mérida, recorrido de campo/RECORRIDO.md; cobertura 2026-11-24 a 2026-11-25; fuente E8-08.3';

-- simulado: sim_campo_inventario_bancas
CREATE TABLE IF NOT EXISTS e8_staging.sim_campo_inventario_bancas (
    origen_dato text,
    id_banca text,
    fecha date,
    lat double precision,
    lon double precision,
    cvegeo_ageb text,
    tipo text,
    material text,
    largo_m double precision,
    alto_asiento_m double precision,
    profundidad_m double precision,
    respaldo text,
    descansabrazos text,
    sombra text,
    distancia_parada_m double precision,
    estado text,
    archivo_foto text,
    observaciones text,
    PRIMARY KEY (id_banca)
);
COMMENT ON TABLE e8_staging.sim_campo_inventario_bancas IS 'Banca o lugar para sentarse; Centro de Mérida, recorrido de campo/RECORRIDO.md; cobertura 2026-11-24 a 2026-11-24; fuente E8-08.1';

-- simulado: sim_campo_lidar_tramo_1
CREATE TABLE IF NOT EXISTS e8_staging.sim_campo_lidar_tramo_1 (
    origen_dato text,
    id_captura text,
    id_tramo text,
    fecha date,
    hora text,
    lat double precision,
    lon double precision,
    cvegeo_ageb text,
    dispositivo text,
    app text,
    archivo_captura text,
    largo_tramo_m double precision,
    ancho_total_m double precision,
    ancho_libre_m double precision,
    obstaculo_tipo text,
    obstaculo_largo_m text,
    obstaculo_ancho_m text,
    obstaculo_alto_m text,
    pendiente_pct double precision,
    observaciones text,
    PRIMARY KEY (id_captura)
);
COMMENT ON TABLE e8_staging.sim_campo_lidar_tramo_1 IS 'Obstáculo medido en el tramo (una fila si no hay obstáculos); Centro de Mérida, recorrido de campo/RECORRIDO.md; cobertura 2026-11-24 a 2026-11-24; fuente E8-06.1';

-- simulado: sim_campo_lidar_tramo_2
CREATE TABLE IF NOT EXISTS e8_staging.sim_campo_lidar_tramo_2 (
    origen_dato text,
    id_captura text,
    id_tramo text,
    fecha date,
    hora text,
    lat double precision,
    lon double precision,
    cvegeo_ageb text,
    dispositivo text,
    app text,
    archivo_captura text,
    largo_tramo_m double precision,
    ancho_total_m double precision,
    ancho_libre_m double precision,
    obstaculo_tipo text,
    obstaculo_largo_m double precision,
    obstaculo_ancho_m double precision,
    obstaculo_alto_m double precision,
    pendiente_pct double precision,
    observaciones text,
    PRIMARY KEY (id_captura)
);
COMMENT ON TABLE e8_staging.sim_campo_lidar_tramo_2 IS 'Obstáculo medido en el tramo (una fila si no hay obstáculos); Centro de Mérida, recorrido de campo/RECORRIDO.md; cobertura 2026-11-24 a 2026-11-24; fuente E8-06.2';

-- simulado: sim_campo_lidar_tramo_3
CREATE TABLE IF NOT EXISTS e8_staging.sim_campo_lidar_tramo_3 (
    origen_dato text,
    id_captura text,
    id_tramo text,
    fecha date,
    hora text,
    lat double precision,
    lon double precision,
    cvegeo_ageb text,
    dispositivo text,
    app text,
    archivo_captura text,
    largo_tramo_m double precision,
    ancho_total_m double precision,
    ancho_libre_m double precision,
    obstaculo_tipo text,
    obstaculo_largo_m double precision,
    obstaculo_ancho_m double precision,
    obstaculo_alto_m double precision,
    pendiente_pct double precision,
    observaciones text,
    PRIMARY KEY (id_captura)
);
COMMENT ON TABLE e8_staging.sim_campo_lidar_tramo_3 IS 'Obstáculo medido en el tramo (una fila si no hay obstáculos); Centro de Mérida, recorrido de campo/RECORRIDO.md; cobertura 2026-11-24 a 2026-11-24; fuente E8-06.3';

-- simulado: sim_campo_ocupacion_bancas
CREATE TABLE IF NOT EXISTS e8_staging.sim_campo_ocupacion_bancas (
    origen_dato text,
    id_conteo text,
    id_banca text,
    fecha date,
    franja text,
    hora_inicio text,
    hora_fin text,
    personas_sentadas bigint,
    personas_esperando_de_pie bigint,
    personas_sentadas_en_otro_lugar bigint,
    temperatura_c double precision,
    observaciones text,
    PRIMARY KEY (id_conteo)
);
COMMENT ON TABLE e8_staging.sim_campo_ocupacion_bancas IS 'Conteo de 15 minutos por banca y franja; Centro de Mérida, recorrido de campo/RECORRIDO.md; cobertura 2026-11-24 a 2026-11-24; fuente E8-08.2';

-- simulado: sim_obras_banquetas_centro
CREATE TABLE IF NOT EXISTS e8_staging.sim_obras_banquetas_centro (
    origen_dato text,
    numero_obra text,
    descripcion text,
    tipo_accion text,
    calle bigint,
    entre_calle_1 bigint,
    entre_calle_2 bigint,
    perimetro text,
    lat double precision,
    lon double precision,
    metros_lineales double precision,
    metros_cuadrados double precision,
    rampas bigint,
    cruces_peatonales bigint,
    monto_contratado_mxn double precision,
    monto_ejercido_mxn double precision,
    monto_por_m2_mxn double precision,
    fuente_financiamiento text,
    fecha_inicio date,
    fecha_termino date,
    fecha_termino_programada date,
    estatus text,
    dependencia text,
    nota text,
    PRIMARY KEY (numero_obra)
);
COMMENT ON TABLE e8_staging.sim_obras_banquetas_centro IS 'Obra; Centro Histórico de Mérida, perímetros A y B; cobertura 2023-01-10 a 2026-10-24; fuente E8-05.3-SIM';

-- simulado: sim_r901_corridas_mes
CREATE TABLE IF NOT EXISTS e8_staging.sim_r901_corridas_mes (
    origen_dato text,
    mes text,
    tipo_dia text,
    dias bigint,
    corridas_programadas bigint,
    corridas_realizadas bigint,
    cumplimiento_pct double precision,
    PRIMARY KEY (mes, tipo_dia)
);
COMMENT ON TABLE e8_staging.sim_r901_corridas_mes IS 'Mes y tipo de día; Ruta R901 IE-TRAM La Plancha – Teya; cobertura 2026-01 a 2026-09; fuente E8-05.2-SIM';

-- simulado: sim_r901_parada_sentido
CREATE TABLE IF NOT EXISTS e8_staging.sim_r901_parada_sentido (
    origen_dato text,
    mes text,
    sentido text,
    orden bigint,
    stop_id text,
    parada text,
    ascensos bigint,
    descensos bigint,
    PRIMARY KEY (mes, sentido, orden)
);
COMMENT ON TABLE e8_staging.sim_r901_parada_sentido IS 'Mes, sentido y parada; Ruta R901 IE-TRAM La Plancha – Teya; cobertura 2026-01 a 2026-09; fuente E8-05.2-SIM';

-- simulado: sim_r901_validaciones_corrida
CREATE TABLE IF NOT EXISTS e8_staging.sim_r901_validaciones_corrida (
    origen_dato text,
    mes text,
    tipo_dia text,
    sentido text,
    trip_id text,
    salida text,
    validaciones bigint,
    PRIMARY KEY (mes, trip_id)
);
COMMENT ON TABLE e8_staging.sim_r901_validaciones_corrida IS 'Mes y corrida del GTFS; Ruta R901 IE-TRAM La Plancha – Teya; cobertura 2026-01 a 2026-09; fuente E8-05.2-SIM';

-- simulado: sim_r901_validaciones_tarifa
CREATE TABLE IF NOT EXISTS e8_staging.sim_r901_validaciones_tarifa (
    origen_dato text,
    mes text,
    tipo_tarifa text,
    tarifa_mxn double precision,
    validaciones bigint,
    ingreso_mxn double precision,
    PRIMARY KEY (mes, tipo_tarifa)
);
COMMENT ON TABLE e8_staging.sim_r901_validaciones_tarifa IS 'Mes y tipo de tarifa; Ruta R901 IE-TRAM La Plancha – Teya; cobertura 2026-01 a 2026-09; fuente E8-05.2-SIM';

-- simulado: sim_tm_boletos_tarifa
CREATE TABLE IF NOT EXISTS e8_staging.sim_tm_boletos_tarifa (
    origen_dato text,
    mes text,
    ambito text,
    tipo_tarifa text,
    boletos bigint,
    base_del_total text,
    PRIMARY KEY (mes, ambito, tipo_tarifa)
);
COMMENT ON TABLE e8_staging.sim_tm_boletos_tarifa IS 'Mes, ámbito y tipo de tarifa; Estación Teya-Mérida y red completa; cobertura 2023-12 a 2026-09; fuente E8-05.1-SIM';

-- simulado: sim_tm_origen_destino_teya
CREATE TABLE IF NOT EXISTS e8_staging.sim_tm_origen_destino_teya (
    origen_dato text,
    mes text,
    estacion_origen text,
    estacion_destino text,
    boletos bigint,
    tiempo_viaje_min double precision,
    PRIMARY KEY (mes, estacion_origen, estacion_destino)
);
COMMENT ON TABLE e8_staging.sim_tm_origen_destino_teya IS 'Mes y par origen-destino con Teya; Red del Tren Maya, viajes desde o hacia Teya; cobertura 2023-12 a 2026-09; fuente E8-05.1-SIM';

-- simulado: sim_tm_pasajeros_estacion_mes
CREATE TABLE IF NOT EXISTS e8_staging.sim_tm_pasajeros_estacion_mes (
    origen_dato text,
    mes text,
    estacion text,
    ascensos bigint,
    descensos bigint,
    PRIMARY KEY (mes, estacion)
);
COMMENT ON TABLE e8_staging.sim_tm_pasajeros_estacion_mes IS 'Estación y mes; Red del Tren Maya (34 estaciones); cobertura 2023-12 a 2026-09; fuente E8-05.1-SIM';

-- simulado: sim_tm_teya_dia_corrida
CREATE TABLE IF NOT EXISTS e8_staging.sim_tm_teya_dia_corrida (
    origen_dato text,
    mes text,
    dia_semana text,
    circulacion text,
    hacia text,
    hora_salida_teya text,
    ascensos bigint,
    descensos bigint,
    PRIMARY KEY (mes, dia_semana, circulacion)
);
COMMENT ON TABLE e8_staging.sim_tm_teya_dia_corrida IS 'Mes, día de la semana y corrida en la estación Teya-Mérida; Estación Teya-Mérida; cobertura 2023-12 a 2026-09; fuente E8-05.1-SIM';

