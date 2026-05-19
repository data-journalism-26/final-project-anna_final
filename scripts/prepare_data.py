import pandas as pd
import json
from pathlib import Path

# -------------------
# PATHS
# -------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA = BASE_DIR / "data" / "Data.csv"
OUTPUT = BASE_DIR / "output"

OUTPUT.mkdir(exist_ok=True)

# -------------------
# LOAD DATA
# -------------------

df = pd.read_csv(DATA)

# convert numeric safely
for col in ["pli", "gdp_pps", "hicp", "median_income"]:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# -------------------
# MAP (2015)
# -------------------

map_df = df[df["TIME_PERIOD"] == 2015].dropna(subset=["pli"])

map_data = {
    "geo": map_df["geo"].tolist(),
    "pli": map_df["pli"].tolist()
}

with open(OUTPUT / "map.json", "w") as f:
    json.dump(map_data, f)

# -------------------
# LINE CHART
# -------------------

countries = [
    "Poland",
    "Bulgaria",
    "Romania",
    "Hungary",
    "Czechia",
    "Germany",
    "Austria",
    "France",
    "Netherlands"
]

line_df = df[df["geo"].isin(countries)]

line_data = []

for country in countries:

    subset = line_df[line_df["geo"] == country].sort_values("TIME_PERIOD")
    subset = subset.dropna(subset=["pli"])

    line_data.append({
        "country": country,
        "year": subset["TIME_PERIOD"].tolist(),
        "pli": subset["pli"].tolist()
    })

with open(OUTPUT / "linechart.json", "w") as f:
    json.dump(line_data, f)

# -------------------
# SCATTER (LATEST YEAR)
# -------------------

latest_year = df["TIME_PERIOD"].max()

scatter_df = df[df["TIME_PERIOD"] == latest_year].copy()
scatter_df = scatter_df.dropna(subset=["gdp_pps", "median_income"])

scatter_data = {
    "geo": scatter_df["geo"].tolist(),
    "gdp_pps": scatter_df["gdp_pps"].tolist(),
    "median_income": scatter_df["median_income"].tolist()
}

with open(OUTPUT / "scatter.json", "w") as f:
    json.dump(scatter_data, f)

# -------------------
# INFLATION (2021–2023 REAL VERSION)
# -------------------

years_needed = [2021, 2022, 2023]

df_inf = df[df["TIME_PERIOD"].isin(years_needed)].copy()

merged = []

for geo in df_inf["geo"].unique():

    d_geo = df_inf[df_inf["geo"] == geo]

    r21 = d_geo[d_geo["TIME_PERIOD"] == 2021]
    r22 = d_geo[d_geo["TIME_PERIOD"] == 2022]
    r23 = d_geo[d_geo["TIME_PERIOD"] == 2023]

    if r21.empty or r23.empty:
        continue

    pli21 = r21["pli"].values[0]
    pli23 = r23["pli"].values[0]

    hicp_2022 = r22["hicp"].values[0] if not r22.empty else None

    if pd.isna(pli21) or pd.isna(pli23):
        continue

    merged.append({
        "geo": geo,
        "hicp": float(hicp_2022) if pd.notna(hicp_2022) else None,
        "pli_change": float(pli23 - pli21)
    })

inflation_data = {
    "geo": [m["geo"] for m in merged],
    "hicp": [m["hicp"] for m in merged],
    "pli_change": [m["pli_change"] for m in merged]
}

with open(OUTPUT / "inflation.json", "w") as f:
    json.dump(inflation_data, f)

# -------------------
# DONE
# -------------------

print("✔ MAP saved")
print("✔ LINE saved")
print("✔ SCATTER saved")
print("✔ INFLATION saved")
print("Pipeline completed successfully.")