"""Source-specific CO2 accounting for public demonstration inputs."""

from __future__ import annotations

import pandas as pd

FACTOR_COLUMNS = (
    "Year",
    "Fuel_kgCO2_per_L",
    "Electricity_kgCO2_per_kWh",
)


def calculate_co2_emissions(
    cohort_energy: pd.DataFrame,
    emission_factors: pd.DataFrame,
) -> pd.DataFrame:
    """Convert cohort fuel and electricity demand to source-specific CO2."""

    energy_required = {"Year", "Fuel_L", "Electricity_kWh"}
    missing_energy = sorted(energy_required - set(cohort_energy.columns))
    missing_factors = [
        column for column in FACTOR_COLUMNS if column not in emission_factors
    ]
    if missing_energy or missing_factors:
        raise ValueError(
            f"Missing energy columns={missing_energy}; "
            f"missing factor columns={missing_factors}"
        )

    factors = emission_factors.loc[:, FACTOR_COLUMNS].copy()
    for column in FACTOR_COLUMNS:
        factors[column] = pd.to_numeric(factors[column], errors="raise")
    factors["Year"] = factors["Year"].astype(int)
    if factors["Year"].duplicated().any():
        raise ValueError("Emission factors must contain one row per year")
    if (factors[list(FACTOR_COLUMNS[1:])] < 0).any(axis=None):
        raise ValueError("Emission factors cannot be negative")

    result = cohort_energy.merge(
        factors,
        on="Year",
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    missing_years = sorted(result.loc[result["_merge"] != "both", "Year"].unique())
    if missing_years:
        raise ValueError(f"Missing emission factors for years: {missing_years}")
    result = result.drop(columns="_merge")

    result["Fuel_CO2_kg"] = result["Fuel_L"] * result["Fuel_kgCO2_per_L"]
    result["Electricity_CO2_kg"] = (
        result["Electricity_kWh"] * result["Electricity_kgCO2_per_kWh"]
    )
    result["Total_CO2_kg"] = (
        result["Fuel_CO2_kg"] + result["Electricity_CO2_kg"]
    )
    return result

