# Clientz – some data loaders for analysts

This Python project contains some generic data loading and caching tools usable in implementing
clients for data APIs. Below are examples for existing modules for querying data from different services.

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

## Inderes

Download fundamentals for various Finnish companies listed in Helsinki stock exchange.

```python

from clientz.services import inderes

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

### Apartment prices

### Paavo

