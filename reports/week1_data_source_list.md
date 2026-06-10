# Week 1 Data Source List

## 1. Tesla Charging Station Data

### 1.1 Tesla Official Supercharger Website
- Source: Tesla official Supercharger page
- URL: https://www.tesla.com/supercharger
- Data type: Official charging network information
- Expected fields: station location, availability, charging network overview
- Access method: website reference
- Cost: free
- Notes: Used as official reference source.

### 1.2 OpenChargeMap API
- Source: OpenChargeMap
- URL: https://www.openchargemap.org/develop/api
- Data type: global charging station data
- Expected fields: station name, latitude, longitude, operator, charger type, power, country
- Access method: API
- Cost: free with possible API limits
- Notes: May require API key.

### 1.3 Kaggle Global EV Charging Station Network Dataset
- Source: Kaggle
- URL: https://www.kaggle.com/datasets/sohails07/global-ev-charging-station-network-2010-2026
- Data type: global EV charging station dataset
- Expected fields: location, operator, number of chargers, power, opening time
- Access method: manual download or Kaggle API
- Cost: free Kaggle account required
- Notes: Need to verify data quality and update frequency.

## 2. EV Sales and Stock Data

### 2.1 IEA Global EV Data Explorer
- Source: International Energy Agency
- URL: https://www.iea.org/data-and-statistics/data-tools/global-ev-data-explorer
- Data type: EV sales and stock by country and year
- Expected fields: country, year, powertrain, sales, stock
- Access method: data explorer download
- Cost: free/public access
- Notes: Useful for measuring potential charging demand.

### 2.2 Tesla Investor Relations
- Source: Tesla Investor Relations
- URL: https://ir.tesla.com/
- Data type: Tesla delivery, production, and business data
- Expected fields: quarter, production, deliveries, region if available
- Access method: reports and financial filings
- Cost: free
- Notes: Used as official Tesla business reference.

## 3. External Factor Data

### 3.1 World Bank Open Data
- Source: World Bank
- URL: https://data.worldbank.org/
- Data type: population, GDP, urbanization, income indicators
- Expected fields: country, year, population, GDP, GDP per capita, urban population
- Access method: CSV download or API
- Cost: free
- Notes: Useful for country-level demand and coverage analysis.

### 3.2 OpenStreetMap / Geofabrik
- Source: OpenStreetMap / Geofabrik
- URL: https://download.geofabrik.de/
- Data type: road network and geographic data
- Expected fields: roads, highways, locations
- Access method: data download
- Cost: free
- Notes: Can support later spatial analysis and site coverage analysis.