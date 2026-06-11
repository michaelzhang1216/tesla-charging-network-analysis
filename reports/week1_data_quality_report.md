# Week 1 Data Quality Assessment Report

## 1. Overview

This report summarizes the initial data quality assessment for the raw datasets collected in Week 1. The assessment focuses on dataset size, field coverage, missing values, duplicate records, and key field availability.

## 2. Database Summary

| Table | Rows | Columns | Duplicate Rows |
|---|---:|---:|---:|
| iea_ev_data_explorer_2026_raw | 49176 | 9 | 15 |
| kaggle_global_ev_charging_station_raw | 257585 | 19 | 3 |
| openchargemap_charging_stations_sample | 133026 | 17 | 223 |
| tesla_deliveries_2015_2025_raw | 2640 | 12 | 0 |
| us_alt_fuel_stations_historical_raw | 95300 | 75 | 0 |
| world_bank_gdp_country_raw | 266 | 71 | 0 |
| world_bank_income_level_country_raw | 265 | 6 | 0 |
| world_bank_population_raw | 17191 | 41 | 0 |
| world_bank_road_density_raw | 1103 | 38 | 0 |

## 3. Table-Level Quality Checks

### 3.x iea_ev_data_explorer_2026_raw

- Rows: 49176
- Columns: 9
- Duplicate rows: 15

**Column names:**

region_country, category, parameter, mode, powertrain, year, unit, value, aggregate_group

**Top missing-value fields:**

| Field | Missing Count | Missing Rate (%) |
|---|---:|---:|
| unit | 22582 | 45.92 |
| region_country | 1078 | 2.19 |
| category | 0 | 0.0 |
| mode | 0 | 0.0 |
| parameter | 0 | 0.0 |
| powertrain | 0 | 0.0 |
| year | 0 | 0.0 |
| value | 0 | 0.0 |
| aggregate_group | 0 | 0.0 |

### 3.x kaggle_global_ev_charging_station_raw

- Rows: 257585
- Columns: 19
- Duplicate rows: 3

**Column names:**

stationid, uuid, dataproviderid, operator, usagetype, usagecost, addresstitle, addressline1, town, stateorprovince, postcode, country, latitude, longitude, maxpowerkw, fastchargecount, connectiontypes, statustype, yearcreated

**Top missing-value fields:**

| Field | Missing Count | Missing Rate (%) |
|---|---:|---:|
| usagecost | 195766 | 76.0 |
| stateorprovince | 74752 | 29.02 |
| operator | 39225 | 15.23 |
| statustype | 36392 | 14.13 |
| usagetype | 35116 | 13.63 |
| postcode | 27075 | 10.51 |
| town | 22756 | 8.83 |
| connectiontypes | 4876 | 1.89 |
| addressline1 | 1817 | 0.71 |
| addresstitle | 5 | 0.0 |

### 3.x openchargemap_charging_stations_sample

- Rows: 133026
- Columns: 17
- Duplicate rows: 223

**Column names:**

id, uuid, station_title, operator, usage_type, status, country, iso_code, state_or_province, town, address_line_1, postcode, latitude, longitude, number_of_connections, date_created, date_last_verified

**Top missing-value fields:**

| Field | Missing Count | Missing Rate (%) |
|---|---:|---:|
| date_last_verified | 133026 | 100.0 |
| state_or_province | 51494 | 38.71 |
| usage_type | 29554 | 22.22 |
| operator | 23750 | 17.85 |
| status | 21610 | 16.24 |
| postcode | 10907 | 8.2 |
| town | 8500 | 6.39 |
| address_line_1 | 70 | 0.05 |
| id | 0 | 0.0 |
| iso_code | 0 | 0.0 |

### 3.x tesla_deliveries_2015_2025_raw

- Rows: 2640
- Columns: 12
- Duplicate rows: 0

**Column names:**

year, month, region, model, estimated_deliveries, production_units, avg_price_usd, battery_capacity_kwh, range_km, co2_saved_tons, source_type, charging_stations

**Top missing-value fields:**

| Field | Missing Count | Missing Rate (%) |
|---|---:|---:|
| year | 0 | 0.0 |
| month | 0 | 0.0 |
| region | 0 | 0.0 |
| model | 0 | 0.0 |
| estimated_deliveries | 0 | 0.0 |
| production_units | 0 | 0.0 |
| avg_price_usd | 0 | 0.0 |
| battery_capacity_kwh | 0 | 0.0 |
| range_km | 0 | 0.0 |
| co2_saved_tons | 0 | 0.0 |

### 3.x us_alt_fuel_stations_historical_raw

- Rows: 95300
- Columns: 75
- Duplicate rows: 0

**Column names:**

fuel_type_code, station_name, street_address, intersection_directions, city, state, zip, plus4, station_phone, status_code, expected_date, groups_with_access_code, access_days_time, cards_accepted, bd_blends, ng_fill_type_code, ng_psi, ev_level1_evse_num, ev_level2_evse_num, ev_dc_fast_count, ev_other_info, ev_network, ev_network_web, geocode_status, latitude, longitude, date_last_confirmed, id, updated_at, owner_type_code, federal_agency_id, federal_agency_name, open_date, hydrogen_status_link, ng_vehicle_class, lpg_primary, e85_blender_pump, ev_connector_types, country, intersection_directions_french, access_days_time_french, bd_blends_french, groups_with_access_code_french, hydrogen_is_retail, access_code, access_detail_code, federal_agency_code, facility_type, cng_dispenser_num, cng_on_site_renewable_source, cng_total_compression_capacity, cng_storage_capacity, lng_on_site_renewable_source, e85_other_ethanol_blends, ev_pricing, ev_pricing_french, lpg_nozzle_types, hydrogen_pressures, hydrogen_standards, cng_fill_type_code, cng_psi, cng_vehicle_class, lng_vehicle_class, ev_on_site_renewable_source, restricted_access, rd_blends, rd_blends_french, rd_blended_with_biodiesel, rd_maximum_biodiesel_level, nps_unit_name, cng_station_sells_renewable_natural_gas, lng_station_sells_renewable_natural_gas, maximum_vehicle_class, ev_workplace_charging, funding_sources

**Key field check:**

- All predefined key fields are present.

**Top missing-value fields:**

| Field | Missing Count | Missing Rate (%) |
|---|---:|---:|
| expected_date | 95300 | 100.0 |
| plus4 | 95300 | 100.0 |
| cng_storage_capacity | 95300 | 100.0 |
| hydrogen_status_link | 95300 | 100.0 |
| ng_vehicle_class | 95300 | 100.0 |
| e85_blender_pump | 95300 | 100.0 |
| lpg_primary | 95300 | 100.0 |
| bd_blends_french | 95300 | 100.0 |
| ng_psi | 95300 | 100.0 |
| ng_fill_type_code | 95300 | 100.0 |

### 3.x world_bank_gdp_country_raw

- Rows: 266
- Columns: 71
- Duplicate rows: 0

**Column names:**

country_name, country_code, indicator_name, indicator_code, 1960, 1961, 1962, 1963, 1964, 1965, 1966, 1967, 1968, 1969, 1970, 1971, 1972, 1973, 1974, 1975, 1976, 1977, 1978, 1979, 1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987, 1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000, 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, unnamed:_70

**Key field check:**

- All predefined key fields are present.

**Top missing-value fields:**

| Field | Missing Count | Missing Rate (%) |
|---|---:|---:|
| unnamed:_70 | 266 | 100.0 |
| 2025 | 266 | 100.0 |
| 1960 | 115 | 43.23 |
| 1961 | 112 | 42.11 |
| 1963 | 110 | 41.35 |
| 1964 | 110 | 41.35 |
| 1962 | 110 | 41.35 |
| 1965 | 104 | 39.1 |
| 1966 | 103 | 38.72 |
| 1967 | 99 | 37.22 |

### 3.x world_bank_income_level_country_raw

- Rows: 265
- Columns: 6
- Duplicate rows: 0

**Column names:**

country_code, region, incomegroup, specialnotes, tablename, unnamed:_5

**Key field check:**

- All predefined key fields are present.

**Top missing-value fields:**

| Field | Missing Count | Missing Rate (%) |
|---|---:|---:|
| unnamed:_5 | 265 | 100.0 |
| specialnotes | 132 | 49.81 |
| incomegroup | 50 | 18.87 |
| region | 48 | 18.11 |
| country_code | 0 | 0.0 |
| tablename | 0 | 0.0 |

### 3.x world_bank_population_raw

- Rows: 17191
- Columns: 41
- Duplicate rows: 0

**Column names:**

datastructure, wb_data360:ds_data3601_3, i, a, vnm, wb_wdi_sp_pop_totl, _t, _t_1, _t_2, ps, _z, _z_1, _z_2, 1999, 7_6287452e7, _z_3, count, 2, wb_wdi, p1y, 0, a_1, pu, annual, vietnam, population,_total, total, all_age_ranges_or_no_breakdown_by_age, total_1, persons, not_applicable, not_applicable_1, not_applicable_2, not_applicable_3, count_integer, two, world_development_indicators_wdi, annual_1, units, normal_value, public

**Key field check:**

- Missing key fields: country_name, country_code, indicator_name, indicator_code

**Top missing-value fields:**

| Field | Missing Count | Missing Rate (%) |
|---|---:|---:|
| datastructure | 0 | 0.0 |
| wb_data360:ds_data3601_3 | 0 | 0.0 |
| i | 0 | 0.0 |
| a | 0 | 0.0 |
| vnm | 0 | 0.0 |
| wb_wdi_sp_pop_totl | 0 | 0.0 |
| _t | 0 | 0.0 |
| _t_1 | 0 | 0.0 |
| _t_2 | 0 | 0.0 |
| ps | 0 | 0.0 |

### 3.x world_bank_road_density_raw

- Rows: 1103
- Columns: 38
- Duplicate rows: 0

**Column names:**

datastructure, wb_data360:ds_data3601_2, i, a, annual, alb, albania, wef_ttdi_roaddens, road_density,_km_surface_area, _t, total, _t_1, all_age_ranges_or_no_breakdown_by_age, _t_2, total_1, km, kilometers, wef_ttdi_val, type:_value, _z, not_applicable, _z_1, not_applicable_1, 2021, 68_03394160583942, wef_ttdi, travel_&_tourism_development_index_ttdi, 0, units, number, number_real_number, 602, ccyy, euromonitor_road_network_data_divided_by_land_area, a_1, normal_value, pu, public

**Top missing-value fields:**

| Field | Missing Count | Missing Rate (%) |
|---|---:|---:|
| euromonitor_road_network_data_divided_by_land_area | 36 | 3.26 |
| 68_03394160583942 | 12 | 1.09 |
| i | 0 | 0.0 |
| a | 0 | 0.0 |
| datastructure | 0 | 0.0 |
| wb_data360:ds_data3601_2 | 0 | 0.0 |
| alb | 0 | 0.0 |
| annual | 0 | 0.0 |
| albania | 0 | 0.0 |
| wef_ttdi_roaddens | 0 | 0.0 |

## 4. Initial Findings

- Multiple raw data sources have been successfully collected and loaded into the SQLite database.
- Charging station datasets contain useful geographic fields such as latitude and longitude, which will support spatial analysis in later stages.
- Some datasets contain missing values in operator, usage type, status, or metadata fields. These fields should be reviewed during Week 2 data cleaning.
- World Bank datasets may have different structures depending on the indicator source. Some files may require reshaping from wide format to long country-year format.
- Dataset merging should not be performed in Week 1. Standardization, deduplication, and integration should be conducted in Week 2.

## 5. Next Steps

- Standardize country names and country codes across charging station, EV sales, and external factor datasets.
- Convert World Bank yearly wide-format data into long format for country-year analysis.
- Identify Tesla-related charging stations from broader charging station datasets.
- Check duplicate stations using station name, operator, address, latitude, and longitude.
- Build a cleaned dataset for exploratory data analysis in Week 2.
