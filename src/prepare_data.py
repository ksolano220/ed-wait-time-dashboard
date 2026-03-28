"""
Clean and prepare CMS ED data for the dashboard.

Filters to ED-related measures, cleans scores, and pivots into
a hospital-level dataset with one row per facility.
"""

import pandas as pd
from pathlib import Path

RAW_PATH = Path("data/timely_effective_care.csv")
OUT_PATH = Path("data/ed_hospitals.csv")

ED_MEASURES = {
    "OP_18b": "median_ed_time_min",
    "OP_18a": "median_ed_time_all_min",
    "OP_18c": "median_ed_time_psych_min",
    "OP_22": "left_before_seen_pct",
    "EDV": "ed_volume",
}


def prepare():
    df = pd.read_csv(RAW_PATH, encoding="latin-1", dtype={"Facility ID": str})

    # Filter to ED measures only
    ed = df[df["Condition"] == "Emergency Department"].copy()

    # Pivot measures into columns per hospital
    hospitals = (
        ed[ed["Measure ID"] == "EDV"][
            ["Facility ID", "Facility Name", "City/Town", "State", "County/Parish", "ZIP Code"]
        ]
        .drop_duplicates(subset=["Facility ID"])
        .set_index("Facility ID")
    )

    for measure_id, col_name in ED_MEASURES.items():
        measure_data = ed[ed["Measure ID"] == measure_id][["Facility ID", "Score"]].copy()
        measure_data = measure_data.drop_duplicates(subset=["Facility ID"])
        measure_data = measure_data.set_index("Facility ID")
        measure_data.columns = [col_name]

        if col_name != "ed_volume":
            measure_data[col_name] = pd.to_numeric(measure_data[col_name], errors="coerce")

        hospitals = hospitals.join(measure_data, how="left")

    # Also grab sample size from OP_18b
    sample_data = ed[ed["Measure ID"] == "OP_18b"][["Facility ID", "Sample"]].copy()
    sample_data = sample_data.drop_duplicates(subset=["Facility ID"]).set_index("Facility ID")
    sample_data.columns = ["sample_size"]
    sample_data["sample_size"] = pd.to_numeric(sample_data["sample_size"], errors="coerce")
    hospitals = hospitals.join(sample_data, how="left")

    hospitals = hospitals.reset_index()
    hospitals.columns = [
        "facility_id", "facility_name", "city", "state", "county", "zip_code",
        "median_ed_time_min", "median_ed_time_all_min", "median_ed_time_psych_min",
        "left_before_seen_pct", "ed_volume", "sample_size",
    ]

    # Drop hospitals with no usable data
    hospitals = hospitals.dropna(subset=["median_ed_time_min"])

    OUT_PATH.parent.mkdir(exist_ok=True)
    hospitals.to_csv(OUT_PATH, index=False)

    print(f"Prepared {len(hospitals)} hospitals → {OUT_PATH}")
    print(f"\nState count: {hospitals['state'].nunique()}")
    print(f"Median ED wait: {hospitals['median_ed_time_min'].median():.0f} min")
    print(f"Range: {hospitals['median_ed_time_min'].min():.0f} – {hospitals['median_ed_time_min'].max():.0f} min")
    print(f"\nVolume distribution:")
    print(hospitals["ed_volume"].value_counts().to_string())


if __name__ == "__main__":
    prepare()
