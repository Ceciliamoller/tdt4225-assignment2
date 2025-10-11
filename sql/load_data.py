# sql/load_data.py
import pandas as pd
from pathlib import Path
from DbConnector import DbConnector

TRIPS_CSV = Path("data/processed/porto_trips.cleaned.csv")
POINTS_CSV = Path("data/processed/porto_trip_points.cleaned.csv")
TMP_TAXIS = Path("data/processed/_taxis.distinct.csv")
TMP_STANDS = Path("data/processed/_stands.distinct.csv")

def ensure_distinct_files():
    df = pd.read_csv(TRIPS_CSV, usecols=["taxi_id","origin_stand"])
    if not TMP_TAXIS.exists():
        df[["taxi_id"]].drop_duplicates().to_csv(TMP_TAXIS, index=False)
    if not TMP_STANDS.exists():
        s = df["origin_stand"].dropna().drop_duplicates().astype("Int64")
        s.to_frame("stand_id").to_csv(TMP_STANDS, index=False)

def main():
    assert TRIPS_CSV.exists(), f"Missing {TRIPS_CSV}"
    assert POINTS_CSV.exists(), f"Missing {POINTS_CSV}"
    ensure_distinct_files()

    db = DbConnector(local_infile=True)
    conn = db.db_connection
    cur = db.cursor

    def run(sql):
        cur.execute(sql)

    print("Enabling local_infile for this session…")
    run("SET SESSION local_infile = 1;")
    print("Disabling FK checks for faster load…")
    run("SET FOREIGN_KEY_CHECKS = 0;")
    conn.commit()

    try:
        # taxis
        print("Loading taxis…")
        run(f"""
            LOAD DATA LOCAL INFILE '{TMP_TAXIS.resolve()}'
            INTO TABLE taxis
            FIELDS TERMINATED BY ',' ENCLOSED BY '"'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            (taxi_id);
        """)
        # stands
        print("Loading stands…")
        run(f"""
            LOAD DATA LOCAL INFILE '{TMP_STANDS.resolve()}'
            INTO TABLE stands
            FIELDS TERMINATED BY ',' ENCLOSED BY '"'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            (stand_id);
        """)
        # trips
        print("Loading trips…")
        run(f"""
            LOAD DATA LOCAL INFILE '{TRIPS_CSV.resolve()}'
            INTO TABLE trips
            FIELDS TERMINATED BY ',' ENCLOSED BY '"'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            (@trip_id,@taxi_id,@call_type,@origin_call,@origin_stand,
             @start_ts,@day_type,@missing_data,@points_count,@duration_s,
             @start_lon,@start_lat,@end_lon,@end_lat,@polyline)
            SET trip_id=@trip_id,
                taxi_id=@taxi_id,
                call_type=@call_type,
                origin_call = NULLIF(@origin_call,''),
                origin_stand = NULLIF(@origin_stand,''),
                start_ts=STR_TO_DATE(@start_ts,'%Y-%m-%d %H:%i:%s'),
                day_type=@day_type,
                missing_data=@missing_data,
                points_count=@points_count,
                duration_s=@duration_s,
                start_point=ST_SRID(POINT(@start_lon,@start_lat),4326),
                end_point=ST_SRID(POINT(@end_lon,@end_lat),4326),
                polyline=NULLIF(@polyline,'');
        """)

        # trip_points
        print("Loading trip_points… this can take a while on big files")
        run(f"""
            LOAD DATA LOCAL INFILE '{POINTS_CSV.resolve()}'
            INTO TABLE trip_points
            FIELDS TERMINATED BY ',' ENCLOSED BY '"'
            LINES TERMINATED BY '\n'
            IGNORE 1 LINES
            (@trip_id,@seq_idx,@ts,@lon,@lat)
            SET trip_id=@trip_id,
                seq_idx=@seq_idx,
                ts=STR_TO_DATE(@ts,'%Y-%m-%d %H:%i:%s'),
                lon=@lon,
                lat=@lat,
                pt=ST_SRID(POINT(@lon,@lat),4326);
        """)

        conn.commit()
        print("Re-enabling FK checks…")
        run("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()

        # sanity counts
        for t in ("taxis","stands","trips","trip_points"):
            run(f"SELECT COUNT(*) FROM {t};")
            print(f"{t}: {cur.fetchone()[0]:,}")

    finally:
        db.close_connection()

if __name__ == "__main__":
    main()
