"""Transparent consumer-cost and subsidy equations used by SOP-CN."""

from __future__ import annotations

import pandas as pd

SUBSIDY_COLUMNS = (
    "AdditionalSubsidy_CNY",
    "CentralSubsidy_CNY",
    "LocalSubsidy_CNY",
    "InternalSubsidy_CNY",
)
OWNERSHIP_COMPONENTS = (
    "ConsumerPrice_CNY",
    "FuelCost_CNY",
    "ElectricityCost_CNY",
    "InconvenienceCost_CNY",
    "RangeAnxietyCost_CNY",
    "PurchasePrivilege_CNY",
    "Constant_CNY",
)


def calculate_consumer_costs(cost_table: pd.DataFrame) -> pd.DataFrame:
    """Apply all four subsidy channels to pre-subsidy consumer price.

    ``PreSubsidyPrice_CNY`` excludes purchase tax and insurance. The returned
    consumer price includes both charges after subsidies are deducted.
    """

    required = {
        "PreSubsidyPrice_CNY",
        "PurchaseTax_CNY",
        "Insurance_CNY",
        *SUBSIDY_COLUMNS,
    }
    missing = sorted(required - set(cost_table.columns))
    if missing:
        raise ValueError(f"Missing consumer-cost columns: {missing}")
    result = cost_table.copy()
    numeric = ["PreSubsidyPrice_CNY", "PurchaseTax_CNY", "Insurance_CNY"] + list(
        SUBSIDY_COLUMNS
    )
    for column in numeric:
        result[column] = pd.to_numeric(result[column], errors="raise")
    if (result[numeric] < 0.0).any(axis=None):
        raise ValueError("Prices, charges and subsidies cannot be negative")
    result["GovernmentSubsidy_CNY"] = result[
        [
            "AdditionalSubsidy_CNY",
            "CentralSubsidy_CNY",
            "LocalSubsidy_CNY",
        ]
    ].sum(axis=1)
    result["ConsumerPrice_CNY"] = (
        result["PreSubsidyPrice_CNY"]
        - result[list(SUBSIDY_COLUMNS)].sum(axis=1)
        + result["PurchaseTax_CNY"]
        + result["Insurance_CNY"]
    )
    return result


def calculate_ownership_cost(cost_table: pd.DataFrame) -> pd.DataFrame:
    """Sum consumer price and non-price ownership-cost components."""

    missing = [column for column in OWNERSHIP_COMPONENTS if column not in cost_table]
    if missing:
        raise ValueError(f"Missing ownership-cost columns: {missing}")
    result = cost_table.copy()
    for column in OWNERSHIP_COMPONENTS:
        result[column] = pd.to_numeric(result[column], errors="raise")
    result["OwnershipTotalCost_CNY"] = result[list(OWNERSHIP_COMPONENTS)].sum(
        axis=1
    )
    result["PCOExcludingConstant"] = (
        result["OwnershipTotalCost_CNY"] - result["Constant_CNY"]
    )
    return result
