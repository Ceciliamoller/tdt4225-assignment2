import pandas as pd
from pathlib import Path

RAW = Path("data/raw/porto.csv") # sjekk at filen er lagret her
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)

def main():
    print("Loading:", RAW)
    df = pd.read_csv(RAW)

    print("\n=== DATA CLEANING ===")
    clean_df = df.copy()

    # 1) TRIP_ID — drop duplicates
    before = len(clean_df)
    clean_df = clean_df.drop_duplicates(subset="TRIP_ID")
    print(f"• Dropped duplicate TRIP_IDs → {before - len(clean_df)} rows removed.")

    # 2) ORIGIN_STAND rule for CALL_TYPE='B' — drop rows with missing stand
    before = len(clean_df)
    mask = (clean_df["CALL_TYPE"] == "B") & (clean_df["ORIGIN_STAND"].isna())
    clean_df = clean_df[~mask]
    print(f"• Dropped {before - len(clean_df)} rows where CALL_TYPE='B' but ORIGIN_STAND was missing.")

    # 3) TIMESTAMP → DATETIME
    clean_df["DATETIME"] = pd.to_datetime(clean_df["TIMESTAMP"], unit="s", errors="coerce")
    print("• Converted TIMESTAMP → DATETIME.")

    # 4) POLYLINE — drop empty '[]'
    before_poly = len(clean_df)
    clean_df = clean_df[clean_df["POLYLINE"] != "[]"]
    print(f"• Dropped {before_poly - len(clean_df)} rows with empty POLYLINE trajectories.")

    # 5) Remove any temporary EDA columns if present
    clean_df = clean_df.drop(columns=["hour", "weekday", "n_points", "duration_min"], errors="ignore")

    # Save cleaned dataset
    out_file = OUT_DIR / "porto.cleaned.csv"
    clean_df.to_csv(out_file, index=False)
    print(f"\nCleaned dataset exported → {out_file} (final rows: {len(clean_df):,})")

if __name__ == "__main__":
    main()
