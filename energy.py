"""Cohort-specific fuel and electricity accounting for the public demo."""

from __future__ import annotations

import pandas as pd

ASSUMPTION_COLUMNS = (
    "Technology",
    "SalesYear",
    "FuelConsumption_L_per_100km",
    "ElectricityConsumption_kWh_per_100km",
    "UtilityFactor",
    "AnnualVKT_km",
    "VehicleMass_kg",
)


def calculate_cohort_energy(
    cohort_stock: pd.DataFrame,
    assumptions: pd.DataFrame,
) -> pd.DataFrame:
    """Apply each sales cohort's own FC, EC, UF and VKT to surviving stock.

    This function deliberately joins assumptions on both ``Technology`` and
    ``SalesYear``. It therefore does not apply a current-year new-vehicle
    efficiency value to vehicles sold in earlier years.
    """

    stock_required = {
        "Market",
        "Technology",
        "SalesYear",
        "Year",
        "Age",
        "StockVehicles",
    }
    missing_stock = sorted(stock_required - set(cohort_stock.columns))
    missing_assumptions = [
        column for column in ASSUMPTION_COLUMNS if column not in assumptions
    ]
    if missing_stock or missing_assumptions:
        raise ValueError(
            f"Missing stock columns={missing_stock}; "
            f"missing assumption columns={missing_assumptions}"
        )

    assumption_data = assumptions.loc[:, ASSUMPTION_COLUMNS].copy()
    numeric_columns = ASSUMPTION_COLUMNS[2:]
    assumption_data["SalesYear"] = pd.to_numeric(
        assumption_data["SalesYear"], errors="raise"
    ).astype(int)
    for column in numeric_columns:
        assumption_data[column] = pd.to_numeric(
            assumption_data[column], errors="raise"
        )

    if assumption_data.duplicated(["Technology", "SalesYear"]).any():
        raise ValueError("Assumptions must be unique by Technology and SalesYear")
    if not assumption_data["UtilityFactor"].between(0.0, 1.0).all():
        raise ValueError("UtilityFactor must remain between 0 and 1")
    nonnegative = [
        "FuelConsumption_L_per_100km",
        "ElectricityConsumption_kWh_per_100km",
        "AnnualVKT_km",
        "VehicleMass_kg",
    ]
    if (assumption_data[nonnegative] < 0).any(axis=None):
        raise ValueError("Energy and vehicle assumptions cannot be negative")

    result = cohort_stock.merge(
        assumption_data,
        on=["Technology", "SalesYear"],
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    missing_keys = result.loc[
        result["_merge"] != "both", ["Technology", "SalesYear"]
    ].drop_duplicates()
    if not missing_keys.empty:
        raise ValueError(f"Missing cohort assumptions:\n{missing_keys}")
    result = result.drop(columns="_merge")

    activity_per_100km = (
        result["StockVehicles"] * result["AnnualVKT_km"] / 100.0
    )
    result["TotalVKT_km"] = result["StockVehicles"] * result["AnnualVKT_km"]
    result["LiquidFuelVKT_km"] = (
        result["TotalVKT_km"] * (1.0 - result["UtilityFactor"])
    )
    result["Fuel_L"] = (
        activity_per_100km
        * result["FuelConsumption_L_per_100km"]
        * (1.0 - result["UtilityFactor"])
    )
    result["Electricity_kWh"] = (
        activity_per_100km
        * result["ElectricityConsumption_kWh_per_100km"]
        * result["UtilityFactor"]
    )
    return result
