# TDT4225 Assignment 2 — MySQL schema

Schema for the Porto taxi dataset. It’s normalized and fast to query. 

## What’s inside

* **Tables:** `taxis`, `trips`, `trip_points`
  *(optional: `stands` if you want a FK for `ORIGIN_STAND`)*
* **Derived in `trips`:** `points_count`, `duration_s` (15-sec sampling), `distance_m` (haversine)
* **Spatial:** `start_point`, `end_point` (SRID 4326)
* **Views (optional):** `v_trip_timebands`, `v_midnight_crossers`

## Repo layout

```
sql/schema.sql ->  tables + indexes
sql/views.sql ->  optional helper views
src/schema.py -> applies schema.sql
src/views.py -> applies views.sql

```

## Data exploration

Data exploration is done in **`EDA.py`**, which checks each column, shows basic statistics, and plots distributions to understand the dataset. It doesn’t change or save any data.

## Cleaning

Cleaning is done in **`src/clean_porto.py`**, which removes duplicate trips, handles missing values, converts timestamps, and drops rows with empty routes. The cleaned data is saved to `data/processed/porto.cleaned.csv`.


## Notes

* The schema mirrors the CSV but adds a few helpful columns so Part 2 queries are straightforward and fast.
* Views are just convenience wrappers, not necessary.


