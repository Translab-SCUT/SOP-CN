"""Generic sales-cohort stock accounting used in the public demonstration."""

from __future__ import annotations

import pandas as pd

SALES_COLUMNS = ("Market", "Technology", "SalesYear", "SalesVehicles")
SURVIVAL_COLUMNS = ("Age", "SurvivalProbability")


def build_cohort_stock(
    sales: pd.DataFrame,
    survival: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> pd.DataFrame:
    """Expand annual sales into surviving stock by sales cohort and model year.

    Each row remains tied to its original ``SalesYear``. This identity is
    preserved for downstream cohort-specific energy-intensity calculations.
    """

    if end_year < start_year:
        raise ValueError("end_year must be greater than or equal to start_year")

    missing_sales = [column for column in SALES_COLUMNS if column not in sales]
    missing_survival = [column for column in SURVIVAL_COLUMNS if column not in survival]
    if missing_sales or missing_survival:
        raise ValueError(
            f"Missing sales columns={missing_sales}; "
            f"missing survival columns={missing_survival}"
        )

    sales_data = sales.loc[:, SALES_COLUMNS].copy()
    survival_data = survival.loc[:, SURVIVAL_COLUMNS].copy()
    sales_data["SalesYear"] = pd.to_numeric(
        sales_data["SalesYear"], errors="raise"
    ).astype(int)
    sales_data["SalesVehicles"] = pd.to_numeric(
        sales_data["SalesVehicles"], errors="raise"
    )
    survival_data["Age"] = pd.to_numeric(
        survival_data["Age"], errors="raise"
    ).astype(int)
    survival_data["SurvivalProbability"] = pd.to_numeric(
        survival_data["SurvivalProbability"], errors="raise"
    )

    if (sales_data["SalesVehicles"] < 0).any():
        raise ValueError("SalesVehicles cannot be negative")
    if survival_data["Age"].duplicated().any():
        raise ValueError("Survival table must contain one row per vehicle age")
    if not survival_data["SurvivalProbability"].between(0.0, 1.0).all():
        raise ValueError("SurvivalProbability must remain between 0 and 1")

    survival_by_age = survival_data.set_index("Age")["SurvivalProbability"]
    records: list[dict[str, object]] = []

    for row in sales_data.itertuples(index=False):
        first_year = max(int(start_year), int(row.SalesYear))
        for year in range(first_year, int(end_year) + 1):
            age = year - int(row.SalesYear)
            if age not in survival_by_age.index:
                continue
            probability = float(survival_by_age.loc[age])
            records.append(
                {
                    "Market": row.Market,
                    "Technology": row.Technology,
                    "SalesYear": int(row.SalesYear),
                    "Year": year,
                    "Age": age,
                    "SalesVehicles": float(row.SalesVehicles),
                    "SurvivalProbability": probability,
                    "StockVehicles": float(row.SalesVehicles) * probability,
                }
            )

    columns = (
        "Market",
        "Technology",
        "SalesYear",
        "Year",
        "Age",
        "SalesVehicles",
        "SurvivalProbability",
        "StockVehicles",
    )
    return pd.DataFrame.from_records(records, columns=columns)

