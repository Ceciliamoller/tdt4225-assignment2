import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from tabulate import tabulate
import json
import seaborn as sns
import matplotlib.pyplot as plt


# Last inn CSV
df = pd.read_csv("porto.csv")  # eller hva filen heter

print("=" * 80)
print("DATASET OVERVIEW")
print("=" * 80)
print(f"Total rows: {len(df)}")
print(f"Total columns: {len(df.columns)}")

""" # 1. Undersøk alle kolonner
print("\n=== COLUMN INFORMATION ===")
info_data = []
for col in df.columns:
    info_data.append(
        [
            col,
            df[col].dtype,
            df[col].isnull().sum(),
            f"{df[col].isnull().sum() / len(df) * 100:.2f}%",
        ]
    )
print(
    tabulate(
        info_data, headers=["Column", "Type", "Missing", "% Missing"], tablefmt="grid"
    )
) """

""" # 2. Analyser TRIP_ID
print("\n=== TRIP_ID ANALYSIS ===")
trip_stats = [
    ["Total trips", len(df)],
    ["Unique TRIP_IDs", df["TRIP_ID"].nunique()],
    ["Duplicate TRIP_IDs", len(df) - df["TRIP_ID"].nunique()],
]
print(tabulate(trip_stats, headers=["Metric", "Count"], tablefmt="grid")) """

""" # 3. Analyser CALL_TYPE
print("\n=== CALL_TYPE DISTRIBUTION ===")
call_type = df["CALL_TYPE"].value_counts(dropna=False).reset_index()
call_type.columns = ["Call Type", "Count"]
call_type["Percentage"] = (call_type["Count"] / len(df) * 100).round(2)

# Erstatt NaN med "Missing" for bedre lesbarhet
call_type["Call Type"] = call_type["Call Type"].fillna("Missing/NULL")

print(tabulate(call_type, headers="keys", tablefmt="grid", showindex=False))


def analyze_categorical_with_plot(df, column_name, title):
    print(f"\n=== {title} ===")

    # Tell verdier inkludert missing
    dist = df[column_name].value_counts(dropna=False).reset_index()
    dist.columns = [column_name, "Count"]
    dist["Percentage"] = (dist["Count"] / len(df) * 100).round(2)

    # Erstatt NaN med lesbart navn
    dist[column_name] = dist[column_name].fillna("Missing/NULL")

    print(tabulate(dist, headers="keys", tablefmt="grid", showindex=False))

    # Ekstra info om missing
    missing = df[column_name].isnull().sum()
    if missing > 0:
        print(
            f"Warning: {missing} rows ({missing/len(df)*100:.2f}%) have missing {column_name}"
        )

    # Visualisering med seaborn
    plt.figure(figsize=(10, 6))
    sns.barplot(
        data=dist,
        x=column_name,
        y="Count",
        palette="viridis",
        hue=column_name,
        legend=False,
    )
    plt.xlabel(column_name, fontsize=12)
    plt.ylabel("Count", fontsize=12)
    plt.title(f"{title}", fontsize=14, fontweight="bold")
    plt.xticks(rotation=45, ha="right")

    # Legg til prosentverdier på toppen av hver bar
    for i, (val, pct) in enumerate(zip(dist["Count"], dist["Percentage"])):
        plt.text(i, val, f"{pct}%", ha="center", va="bottom", fontsize=10)

    plt.tight_layout()
    plt.savefig(f"{column_name}_distribution.png", dpi=300, bbox_inches="tight")
    plt.show()
    print(f"Plot saved as '{column_name}_distribution.png'\n")


# Bruk funksjonen:
analyze_categorical_with_plot(df, "CALL_TYPE", "CALL_TYPE DISTRIBUTION")
analyze_categorical_with_plot(df, "DAY_TYPE", "DAY_TYPE DISTRIBUTION") """


""" # 4. Analyser DAY_TYPE
print("\n=== DAY_TYPE DISTRIBUTION ===")
day_type = df["DAY_TYPE"].value_counts().reset_index()
day_type.columns = ["Day Type", "Count"]
day_type["Percentage"] = (day_type["Count"] / len(df) * 100).round(2)
print(tabulate(day_type, headers="keys", tablefmt="grid", showindex=False))

# 5. VIKTIGST: Analyser POLYLINE (trajectories)
print("\n=== POLYLINE ANALYSIS ===")

# Telle missing/empty
missing_polyline = df["POLYLINE"].isnull().sum()
empty_polyline = (df["POLYLINE"] == "[]").sum()
valid_polyline = len(df) - missing_polyline - empty_polyline

polyline_summary = [
    ["Missing (NaN)", missing_polyline, f"{missing_polyline/len(df)*100:.2f}%"],
    ["Empty ([])", empty_polyline, f"{empty_polyline/len(df)*100:.2f}%"],
    ["Valid trajectories", valid_polyline, f"{valid_polyline/len(df)*100:.2f}%"],
    ["Total", len(df), "100.00%"],
]
print(
    tabulate(
        polyline_summary, headers=["Status", "Count", "Percentage"], tablefmt="grid"
    )
)


# Analyser lengde på trajectories
def get_trajectory_length(polyline):
    if pd.isna(polyline) or polyline == "[]":
        return 0
    try:
        coords = json.loads(polyline)
        return len(coords)
    except:
        return 0


df["traj_length"] = df["POLYLINE"].apply(get_trajectory_length)

print("\n=== TRAJECTORY LENGTH STATISTICS ===")
stats = df["traj_length"].describe()
stats_table = [[stat, f"{value:.2f}"] for stat, value in stats.items()]
print(tabulate(stats_table, headers=["Statistic", "Value"], tablefmt="grid"))

# 6. Analyser MISSING_DATA flag
print("\n=== MISSING_DATA FLAG ===")
missing_flag = df["MISSING_DATA"].value_counts().reset_index()
missing_flag.columns = ["Flag", "Count"]
missing_flag["Percentage"] = (missing_flag["Count"] / len(df) * 100).round(2)
print(tabulate(missing_flag, headers="keys", tablefmt="grid", showindex=False))

# 7. Analyser andre kolonner (TAXI_ID, ORIGIN_CALL, etc.)
print("\n=== OTHER ATTRIBUTES ===")
other_stats = [
    ["Unique Taxis", df["TAXI_ID"].nunique()],
    ["Unique ORIGIN_CALLs", df["ORIGIN_CALL"].nunique()],
    ["Unique ORIGIN_STANDs", df["ORIGIN_STAND"].nunique()],
    ["NULL ORIGIN_CALLs", df["ORIGIN_CALL"].isnull().sum()],
    ["NULL ORIGIN_STANDs", df["ORIGIN_STAND"].isnull().sum()],
]
print(tabulate(other_stats, headers=["Metric", "Count"], tablefmt="grid")) """
