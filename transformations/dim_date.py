import pandas as pd
from pathlib import Path


# ============================================================
# PROJECT DIRECTORIES
# ============================================================

PROJECT_ROOT = Path("/opt/supply-chain")

OUTPUT_DIR = (
    PROJECT_ROOT
    / "data"
    / "processed"
    / "dimensions"
)

OUTPUT_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# TRANSFORM DATE DATA
# ============================================================

def transform_date():

    print("=" * 60)
    print("DATE DIMENSION TRANSFORMATION")
    print("=" * 60)

    # --------------------------------------------------------
    # 1. Define date range
    # --------------------------------------------------------

    start_date = "2020-01-01"
    end_date = "2026-12-31"

    dates = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D"
    )

    dim_date = pd.DataFrame(
        {
            "full_date": dates
        }
    )

    print(
        f"Dates generated: "
        f"{len(dim_date):,}"
    )

    # --------------------------------------------------------
    # 2. Create date key
    # --------------------------------------------------------

    dim_date["date_key"] = (
        dim_date["full_date"]
        .dt.strftime("%Y%m%d")
        .astype(int)
    )

    # --------------------------------------------------------
    # 3. Create year
    # --------------------------------------------------------

    dim_date["year"] = (
        dim_date["full_date"]
        .dt.year
    )

    # --------------------------------------------------------
    # 4. Create quarter
    # --------------------------------------------------------

    dim_date["quarter"] = (
        dim_date["full_date"]
        .dt.quarter
    )

    # --------------------------------------------------------
    # 5. Create month
    # --------------------------------------------------------

    dim_date["month"] = (
        dim_date["full_date"]
        .dt.month
    )

    # --------------------------------------------------------
    # 6. Create month name
    # --------------------------------------------------------

    dim_date["month_name"] = (
        dim_date["full_date"]
        .dt.month_name()
    )

    # --------------------------------------------------------
    # 7. Create week number
    # --------------------------------------------------------

    dim_date["week"] = (
        dim_date["full_date"]
        .dt.isocalendar()
        .week
        .astype(int)
    )

    # --------------------------------------------------------
    # 8. Create day
    # --------------------------------------------------------

    dim_date["day"] = (
        dim_date["full_date"]
        .dt.day
    )

    # --------------------------------------------------------
    # 9. Create day name
    # --------------------------------------------------------

    dim_date["day_name"] = (
        dim_date["full_date"]
        .dt.day_name()
    )

    # --------------------------------------------------------
    # 10. Identify weekends
    # --------------------------------------------------------

    dim_date["is_weekend"] = (
        dim_date["full_date"]
        .dt.dayofweek
        >= 5
    )

    # --------------------------------------------------------
    # 11. Reorder columns
    # --------------------------------------------------------

    dim_date = dim_date[
        [
            "date_key",
            "full_date",
            "year",
            "quarter",
            "month",
            "month_name",
            "week",
            "day",
            "day_name",
            "is_weekend"
        ]
    ]

    # --------------------------------------------------------
    # 12. Validation
    # --------------------------------------------------------

    if dim_date["date_key"].duplicated().any():

        raise ValueError(
            "Duplicate date_key found."
        )

    if dim_date["full_date"].duplicated().any():

        raise ValueError(
            "Duplicate full_date found."
        )

    if dim_date["date_key"].isnull().any():

        raise ValueError(
            "Null date_key found."
        )

    # --------------------------------------------------------
    # 13. Write output
    # --------------------------------------------------------

    output_file = (
        OUTPUT_DIR / "dim_date.csv"
    )

    dim_date.to_csv(
        output_file,
        index=False
    )

    # --------------------------------------------------------
    # 14. Print summary
    # --------------------------------------------------------

    print(
        f"Date range: "
        f"{start_date} to {end_date}"
    )

    print(
        f"Transformed records: "
        f"{len(dim_date):,}"
    )

    print(
        f"Output written to: "
        f"{output_file}"
    )

    print(
        "Date dimension transformation "
        "completed successfully."
    )

    return dim_date


# ============================================================
# STANDALONE EXECUTION
# ============================================================

if __name__ == "__main__":

    transform_date()