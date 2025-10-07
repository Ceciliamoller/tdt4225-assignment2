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

## TRIP_ID: Unique identier for each trip. 

# --- Basic info about TRIP_ID ---
n_rows = len(df)
n_unique = df["TRIP_ID"].nunique()
n_duplicates = df["TRIP_ID"].duplicated().sum()
n_missing = df["TRIP_ID"].isna().sum()

# --- Create a small DataFrame summary ---
trip_id_summary = pd.DataFrame({
    "Total Rows": [n_rows],
    "Unique TRIP_IDs": [n_unique],
    "Duplicate (Not Unique) TRIP_IDs": [n_duplicates],
    "Missing TRIP_IDs": [n_missing]
})

# --- Print nice table ---
print("\n=== TRIP_ID ===")
print(tabulate(trip_id_summary, headers="keys", tablefmt="psql", showindex=False))


## CALL_TYPE: Code indicating how the trip was initiated. 

# --- 1. Inspect unique values and counts
call_counts = df["CALL_TYPE"].value_counts(dropna=False)
call_percent = df["CALL_TYPE"].value_counts(normalize=True, dropna=False) * 100
missing_calltype = df["CALL_TYPE"].isna().sum()

call_summary = pd.DataFrame({
    "Count": call_counts,
    "Percent": call_percent.round(2)
}).reset_index().rename(columns={"index": "CALL_TYPE"})

# Add a summary row for missing values
missing_row = pd.DataFrame([{
    "CALL_TYPE": "Missing (NaN)",
    "Count": missing_calltype,
    "Percent": round(missing_calltype / len(df) * 100, 3)
}])

call_summary = pd.concat([call_summary, missing_row], ignore_index=True)

print("\n=== CALL_TYPE ===")
print(tabulate(call_summary, headers="keys", tablefmt="psql", showindex=False))

# --- 2. Visualize the distribution
sns.countplot(x="CALL_TYPE", data=df, palette="pastel")
plt.title("Distribution of CALL_TYPE")
plt.xlabel("Call Type (A=dispatch, B=stand, C=street pickup)")
plt.ylabel("Number of Trips")
plt.show(block=False)
plt.pause(2)   # keep it visible for 2 seconds
plt.close()


## ORIGIN_CALL: ID of the client who initiated the call 
# (only set when CALL_TYPE = ‘A’). Otherwise NULL.  --> # origin_call = # (call_type = 'A') = 364770

# --- 1. Check for missing values
missing_origin_call = df["ORIGIN_CALL"].isna().sum()
duplicate_origin_call = df["ORIGIN_CALL"].duplicated().sum()
non_missing_origin_call = len(df) - missing_origin_call
total_call_type_a = (df["CALL_TYPE"] == "A").sum()

# --- 3. Create a clear summary table
summary = pd.DataFrame({
    "Total Rows": [len(df)],
    "Non-Missing Values": [non_missing_origin_call],
    "Missing Values": [missing_origin_call],
    "Duplicates": [duplicate_origin_call],
    "CALL_TYPE = 'A' Trips": [total_call_type_a],
})

print("\n=== ORIGIN_CALL ===")
print(tabulate(summary, headers="keys", tablefmt="psql", showindex=False))

## ORIGIN_STAND: Taxi stand ID where the trip started (only set when CALL_TYPE = ‘B’). Otherwise NULL.

# --- 1. Basic stats
missing_origin_stand = df["ORIGIN_STAND"].isna().sum()
duplicate_origin_stand = df["ORIGIN_STAND"].duplicated().sum()
non_missing_origin_stand = len(df) - missing_origin_stand
total_call_type_b = (df["CALL_TYPE"] == "B").sum()

summary_stand = pd.DataFrame({
    "Total Rows": [len(df)],
    "Non-Missing Values": [non_missing_origin_stand],
    "Missing Values": [missing_origin_stand],
    "Duplicates": [duplicate_origin_stand],
    "CALL_TYPE = 'B' Trips": [total_call_type_b]
    })

print("\n=== ORIGIN_STAND ===")
print(tabulate(summary_stand, headers="keys", tablefmt="psql", showindex=False))



## TAXI_ID: Unique identier of the taxi performing the trip. The same taxi may appear in many trips. 

# --- TAXI_ID basic info ---
total_taxis = df["TAXI_ID"].nunique()
total_rows = len(df)
missing_taxi = df["TAXI_ID"].isna().sum()
trips_per_taxi = df["TAXI_ID"].value_counts()
total_trips_counted = trips_per_taxi.sum()

print("\n=== TAXI_ID ===")
print(f"• Total trips: {total_rows:,}")
print(f"• Sum of trips across taxis: {total_trips_counted:,}")
print(f"• Unique taxis: {total_taxis:,}")
print(f"• Missing TAXI_ID values: {missing_taxi:,}")
print(f"• Average trips per taxi: {trips_per_taxi.mean():.1f}")
print(f"• Most active taxi made {trips_per_taxi.max()} trips")
print(f"• Least active taxi made {trips_per_taxi.min()} trips")

# --- Visualize distribution ---
sns.histplot(trips_per_taxi, bins=50, kde=False)
plt.title("Distribution of Trips per Taxi")
plt.xlabel("Number of trips")
plt.ylabel("Count of taxis")
plt.show()


## TIMESTAMP: Start time of the trip, expressed as Unix time (seconds since 1970-01-01). 
## Should be converted to a standard DATETIME format for queries.


print("\n=== TIMESTAMP Attribute Analysis ===")

# --- 1. Basic checks ---
print("• Data type:", df["TIMESTAMP"].dtype)
print(f"• Missing values: {df['TIMESTAMP'].isna().sum():,}")

# --- 2. Convert to datetime for exploration ---
# to_datetime does the same thing as MySQL’s FROM_UNIXTIME() (from linked pdf))
df["DATETIME"] = pd.to_datetime(df["TIMESTAMP"], unit="s", errors="coerce")

# --- 3. Check conversion success ---
num_failed = df["DATETIME"].isna().sum()
print(f"• Conversion errors : {num_failed:,}")

# --- 4. Range check ---
min_time, max_time = df["DATETIME"].min(), df["DATETIME"].max()
print(f"• Earliest trip: {min_time}")
print(f"• Latest trip:   {max_time}")

# --- 5. Extract features ---
df["hour"] = df["DATETIME"].dt.hour
df["weekday"] = df["DATETIME"].dt.day_name()

# --- 6. Print summary stats ---
trip_range_days = (max_time - min_time).days
print(f"• Time span covered: {trip_range_days:,} days")
print(f"• Unique hours present: {df['hour'].nunique()}")
print(f"• Unique weekdays present: {df['weekday'].nunique()}")

# --- 7. Summaries per hour and weekday ---
hour_counts = df["hour"].value_counts().sort_index()
weekday_counts = df["weekday"].value_counts()

# --- 8. Visualize trips per hour ---
plt.figure(figsize=(8,4))
sns.countplot(x="hour", data=df, color="lightblue")
plt.title("Distribution of Trips by Hour of Day")
plt.xlabel("Hour of Day (0–23)")
plt.ylabel("Number of Trips")
plt.tight_layout()
plt.show()

# --- 9. Visualize trips per weekday ---
plt.figure(figsize=(8,4))
sns.countplot(x="weekday", data=df, order=["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"], color="lightgreen")
plt.title("Distribution of Trips by Weekday")
plt.xlabel("Day of Week")
plt.ylabel("Number of Trips")
plt.tight_layout()
plt.show()


## DAYTYPE: Indicates whether the trip occurred on a normal day, a holiday, or the day before a holiday. 
print("\n=== DAY_TYPE Attribute Analysis ===")

# --- Valid expected values ---
valid_values = ["A", "B", "C"]

# --- Identify missing and invalid values ---
missing_daytype = df["DAY_TYPE"].isna().sum()
invalid_daytype = (~df["DAY_TYPE"].isin(valid_values)) & df["DAY_TYPE"].notna()
num_invalid = invalid_daytype.sum()

# --- Count valid values ---
valid_counts = df["DAY_TYPE"].value_counts(dropna=False)

# --- Build summary table ---
day_summary = pd.DataFrame({
    "DAY_TYPE": ["A", "B", "C", "Invalid", "Missing"],
    "Count": [
        valid_counts.get("A", 0),
        valid_counts.get("B", 0),
        valid_counts.get("C", 0),
        num_invalid,
        missing_daytype
    ]
})

# --- Add percentage column (ensure total = 100%) ---
day_summary["Percent"] = (day_summary["Count"] / len(df) * 100).round(2)
day_summary.loc[day_summary.index[-1], "Percent"] = round(
    100 - day_summary["Percent"].iloc[:-1].sum(), 2
)  # ensures total = 100%

# --- Print clean summary table ---
print(tabulate(day_summary, headers="keys", tablefmt="psql", showindex=False))



# 4. Optional plot
sns.countplot(x="DAY_TYPE", data=df, palette="pastel",
              order=["A","B","C"])
plt.title("Distribution of Trips by Day Type")
plt.xlabel("Day Type (A=Normal, B=Holiday, C=Pre-Holiday)")
plt.ylabel("Number of Trips")
plt.tight_layout()
plt.show()


## MISSING_DATA: Boolean ag indicating whether there are missing GPS points in the POLYLINE. 
# FALSE means the data is complete, TRUE means some points are missing. 


print("\n=== MISSING_DATA Attribute Analysis ===")

# --- 1. Check value distribution ---
missing_counts = df["MISSING_DATA"].value_counts(dropna=False)
missing_percent = (missing_counts / len(df) * 100).round(2)

# --- 2. Combine in table ---
summary_missing = pd.DataFrame({
    "MISSING_DATA": missing_counts.index.astype(str),
    "Count": missing_counts.values,
    "Percent": missing_percent.values
}).reset_index(drop=True)

# --- 3. Add check for invalid or blank values ---
invalid_values = df[~df["MISSING_DATA"].isin([True, False])].shape[0]
summary_missing.loc[len(summary_missing)] = ["Invalid", invalid_values, round(invalid_values / len(df) * 100, 2)]

# --- 4. Print results ---
print(tabulate(summary_missing, headers="keys", tablefmt="psql", showindex=False))


## POLYLINE: A list of GPS points forming the trajectory. Each point is represented as [longitude, latitude], sampled at 15-second intervals. 
import json

print("\n=== POLYLINE Attribute Analysis ===")

# --- Count missing and empty ---
missing_poly = df["POLYLINE"].isna().sum()
empty_poly = (df["POLYLINE"] == "[]").sum()
valid_poly = len(df) - (missing_poly + empty_poly)

# --- Consistency check ---
poly_empty_and_flag_false = ((df["POLYLINE"] == "[]") & (df["MISSING_DATA"] == False)).sum()

# --- Count GPS points per trajectory ---
def count_points(polyline_str):
    try:
        return len(json.loads(polyline_str))
    except:
        return 0

df["n_points"] = df["POLYLINE"].apply(count_points)
df["duration_min"] = (df["n_points"] * 15) / 60  # each point = 15 sec

# --- Compare MISSING_DATA True vs False ---
summary_flag = (
    df.groupby("MISSING_DATA")[["n_points", "duration_min"]]
    .mean()
    .rename(columns={"n_points": "avg_points", "duration_min": "avg_duration"})
)

# --- Print compact bullet summary ---
print(f"• Total trips: {len(df):,}")
print(f"• Empty trajectories: {empty_poly:,} ({empty_poly/len(df)*100:.2f}%)")
print(f"• Valid trajectories: {valid_poly/len(df)*100:.2f}%")
print(f"• Average trip: {df['n_points'].mean():.0f} GPS points (~{df['duration_min'].mean():.0f} min)")
print(f"• Median trip: {df['n_points'].median():.0f} GPS points")
print(f"• Trips with MISSING_DATA=True: "
      f"{summary_flag.loc[True, 'avg_points']:.0f} GPS points (~{summary_flag.loc[True, 'avg_duration']:.0f} min)")
print(f"• Trips with MISSING_DATA=False: "
      f"{summary_flag.loc[False, 'avg_points']:.0f} GPS points (~{summary_flag.loc[False, 'avg_duration']:.0f} min)")
print(f"• Rows where POLYLINE='[]' but MISSING_DATA=False: {poly_empty_and_flag_false}")

''' 
# ta vekk?:
# --- 6️⃣ Visualize trajectory length distribution ---
plt.figure(figsize=(8,4))
sns.histplot(df["n_points"], bins=50, color="skyblue", kde=False)
plt.title("Distribution of Number of GPS Points per Trip")
plt.xlabel("Number of GPS Points")
plt.ylabel("Count of Trips")
plt.xlim(0, 200)  # crop extreme outliers for better readability
plt.tight_layout()
plt.show()

# --- 7️⃣ Visualize trip duration (minutes) ---
plt.figure(figsize=(8,4))
sns.histplot(df["duration_min"], bins=50, color="lightgreen", kde=False)
plt.title("Distribution of Trip Duration (minutes)")
plt.xlabel("Duration (minutes)")
plt.ylabel("Count of Trips")
plt.xlim(0, 60)
plt.tight_layout()
plt.show()
'''




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
print(tabulate(other_stats, headers=["Metric", "Count"], tablefmt="grid")) 


# TRIP_ID — Trip Identifier
df["TRIP_ID"].duplicated().sum() --SKAL DENNE MED?
"""

# ===============================================================
# 🧹 DATA CLEANING FOR MYSQL INSERTION
# ===============================================================
print("\n=== DATA CLEANING ===")

clean_df = df.copy()

# --- 1. TRIP_ID ---
# Drop 81 duplicates to ensure each trip_id is unique
clean_df = clean_df.drop_duplicates(subset="TRIP_ID")
print("• Dropped duplicate TRIP_IDs → now unique.")

# --- 2. CALL_TYPE ---
# No issue found — keep as is
print("• CALL_TYPE: no changes needed.")

# --- 3. ORIGIN_CALL ---
# No issues found — keep as is
print("• ORIGIN_CALL: no changes needed.")

# --- 4. ORIGIN_STAND ---
# Found 11,302 missing for CALL_TYPE = 'B' → drop those rows
before = len(clean_df)
clean_df = clean_df[~((clean_df["CALL_TYPE"] == "B") & (clean_df["ORIGIN_STAND"].isna()))]
after = len(clean_df)
print(f"• Dropped {before - after} rows where CALL_TYPE='B' but ORIGIN_STAND was missing.")

# --- 5. TAXI_ID ---
# No issue found
print("• TAXI_ID: no changes needed.")

# --- 6. TIMESTAMP ---
# Convert Unix timestamp → readable datetime (important for SQL)
clean_df["DATETIME"] = pd.to_datetime(clean_df["TIMESTAMP"], unit="s", errors="coerce")
print("• Converted TIMESTAMP → DATETIME for database queries.")

# --- 7. DAY_TYPE ---
# No issue found
print("• DAY_TYPE: no changes needed.")

# --- 8. MISSING_DATA ---
# Only 10 out of 1.7M rows had missing GPS data
# → Keep them (important info for analysis later)
print("• MISSING_DATA: retained (only 10 rows had True).")

# --- 9. POLYLINE ---
# Found 5901 empty trajectories ('[]') → drop those
before_poly = len(clean_df)
clean_df = clean_df[clean_df["POLYLINE"] != "[]"]
after_poly = len(clean_df)
print(f"• Dropped {before_poly - after_poly} rows with empty POLYLINE trajectories.")

# --- Save cleaned dataset ---
clean_df.to_csv("cleaned_porto.csv", index=False)
print(f"\n✅ Cleaned dataset exported → cleaned_porto.csv (final rows: {len(clean_df):,})")


