# TDT4225 Assignment 2 — MySQL schema

Schema for the Porto taxi dataset. It’s normalized and fast to query. 


## Repo layout

```
sql/schema.sql ->  tables + indexes
sql/views.sql ->  optional helper views
src/schema.py -> applies schema.sql
src/views.py -> applies views.sql

```

## Data exploration

Data exploration is done in **`EDA.py`**, which checks each column, shows basic statistics, and plots distributions to understand the dataset. It doesn’t change or save any data.


## Notes

* The schema mirrors the CSV but adds a few helpful columns so Part 2 queries are straightforward and fast.
* Views are just convenience wrappers, not necessary.

### Schema setup

The database schema defines tables for taxis, stands, trips, and trip_points in the assignment_2 database. Trips store metadata and precomputed fields like points_count and duration_s, plus spatial columns with SRID 4326 for start_point and end_point. trip_points stores every GPS point with a sequence index, timestamp, and a spatial point. 

#### Run the schema

```bash
python src/schema.py
```


### Cleaning setup

The cleaning script prepares the raw Porto dataset for the database. It removes rows with empty POLYLINE and rows flagged as MISSING_DATA. For duplicate TRIP_ID it keeps the version with the longest POLYLINE. CALL_TYPE B with missing ORIGIN_STAND is kept and stored as NULL. Timestamps are converted to DATETIME, and fields like points_count, duration_s, start and end coordinates are precomputed.

#### Run the cleaner

```bash
python sql/clean_porto.py
```

Outputs

- data/processed/porto_trips.cleaned.csv
-> one row per trip with precomputed fields

- data/processed/porto_trip_points.cleaned.csv
-> one row per GPS point with trip_id, seq_idx, ts, lon, lat

### Data loading

The data loading script uses bulk loading to insert all cleaned data into the database efficiently.

#### Run the loader

```bash
python sql/load_data.py
```


