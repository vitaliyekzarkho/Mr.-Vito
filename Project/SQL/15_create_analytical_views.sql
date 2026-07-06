DROP VIEW IF EXISTS vw_homelessness_rate_per_10000;
DROP VIEW IF EXISTS vw_demographic_profile;
DROP VIEW IF EXISTS vw_accommodation_profile;
DROP VIEW IF EXISTS vw_rent_pressure;
DROP VIEW IF EXISTS vw_housing_affordability;
DROP VIEW IF EXISTS vw_unemployment_context;

CREATE VIEW vw_homelessness_rate_per_10000 AS
WITH population_by_region AS (
    SELECT
        b.homelessness_region,
        p.year AS population_year,
        SUM(p.population) AS population
    FROM dim_geography_bridge AS b
    INNER JOIN clean_population AS p
        ON b.county = p.county
    GROUP BY
        b.homelessness_region,
        p.year
)
SELECT
    h.homelessness_region,
    p.population_year,
    h.total_adults AS homeless_adults,
    p.population,
    ROUND((CAST(h.total_adults AS REAL) / p.population) * 10000, 2) AS homeless_adults_per_10000
FROM clean_homelessness AS h
INNER JOIN population_by_region AS p
    ON h.homelessness_region = p.homelessness_region;

CREATE VIEW vw_demographic_profile AS
SELECT
    homelessness_region,
    'gender' AS profile_type,
    'Male' AS category,
    male_adults AS adults,
    total_adults,
    ROUND((CAST(male_adults AS REAL) / total_adults) * 100, 2) AS share_pct
FROM clean_homelessness
UNION ALL
SELECT
    homelessness_region,
    'gender' AS profile_type,
    'Female' AS category,
    female_adults AS adults,
    total_adults,
    ROUND((CAST(female_adults AS REAL) / total_adults) * 100, 2) AS share_pct
FROM clean_homelessness
UNION ALL
SELECT
    homelessness_region,
    'age' AS profile_type,
    '18-24' AS category,
    adults_18_24 AS adults,
    total_adults,
    ROUND((CAST(adults_18_24 AS REAL) / total_adults) * 100, 2) AS share_pct
FROM clean_homelessness
UNION ALL
SELECT
    homelessness_region,
    'age' AS profile_type,
    '25-44' AS category,
    adults_25_44 AS adults,
    total_adults,
    ROUND((CAST(adults_25_44 AS REAL) / total_adults) * 100, 2) AS share_pct
FROM clean_homelessness
UNION ALL
SELECT
    homelessness_region,
    'age' AS profile_type,
    '45-64' AS category,
    adults_45_64 AS adults,
    total_adults,
    ROUND((CAST(adults_45_64 AS REAL) / total_adults) * 100, 2) AS share_pct
FROM clean_homelessness
UNION ALL
SELECT
    homelessness_region,
    'age' AS profile_type,
    '65+' AS category,
    adults_65_plus AS adults,
    total_adults,
    ROUND((CAST(adults_65_plus AS REAL) / total_adults) * 100, 2) AS share_pct
FROM clean_homelessness;

CREATE VIEW vw_accommodation_profile AS
SELECT
    homelessness_region,
    'Private Emergency Accommodation' AS accommodation_type,
    private_emergency_accommodation AS adults,
    total_adults,
    ROUND((CAST(private_emergency_accommodation AS REAL) / total_adults) * 100, 2) AS share_of_total_adults_pct
FROM clean_homelessness
UNION ALL
SELECT
    homelessness_region,
    'Supported Temporary Accommodation' AS accommodation_type,
    supported_temporary_accommodation AS adults,
    total_adults,
    ROUND((CAST(supported_temporary_accommodation AS REAL) / total_adults) * 100, 2) AS share_of_total_adults_pct
FROM clean_homelessness
UNION ALL
SELECT
    homelessness_region,
    'Temporary Emergency Accommodation' AS accommodation_type,
    temporary_emergency_accommodation AS adults,
    total_adults,
    ROUND((CAST(temporary_emergency_accommodation AS REAL) / total_adults) * 100, 2) AS share_of_total_adults_pct
FROM clean_homelessness
UNION ALL
SELECT
    homelessness_region,
    'Other Accommodation' AS accommodation_type,
    other_accommodation AS adults,
    total_adults,
    ROUND((CAST(other_accommodation AS REAL) / total_adults) * 100, 2) AS share_of_total_adults_pct
FROM clean_homelessness;

CREATE VIEW vw_rent_pressure AS
WITH rent_by_region AS (
    SELECT
        b.homelessness_region,
        r.year,
        r.half,
        r.half_year,
        ROUND(AVG(r.rent_euro), 2) AS avg_rent_euro,
        ROUND(
            SUM(r.rent_euro * p.population) / SUM(p.population),
            2
        ) AS population_weighted_avg_rent_euro,
        COUNT(DISTINCT r.county) AS county_count
    FROM clean_rent AS r
    INNER JOIN dim_geography_bridge AS b
        ON r.county = b.county
    INNER JOIN clean_population AS p
        ON r.county = p.county
    GROUP BY
        b.homelessness_region,
        r.year,
        r.half,
        r.half_year
)
SELECT
    rr.homelessness_region,
    rr.year,
    rr.half,
    rr.half_year,
    rr.avg_rent_euro,
    rr.population_weighted_avg_rent_euro,
    rr.county_count,
    hr.population_year,
    hr.homeless_adults,
    hr.population,
    hr.homeless_adults_per_10000
FROM rent_by_region AS rr
INNER JOIN vw_homelessness_rate_per_10000 AS hr
    ON rr.homelessness_region = hr.homelessness_region;

CREATE VIEW vw_housing_affordability AS
WITH housing_by_region AS (
    SELECT
        b.homelessness_region,
        hs.year,
        ROUND(
            SUM(hs.mean_sale_price * p.population) / SUM(p.population),
            2
        ) AS population_weighted_mean_sale_price,
        ROUND(
            SUM(CASE WHEN hs.median_annual_earnings IS NOT NULL THEN hs.median_annual_earnings * p.population END)
            / SUM(CASE WHEN hs.median_annual_earnings IS NOT NULL THEN p.population END),
            2
        ) AS population_weighted_median_annual_earnings,
        SUM(hs.total_dwellings_built) AS total_dwellings_built,
        ROUND(SUM(hs.estimated_total_floor_area_sqm), 2) AS estimated_total_floor_area_sqm,
        ROUND(
            SUM(CASE WHEN hs.price_per_sqm IS NOT NULL THEN hs.price_per_sqm * p.population END)
            / SUM(CASE WHEN hs.price_per_sqm IS NOT NULL THEN p.population END),
            2
        ) AS population_weighted_price_per_sqm,
        COUNT(DISTINCT hs.county) AS county_count
    FROM clean_housing AS hs
    INNER JOIN dim_geography_bridge AS b
        ON hs.county = b.county
    INNER JOIN clean_population AS p
        ON hs.county = p.county
    GROUP BY
        b.homelessness_region,
        hs.year
)
SELECT
    hb.homelessness_region,
    hb.year,
    hb.population_weighted_mean_sale_price,
    hb.population_weighted_median_annual_earnings,
    ROUND(
        hb.population_weighted_mean_sale_price / hb.population_weighted_median_annual_earnings,
        2
    ) AS price_to_income_ratio,
    hb.total_dwellings_built,
    ROUND((CAST(hb.total_dwellings_built AS REAL) / hr.population) * 10000, 2) AS dwellings_built_per_10000,
    hb.estimated_total_floor_area_sqm,
    hb.population_weighted_price_per_sqm,
    hb.county_count,
    hr.population_year,
    hr.homeless_adults,
    hr.population,
    hr.homeless_adults_per_10000
FROM housing_by_region AS hb
INNER JOIN vw_homelessness_rate_per_10000 AS hr
    ON hb.homelessness_region = hr.homelessness_region;

CREATE VIEW vw_unemployment_context AS
WITH headline_unemployment AS (
    SELECT
        year,
        nuts2_region,
        unemployment_rate
    FROM clean_unemployment
    WHERE age_group = 'All ages'
      AND sex = 'Both sexes'
      AND education_attainment_level = 'Levels of Education (Levels 0-8)'
),
region_nuts2 AS (
    SELECT
        homelessness_region,
        nuts2_region,
        COUNT(DISTINCT county) AS county_count_in_nuts2
    FROM dim_geography_bridge
    GROUP BY
        homelessness_region,
        nuts2_region
),
region_nuts2_count AS (
    SELECT
        homelessness_region,
        COUNT(DISTINCT nuts2_region) AS nuts2_count
    FROM dim_geography_bridge
    GROUP BY homelessness_region
)
SELECT
    rn.homelessness_region,
    rn.nuts2_region,
    hu.year,
    hu.unemployment_rate,
    rn.county_count_in_nuts2,
    rnc.nuts2_count,
    CASE
        WHEN rnc.nuts2_count = 1 THEN 'Direct NUTS2 join safe'
        ELSE 'Mixed NUTS2 region - interpret with caution'
    END AS unemployment_join_note,
    hr.population_year,
    hr.homeless_adults,
    hr.population,
    hr.homeless_adults_per_10000
FROM region_nuts2 AS rn
INNER JOIN region_nuts2_count AS rnc
    ON rn.homelessness_region = rnc.homelessness_region
INNER JOIN headline_unemployment AS hu
    ON rn.nuts2_region = hu.nuts2_region
INNER JOIN vw_homelessness_rate_per_10000 AS hr
    ON rn.homelessness_region = hr.homelessness_region;
