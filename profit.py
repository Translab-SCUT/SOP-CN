"""Annual manufacturer-profit objective used by subsidy optimization."""

from __future__ import annotations

import pandas as pd


def calculate_annual_manufacturer_profit(sales_costs: pd.DataFrame) -> tuple[pd.DataFrame, float]:
    """Calculate per-vehicle margin and annual total manufacturer profit.

    Internal subsidy is already deducted from ``ConsumerPrice_CNY`` and is not
    added back as manufacturer revenue. Government subsidies are added back.
    ``SalesVehicles`` is measured in vehicles, not thousands of vehicles.
    """

    required = {
        "ConsumerPrice_CNY",
        "PurchaseTax_CNY",
        "Insurance_CNY",
        "AdditionalSubsidy_CNY",
        "CentralSubsidy_CNY",
        "LocalSubsidy_CNY",
        "ProductionCost_CNY",
        "SalesVehicles",
    }
    missing = sorted(required - set(sales_costs.columns))
    if missing:
        raise ValueError(f"Missing manufacturer-profit columns: {missing}")
    result = sales_costs.copy()
    for column in required - {"Market", "Technology"}:
        result[column] = pd.to_numeric(result[column], errors="raise")
    if (result["SalesVehicles"] < 0.0).any():
        raise ValueError("SalesVehicles cannot be negative")
    government_subsidy = result[
        [
            "AdditionalSubsidy_CNY",
            "CentralSubsidy_CNY",
            "LocalSubsidy_CNY",
        ]
    ].sum(axis=1)
    result["ManufacturerMargin_CNY_per_vehicle"] = (
        result["ConsumerPrice_CNY"]
        - result["PurchaseTax_CNY"]
        - result["Insurance_CNY"]
        + government_subsidy
        - result["ProductionCost_CNY"]
    )
    result["ManufacturerProfit_CNY"] = (
        result["SalesVehicles"] * result["ManufacturerMargin_CNY_per_vehicle"]
    )
    return result, float(result["ManufacturerProfit_CNY"].sum())
