--creating normal table--
CREATE TABLE table_normal (

    entry_id SERIAL PRIMARY KEY,

    aber_ckgl FLOAT,
    aber_ckp FLOAT,

    estado_dhsv FLOAT,
    estado_m1 FLOAT,
    estado_m2 FLOAT,
    estado_pxo FLOAT,
    estado_sdv_gl FLOAT,
    estado_sdv_p FLOAT ,
    estado_w1 FLOAT,
    estado_w2 FLOAT,
    estado_xo FLOAT ,

    p_anular FLOAT,
    p_jus_bs FLOAT,
    p_jus_ckgl FLOAT,
    p_jus_ckp FLOAT,

    p_mon_ckgl FLOAT,
    p_mon_ckp FLOAT,
    p_mon_sdv_p FLOAT,

    p_pdg FLOAT,
    pt_p FLOAT,
    p_tpt FLOAT,

    qbs FLOAT,
    qgl FLOAT,

    t_jus_ckp FLOAT,
    t_mon_ckp FLOAT,
    t_pdg FLOAT,
    t_tpt FLOAT,

    class FLOAT,
    state VARCHAR(100),
    well_id VARCHAR(100)
);

--creating slugging table--
CREATE TABLE table_slugging (

    entry_id SERIAL PRIMARY KEY,

    aber_ckgl FLOAT,
    aber_ckp FLOAT,

    estado_dhsv FLOAT,
    estado_m1 FLOAT,
    estado_m2 FLOAT,
    estado_pxo FLOAT,
    estado_sdv_gl FLOAT,
    estado_sdv_p FLOAT ,
    estado_w1 FLOAT,
    estado_w2 FLOAT,
    estado_xo FLOAT ,


    p_anular FLOAT,
    p_jus_bs FLOAT,
    p_jus_ckgl FLOAT,
    p_jus_ckp FLOAT,

    p_mon_ckgl FLOAT,
    p_mon_ckp FLOAT,
    p_mon_sdv_p FLOAT,

    p_pdg FLOAT,
    pt_p FLOAT,
    p_tpt FLOAT,

    qbs FLOAT,
    qgl FLOAT,

    t_jus_ckp FLOAT,
    t_mon_ckp FLOAT,
    t_pdg FLOAT,
    t_tpt FLOAT,

    class FLOAT,
    state FLOAT,

    asset_type VARCHAR(50),
    well_id VARCHAR(100)

);

--creating table_hydrates--
CREATE TABLE table_hydrates (

    entry_id SERIAL PRIMARY KEY,

    aber_ckgl FLOAT,
    aber_ckp FLOAT,

    estado_dhsv FLOAT,
    estado_m1 FLOAT,
    estado_m2 FLOAT,
    estado_pxo FLOAT,
    estado_sdv_gl FLOAT,
    estado_sdv_p FLOAT ,
    estado_w1 FLOAT,
    estado_w2 FLOAT,
    estado_xo FLOAT ,


    p_anular FLOAT,
    p_jus_bs FLOAT,
    p_jus_ckgl FLOAT,
    p_jus_ckp FLOAT,

    p_mon_ckgl FLOAT,
    p_mon_ckp FLOAT,
    p_mon_sdv_p FLOAT,

    p_pdg FLOAT,
    pt_p FLOAT,
    p_tpt FLOAT,

    qbs FLOAT,
    qgl FLOAT,

    t_jus_ckp FLOAT,
    t_mon_ckp FLOAT,
    t_pdg FLOAT,
    t_tpt FLOAT,

    class FLOAT,
    state FLOAT,

    asset_type VARCHAR(50),
    well_id VARCHAR(100)

);

--Steady state baseline for healthy table--
SELECT
    AVG(pt_p) AS avg_pressure,
    MIN(pt_p) AS min_pressure,
    MAX(pt_p) AS max_pressure,
    STDDEV(pt_p) AS std_pressure,

    AVG(t_tpt) AS avg_temperature,
    MIN(t_tpt)AS min_temperature,
    MAX(t_tpt)  AS max_temperature,
    STDDEV(t_tpt) AS std_temperature
FROM table_normal;

--Slugging oscillation Analysis--
SELECT
    entry_id,
    pt_p,
    STDDEV(pt_p) OVER (
        ORDER BY entry_id
        ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
    ) AS rolling_std_pressure
FROM table_slugging;

--Hydrate thermodynamics divergence--
SELECT
    entry_id,
    p_mon_ckp,
    t_tpt,

    p_mon_ckp - LAG(p_mon_ckp, 60)
        OVER (ORDER BY entry_id) AS pressure_gradient,

    t_tpt - LAG(t_tpt, 60)
        OVER (ORDER BY entry_id) AS temperature_gradient

FROM table_hydrates;

--  CROSS-CONDITION ASSET PRESSURE AUDIT --

SELECT 
    healthy.well_id AS nominal_well_id,
    slugging.well_id AS slugging_well_id,
    ROUND(healthy.avg_healthy_pressure::numeric, 2) AS nominal_baseline_pressure_pa,
    ROUND(slugging.max_slugging_pressure::numeric, 2) AS peak_slugging_wave_pressure_pa,
    
    
    ROUND((slugging.max_slugging_pressure - healthy.avg_healthy_pressure)::numeric, 2) AS absolute_pressure_surge_pa,
    
    
    ROUND(((slugging.max_slugging_pressure - healthy.avg_healthy_pressure) / healthy.avg_healthy_pressure * 100)::numeric, 2) AS surge_percentage_increase

FROM 
    
    (SELECT 
         well_id, 
         AVG(p_tpt) AS avg_healthy_pressure
     FROM table_normal
     GROUP BY well_id) AS healthy

INNER JOIN 
    
    (SELECT 
         well_id, 
         MAX(p_tpt) AS max_slugging_pressure
     FROM table_slugging
     WHERE class = 3
     GROUP BY well_id) AS slugging

ON SUBSTRING(healthy.well_id FROM 1 FOR 10) = SUBSTRING(slugging.well_id FROM 1 FOR 10)

ORDER BY surge_percentage_increase DESC;

-- SIMULATION VS REAL-WORLD VULNERABILITY INDEX--

SELECT 
    COALESCE(slugging.standardized_asset_type, hydrates.standardized_asset_type) AS asset_classification,
    COALESCE(slugging.total_slugging_seconds, 0) AS total_slugging_seconds,
    COALESCE(hydrates.total_hydrates_seconds, 0) AS total_hydrates_seconds

FROM 
    (SELECT 
         CASE 
             WHEN asset_type ILIKE '%simulated%' THEN 'Simulated' 
             WHEN asset_type ILIKE '%real%' THEN 'Real Well'
             ELSE asset_type 
         END AS standardized_asset_type,
         COUNT(*) AS total_slugging_seconds
     FROM table_slugging
     WHERE class = 3 
     GROUP BY 
         CASE 
             WHEN asset_type ILIKE '%simulated%' THEN 'Simulated'
             WHEN asset_type ILIKE '%real%' THEN 'Real Well'
             ELSE asset_type 
         END) AS slugging

FULL OUTER JOIN 
    
    (SELECT 
         CASE 
             WHEN asset_type ILIKE '%simulated%' THEN 'Simulated' 
             WHEN asset_type ILIKE '%real%' THEN 'Real Well'
             ELSE asset_type 
         END AS standardized_asset_type,
         COUNT(*) AS total_hydrates_seconds
     FROM table_hydrates
     WHERE class = 8 
     GROUP BY 
         CASE 
             WHEN asset_type ILIKE '%simulated%' THEN 'Simulated'
             WHEN asset_type ILIKE '%real%' THEN 'Real Well'
             ELSE asset_type 
         END) AS hydrates

ON slugging.standardized_asset_type = hydrates.standardized_asset_type

ORDER BY asset_classification ASC;


--INSTANTANEOUS STATISTICAL Z-SCORE ENGINE--
SELECT 
    s.well_id,
    s.entry_id AS time_tick,
    s.p_tpt AS current_raw_pressure,
    ROUND(baseline.avg_p::numeric, 2) AS healthy_historical_mean,
    ROUND(baseline.std_p::numeric, 2) AS healthy_historical_stddev,
    
        ROUND(
        ((s.p_tpt - baseline.avg_p) / NULLIF(baseline.std_p, 0))::numeric, 
        2
    ) AS instantaneous_pressure_z_score

FROM table_slugging AS s

INNER JOIN 
   
    (SELECT 
         SUBSTRING(well_id FROM 1 FOR 10) AS clean_well_id, 
         AVG(p_tpt) AS avg_p, 
         STDDEV(p_tpt) AS std_p
     FROM table_normal
     GROUP BY SUBSTRING(well_id FROM 1 FOR 10)) AS baseline
ON SUBSTRING(s.well_id FROM 1 FOR 10) = baseline.clean_well_id

WHERE s.class = 3 
ORDER BY ABS((s.p_tpt - baseline.avg_p) / NULLIF(baseline.std_p, 0)) DESC
LIMIT 5000;

--TWO-ROW SIMULATOR THERMAL FIDELITY AUDIT MATRIX--
SELECT 
    slugging_flow.asset_classification,
    ROUND(normal_flow.avg_healthy_temp::numeric, 2) AS nominal_operating_temp_c,
    ROUND(slugging_flow.avg_slugging_temp::numeric, 2) AS active_slugging_temp_c,
    
    
    ROUND((slugging_flow.avg_slugging_temp - normal_flow.avg_healthy_temp)::numeric, 2) AS simulation_thermal_shift

FROM 
    
    (SELECT 
         'Physical Field Assets' AS asset_classification,
         AVG(t_tpt) AS avg_healthy_temp
     FROM table_normal
     GROUP BY 1) AS normal_flow


RIGHT OUTER JOIN 
    
    (SELECT 
         CASE 
             WHEN asset_type ILIKE '%simulated%' THEN 'Simulated Environment'
             WHEN asset_type ILIKE '%real%' THEN 'Physical Field Assets'
             ELSE asset_type 
         END AS asset_classification,
         AVG(t_tpt) AS avg_slugging_temp
     FROM table_slugging
     WHERE class = 3
     GROUP BY 
         CASE 
             WHEN asset_type ILIKE '%simulated%' THEN 'Simulated Environment'
             WHEN asset_type ILIKE '%real%' THEN 'Physical Field Assets'
             ELSE asset_type 
         END) AS slugging_flow

ON normal_flow.asset_classification = slugging_flow.asset_classification
ORDER BY slugging_flow.asset_classification DESC;