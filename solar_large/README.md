
# Energy Investment Dashboard

**From public energy-market data to investment decisions** — an end-to-end analytics project in Python, SQL, Power BI and Microsoft Fabric.

The dashboard connects three questions an investment committee asks about renewable-energy assets in the Netherlands:

1. **Market** — What do solar and wind actually earn, given *when* they produce?
2. **Investment** — Which projects clear the hurdle rate, how certain is that, and which assumptions could break the case?
3. **Impact** — How much CO₂ does each project avoid, measured transparently and consistently?

> **Status:** in development. See the [roadmap](#roadmap) for what is built and what is next.

---

## Architecture

| Layer          | What happens                                                | Skills                              |
| -------------- | ----------------------------------------------------------- | ----------------------------------- |
| Python         | Notebooks ingest data and run the investment models         | Python, pandas, PySpark, Delta      |
| Lakehouse      | Raw data stored as received (bronze), then cleaned (silver) | Data quality, MERGE, time zones     |
| Warehouse      | Star schema with fact and dimension tables                  | SQL, dimensional modelling          |
| Semantic model | Measures and relationships                                  | DAX, Direct Lake                    |
| Report         | Three pages: Market, Investment, ESG                        | Visualisation, data storytelling    |
| Fabric         | Daily refresh pipeline, Git integration                     | Microsoft Fabric, CI-style workflow |

---

## Data sources

| Source                                                          | Data                                                                 | Used for                                                  |
| --------------------------------------------------------------- | -------------------------------------------------------------------- | --------------------------------------------------------- |
| [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/) | Day-ahead prices, generation per fuel type, load, cross-border flows | Market page, capture rates, battery spreads, CO₂ profile |
| [KNMI Data Platform](https://dataplatform.knmi.nl/)              | Hourly solar radiation and wind speed                                | Explaining generation, price forecasting                  |
| TenneT                                                          | Imbalance prices, balancing services                                 | Battery business case                                     |
| [CBS StatLine](https://opendata.cbs.nl/)                         | Installed capacity, energy balance                                   | Context, regional dimension                               |
| Klimaatmonitor                                                  | Renewable energy per municipality                                    | Regional analysis                                         |
| Netbeheer Nederland capacity map                                | Grid congestion                                                      | Grid-congestion layer                                     |
| RVO                                                             | SDE++ base amounts and conditions                                    | Solar model assumptions                                   |
| [co2emissiefactoren.nl](https://www.co2emissiefactoren.nl/)      | Official Dutch emission factors                                      | ESG page                                                  |

Raw data is not committed to this repository. Check each source's terms of use before redistributing data.

---

## Repository structure

```
energy-investment-dashboard/
├── README.md
├── requirements.txt
├── models/                 # Investment models (Python)
│   ├── solar/              # Solar project: cash flows, SDE++, IRR, NPV, DSCR
│   ├── bess/               # Battery storage: day-ahead and balancing revenues
│   └── ppa/                # PPA vs. merchant: capture prices
├── notebooks/
│   ├── 01_ingest_entsoe.ipynb
│   ├── 02_bronze_to_silver.ipynb
│   └── 03_run_models.ipynb
├── sql/                    # Warehouse views for the star schema
├── powerbi/                # Power BI Project (.pbip) for version control
├── docs/
│   ├── methodology.md      # Assumptions, emission factors, limitations
│   └── img/                # Screenshots
├── tests/                  # Data-quality and model tests
└── data/
    └── sample/             # Small sample files for running locally
```

---

## Data engineering notes

Energy data has a few traps that this project handles explicitly:

* **Time.** All timestamps are stored in UTC; local time (Europe/Amsterdam) is derived. Daylight saving time creates 23- and 25-hour days.
* **Resolution.** The European day-ahead market moved from hourly to 15-minute products for delivery day 1 October 2025. Silver keeps quarter-hours and adds a separate hourly table so periods remain comparable.
* **Units.** MW is power, MWh is energy: a quarter-hour at 100 MW is 25 MWh.
* **Duplicates.** Re-ingested days are upserted with `MERGE` on timestamp and bidding zone.
* **Missing values** are flagged, never silently filled.
* **Negative prices** are real and kept — they are central to the PPA and battery cases.
* **Quality checks.** Each run verifies 96 quarter-hours per day (92 or 100 on clock-change days); the pipeline stops on deviations.

---

## Data model

**Market**

**Investment**

| Fact table           | Grain (one row per)                |
| -------------------- | ---------------------------------- |
| `fact_price`       | zone × quarter-hour               |
| `fact_generation`  | zone × technology × quarter-hour |
| `fact_cashflow`    | project × scenario × run × year |
| `fact_kpi`         | project × scenario × run         |
| `fact_montecarlo`  | project × run × simulation       |
| `fact_sensitivity` | project × run × assumption       |

Design choices: date and time are separate dimensions to keep the model small; prices and generation share conformed dimensions rather than joining directly; `dim_project` carries a `technology_key` that links each investment to its market data; `dim_run` makes every model run traceable and comparable.

---

## Key measures

**Capture rate** — what solar or wind actually earns relative to the average market price:

dax

```dax
Capture price =
VAR Revenue =
    SUMX (
        CROSSJOIN ( VALUES ( dim_date[date_key] ), VALUES ( dim_time[time_key] ),
                    VALUES ( dim_zone[zone_key] ) ),
        [Generation MWh] * [Avg price]
    )
RETURN DIVIDE ( Revenue, [Generation MWh] )

Capture rate = DIVIDE ( [Capture price], [Avg price] )
```

**Downside risk** — probability that a project's IRR falls below a user-selected hurdle rate:

dax

```dax
Probability below hurdle =
VAR Hurdle = [Hurdle IRR Value]   -- what-if parameter
RETURN
    DIVIDE (
        CALCULATE ( COUNTROWS ( fact_montecarlo ), fact_montecarlo[irr] < Hurdle ),
        COUNTROWS ( fact_montecarlo )
    )
```

Other measures include negative-price quarter-hours, average daily price spread, CO₂ emissions and grid intensity (g/kWh), IRR versus base scenario, and IRR P10/P90.

---

## Report pages

**Market** — Capture rates of solar and wind by month, a price heatmap by hour and month, negative-price frequency and the average daily generation mix. Shows why solar cannibalises its own price and why batteries earn money.

**Investment** — An investment-committee view: IRR, NPV, minimum DSCR and probability of missing the hurdle rate; a risk-return portfolio plot; a tornado chart of key assumptions; the Monte Carlo IRR distribution; annual cash flows with DSCR. Model assumptions are tested against observed market capture rates.

**ESG** — Grid CO₂ intensity by hour, avoided emissions per project and per million euros invested, hourly matching of renewable supply to demand, and EU Taxonomy status per project. Average and marginal emission factors can be toggled; avoided emissions are reported separately from Scope 1–3, and the methodology is documented in `docs/methodology.md`.

---

## Roadmap

* [ ] **v1 — Power BI Desktop:** ENTSO-E prices and generation (2024–2025), star schema, Market page
* [ ] Solar project model with IRR, NPV, DSCR, sensitivities and Monte Carlo
* [ ] Battery storage model with day-ahead and balancing revenues
* [ ] **v2 — Microsoft Fabric:** Lakehouse (bronze/silver), Warehouse, refresh pipeline, Git integration
* [ ] **v3 — Investment and ESG pages:** portfolio view, risk analysis, impact metrics
* [ ] PPA pricing model (PPA vs. merchant)

---

## Getting started

bash

```bash
git clone https://github.com/tjebbel/energy-investment-dashboard.git
cd energy-investment-dashboard
pip install -r requirements.txt
```

1. Download Dutch day-ahead prices and generation per production type from the ENTSO-E Transparency Platform, or request a free API token to automate ingestion.
2. Run the notebooks in order (`01` → `03`) to build the bronze, silver and model tables.
3. Open the Power BI project in `powerbi/` and refresh.

---

## Tech stack

Python (pandas, NumPy, SciPy, PySpark) · SQL · Power BI (DAX, semantic modelling) · Microsoft Fabric (Lakehouse, Warehouse, Data Pipelines, Direct Lake) · Git

---

## About

Built by **Tjebbe Lodeizen** — finance professional with 8+ years across energy (Vattenfall, Groendus), capital markets (Euronext) and healthcare (Philips), focused on the energy transition and sustainable finance.

[LinkedIn](https://www.linkedin.com/in/tjebbe-lodeizen-33194125) · [GitHub](https://github.com/tjebbel)

*Data sources are credited above. Emission factors, DSCR thresholds and model assumptions are indicative; see the methodology notes for limitations.*
