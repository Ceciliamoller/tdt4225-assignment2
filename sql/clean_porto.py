import json
import csv  # Added to handle the CSV file
import pandas as pd
from pathlib import Path

RAW = Path("data/raw/porto.csv")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def polyline_len(poly):
    """Return number of GPS points in a POLYLINE string."""
    if isinstance(poly, str):
        try:
            return len(json.loads(poly))
        except Exception:
            return 0
    return 0


def main():
    print("Loading:", RAW)
    df = pd.read_csv(RAW)

    # --- Cleaning rules ---

    df = df[df["POLYLINE"] != "[]"].copy()

    df = df[df["MISSING_DATA"] == False].copy()

    df["__n_points"] = df["POLYLINE"].apply(polyline_len)
    idx = df.groupby("TRIP_ID")["__n_points"].idxmax()
    df = df.loc[idx].copy()

    df["DATETIME"] = pd.to_datetime(df["TIMESTAMP"], unit="s", errors="coerce")

    df["points_count"] = df["__n_points"].astype("int64")
    df["duration_s"] = (df["points_count"].clip(lower=1) - 1) * 15

    def first_last(poly):
        pts = json.loads(poly)
        lon0, lat0 = pts[0]
        lonN, latN = pts[-1]
        return pd.Series([lon0, lat0, lonN, latN])

    df[["start_lon", "start_lat", "end_lon", "end_lat"]] = df["POLYLINE"].apply(
        first_last
    )

    trips_cols = [
        "TRIP_ID",
        "TAXI_ID",
        "CALL_TYPE",
        "ORIGIN_CALL",
        "ORIGIN_STAND",
        "DATETIME",
        "DAY_TYPE",
        "MISSING_DATA",
        "points_count",
        "duration_s",
        "start_lon",
        "start_lat",
        "end_lon",
        "end_lat",
        "POLYLINE",
    ]
    trips_out = df[trips_cols].rename(
        columns={
            "TRIP_ID": "trip_id",
            "TAXI_ID": "taxi_id",
            "CALL_TYPE": "call_type",
            "ORIGIN_CALL": "origin_call",
            "ORIGIN_STAND": "origin_stand",
            "DATETIME": "start_ts",
            "DAY_TYPE": "day_type",
            "MISSING_DATA": "missing_data",
        }
    )

    trips_path = OUT_DIR / "porto_trips.cleaned.csv"
    trips_out.to_csv(trips_path, index=False)
    print(f"→ {trips_path}  rows={len(trips_out):,}")

    # Write GPS points incrementally to avoid memory issues
    points_path = OUT_DIR / "porto_trip_points.cleaned.csv"

    # Open CSV file and write header immediately
    with open(points_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["trip_id", "seq_idx", "ts", "lon", "lat"])  # Header

        total_points = 0
        # Process one trip at a time
        for idx, (trip_id, start_ts, poly) in enumerate(
            zip(trips_out["trip_id"], trips_out["start_ts"], df["POLYLINE"])
        ):
            # Show progress every 100k trips
            if idx % 100000 == 0:
                print(
                    f"  Processing trip {idx:,} / {len(trips_out):,}  (points written: {total_points:,})"
                )

            pts = json.loads(poly)
            for i, (lon, lat) in enumerate(pts):
                ts = start_ts + pd.to_timedelta(15 * i, unit="s")
                writer.writerow([trip_id, i, ts, lon, lat])  # Write immediately to file
                total_points += 1

    print(f"→ {points_path} rows={total_points:,}")


if __name__ == "__main__":
    main()
