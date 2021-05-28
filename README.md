# Pandas-datastores – Data downloading and caching to Pandas data types

This Python project contains some generic data loading and caching tools usable
in implementing query clients for data APIs. Below are examples for existing modules
for querying data from different services.

<!-- markdown-toc start - Don't edit this section. Run M-x markdown-toc-refresh-toc -->
**Table of Contents**

- [Finnish Meteorological Institute](#finnish-meteorological-institute)
- [Inderes](#inderes)
- [Statistics Finland](#statistics-finland)
    - [Apartment prices](#apartment-prices)
    - [Paavo](#paavo)
- [Installation](#installation)

<!-- markdown-toc end -->


## Finnish Meteorological Institute

Downloading hourly two-day forecasts from the HIRLAM weather model supported.
The data source contains various quantities.

```python

from stores.services import fmi


api = fmi.API()
helsinki = fmi.Helsinki().download(api)
# helsinki.head().ilod[:, :5]
# 
#                     GeopHeight  Temperature  Pressure  Humidity  WindDirection
# 2020-12-21 22:00:00        6.99         3.59   1016.37     94.73          217.0
# 2020-12-21 23:00:00        6.99         3.68   1016.34     95.29          218.0
# 2020-12-22 00:00:00        6.99         3.88   1016.07     95.83          219.0
# 2020-12-22 01:00:00        6.99         3.94   1015.48     96.23          214.0
# 2020-12-22 02:00:00        6.99         3.99   1015.41     96.47          215.0
# 

```

Under the hood the code uses the following (for arbitrary European geolocation):

```python

data = api.forecast_hirlam_surface_point_hourly_2d.get(lat=60.1699, lon=24.9384)

```

### NOTE

Dependencies: `bs4`, `lxml`, `user_agent`.

## Inderes

Download fundamentals for various Finnish companies listed in Helsinki stock exchange.

```python

from stores.services import inderes


api = inderes.API()

# Data table containing various fundamentals
data_table = inderes.DataTable().download(api)

# Data table with forecasts for next year
forecast = inderes.CompanyForecast().download(api)

# Price-to-earnings ratios
pe = inderes.PriceToEarnings(year="this").download(api)
#
# pe[pe > 0]
# 
# As of 2020/12/22:
# 
# Sievi Capital      8.450682
# Suominen           9.960260
# Innofactor        11.958954
# TietoEVRY         11.969733
# Wulff-Yhtiöt      12.126051
#                     ...
# EAB Group        164.849497
# CapMan           187.390689
# LeadDesk         236.682867
# Glaston          259.793814
# Nixu             548.839458
# Length: 89, dtype: float64
# 

# Price-to-book values
pb = inderes.PriceToBook(year="next").download(api)

```

## Statistics Finland

Querying historical Finnish apartment price data.

```python

from stores.services import statfin


api = statfin.API()
kontula = statfin.QuarterlyZip("00940")
# 
# kontula.iloc[[42, 123, 141]]
# 
#      Postinumero  Talotyyppi Vuosineljännes  keskihinta_ptno  lkm_julk
# 42           940           1     2020-07-01              NaN         2
# 123          940           3     2019-04-01           2142.0        37
# 141          940           4     2013-01-01              NaN        37
#
house_types = statfin.HouseTypes().download(api)
#
# house_types
# 
# {'1': 'Kerrostalo yksiöt',
#  '2': 'Kerrostalo kaksiot',
#  '3': 'Kerrostalo kolmiot+',
#  '4': 'Kerrostalot yhteensä',
#  '5': 'Rivitalot yhteensä',
#  '6': 'Talotyypit yhteensä'}
# 

```

### Apartment prices

### Paavo

## Oikotie

