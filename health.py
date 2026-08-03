"""Health-relevant pollutant and attributable-mortality accounting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

import numpy as np
import pandas as pd

POLLUTANTS = ("PM2.5", "NOx", "SO2", "VOC")
SCOPE_STACK = {
    "Fuel_WTP": "Low-stack",
    "TTW": "Ground",
    "Non_Exhaust": "Ground",
    "Power_WTP": "High-stack",
}


def normalize_pollutant(value: object) -> str:
    """Normalize common pollutant labels to the public output vocabulary."""

    compact = (
        str(value)
        .strip()
        .upper()
        .replace(" ", "")
        .replace("_", "")
        .replace("-", "")
        .replace(".", "")
        .replace("\u2082", "2")
        .replace("\u2085", "5")
    )
    aliases = {
        "PM25": "PM2.5",
        "NOX": "NOx",
        "NO": "NOx",
        "SO2": "SO2",
        "VOC": "VOC",
        "NMVOC": "VOC",
        "NMVOCS": "VOC",
    }
    return aliases.get(compact, str(value).strip())


def scale_fuel_pollutant_factors(
    reference_factors: pd.DataFrame,
    fuel_co2_kg_per_l: float,
    reference_fuel_co2_kg_per_l: float,
    fuel_consumption_blend_factor: float = 1.0,
) -> pd.DataFrame:
    """Scale fuel WTP and TTW factors with the selected fuel-CO2 scenario.

    Fuel WTP factors in g/L use the direct CO2-per-litre ratio. TTW factors in
    g/km additionally include the blend energy penalty because they do not
    multiply the already adjusted fuel volume.
    """

    required = {
        "Pollutant",
        "Fuel_WTP_reference_g_per_L",
        "TTW_reference_g_per_km",
    }
    missing = sorted(required - set(reference_factors.columns))
    if missing:
        raise ValueError(f"Missing reference pollutant-factor columns: {missing}")
    if reference_fuel_co2_kg_per_l <= 0.0 or fuel_consumption_blend_factor <= 0.0:
        raise ValueError("Reference fuel CO2 and blend factor must be positive")
    if fuel_co2_kg_per_l < 0.0:
        raise ValueError("Fuel CO2 factor cannot be negative")

    numeric_columns = [
        "Fuel_WTP_reference_g_per_L",
        "TTW_reference_g_per_km",
    ]
    result = reference_factors.loc[:, ["Pollutant"] + numeric_columns].copy()
    result["Pollutant"] = result["Pollutant"].map(normalize_pollutant)
    for column in numeric_columns:
        result[column] = pd.to_numeric(result[column], errors="raise")
    if (result[numeric_columns] < 0.0).any(axis=None):
        raise ValueError("Pollutant factors cannot be negative")
    per_litre_ratio = float(fuel_co2_kg_per_l) / float(
        reference_fuel_co2_kg_per_l
    )
    result["Fuel_WTP_g_per_L"] = (
        result["Fuel_WTP_reference_g_per_L"] * per_litre_ratio
    )
    result["TTW_g_per_km"] = (
        result["TTW_reference_g_per_km"]
        * per_litre_ratio
        * float(fuel_consumption_blend_factor)
    )
    result["FuelCO2ScalingRatio_per_L"] = per_litre_ratio
    result["FuelCO2ScalingRatio_per_km"] = (
        per_litre_ratio * float(fuel_consumption_blend_factor)
    )
    return result


def derive_power_pollutant_factors(
    pollutant_ratios: pd.DataFrame,
    electricity_co2_kg_per_kwh: float,
) -> pd.DataFrame:
    """Derive power WTP factors as grid CO2 times pollutant/CO2 ratio."""

    required = {"Pollutant", "Ratio_mg_per_gCO2"}
    missing = sorted(required - set(pollutant_ratios.columns))
    if missing:
        raise ValueError(f"Missing power-pollutant ratio columns: {missing}")
    if electricity_co2_kg_per_kwh < 0.0:
        raise ValueError("Electricity CO2 factor cannot be negative")
    result = pollutant_ratios.loc[:, ["Pollutant", "Ratio_mg_per_gCO2"]].copy()
    result["Pollutant"] = result["Pollutant"].map(normalize_pollutant)
    result["Ratio_mg_per_gCO2"] = pd.to_numeric(
        result["Ratio_mg_per_gCO2"], errors="raise"
    )
    if (result["Ratio_mg_per_gCO2"] < 0.0).any():
        raise ValueError("Power-pollutant ratios cannot be negative")
    result["Power_WTP_mg_per_kWh"] = (
        float(electricity_co2_kg_per_kwh)
        * 1000.0
        * result["Ratio_mg_per_gCO2"]
    )
    return result


def calculate_pollutant_emissions(
    cohort_energy: pd.DataFrame,
    pathway_factors: pd.DataFrame,
    non_exhaust_pm25_g_per_km_at_reference_mass: float,
    reference_mass_kg: float = 1500.0,
) -> pd.DataFrame:
    """Calculate four health-emission pathways for every surviving cohort."""

    energy_required = {
        "Market",
        "Technology",
        "SalesYear",
        "Year",
        "StockVehicles",
        "VehicleMass_kg",
        "Fuel_L",
        "Electricity_kWh",
        "TotalVKT_km",
        "LiquidFuelVKT_km",
    }
    factor_required = {
        "Pollutant",
        "Fuel_WTP_g_per_L",
        "TTW_g_per_km",
        "Power_WTP_mg_per_kWh",
    }
    missing_energy = sorted(energy_required - set(cohort_energy.columns))
    missing_factors = sorted(factor_required - set(pathway_factors.columns))
    if missing_energy or missing_factors:
        raise ValueError(
            f"Missing energy columns={missing_energy}; "
            f"missing pathway-factor columns={missing_factors}"
        )
    if reference_mass_kg <= 0.0 or non_exhaust_pm25_g_per_km_at_reference_mass < 0.0:
        raise ValueError("Reference mass must be positive and non-exhaust factor nonnegative")

    factors = pathway_factors.loc[:, list(factor_required)].copy()
    factors["Pollutant"] = factors["Pollutant"].map(normalize_pollutant)
    if factors["Pollutant"].duplicated().any():
        raise ValueError("Pathway factors must contain one row per pollutant")
    for column in factor_required - {"Pollutant"}:
        factors[column] = pd.to_numeric(factors[column], errors="raise")
    if (factors[list(factor_required - {"Pollutant"})] < 0.0).any(axis=None):
        raise ValueError("Pathway factors cannot be negative")

    records: list[dict[str, object]] = []
    identity_columns = [
        column
        for column in ("Province", "Market", "Technology", "SalesYear", "Year")
        if column in cohort_energy.columns
    ]
    for energy_row in cohort_energy.itertuples(index=False):
        energy = energy_row._asdict()
        identity = {column: energy[column] for column in identity_columns}
        for factor_row in factors.itertuples(index=False):
            pollutant = normalize_pollutant(factor_row.Pollutant)
            emissions = {
                "Fuel_WTP": energy["Fuel_L"] * factor_row.Fuel_WTP_g_per_L / 1e6,
                "TTW": energy["LiquidFuelVKT_km"] * factor_row.TTW_g_per_km / 1e6,
                "Power_WTP": (
                    energy["Electricity_kWh"]
                    * factor_row.Power_WTP_mg_per_kWh
                    / 1e9
                ),
                "Non_Exhaust": (
                    energy["TotalVKT_km"]
                    * non_exhaust_pm25_g_per_km_at_reference_mass
                    * energy["VehicleMass_kg"]
                    / reference_mass_kg
                    / 1e6
                    if pollutant == "PM2.5"
                    else 0.0
                ),
            }
            for scope, emission_t in emissions.items():
                records.append(
                    {
                        **identity,
                        "Scope": scope,
                        "Stack": SCOPE_STACK[scope],
                        "Pollutant": pollutant,
                        "Emission_t": float(emission_t),
                    }
                )
    return pd.DataFrame.from_records(records)


@dataclass(frozen=True)
class MortalityResult:
    """Unique mortality detail plus one total per geography-year."""

    detail: pd.DataFrame
    totals: pd.DataFrame


def calculate_attributable_mortality(
    pollutant_emissions: pd.DataFrame,
    mortality_factors: pd.DataFrame,
    population: pd.DataFrame,
) -> MortalityResult:
    """Convert source-specific emissions to attributable deaths.

    The detail table contains only original markets and each scope-pollutant
    contribution once. The totals table is separate, preventing repeated sums
    across scope, pollutant and derived market aggregations.
    """

    emission_required = {"Year", "Market", "Scope", "Stack", "Pollutant", "Emission_t"}
    factor_required = {"Pollutant", "Stack", "Deaths_per_t"}
    population_required = {"Year", "PopulationPersons"}
    missing_emissions = sorted(emission_required - set(pollutant_emissions.columns))
    missing_factors = sorted(factor_required - set(mortality_factors.columns))
    missing_population = sorted(population_required - set(population.columns))
    if missing_emissions or missing_factors or missing_population:
        raise ValueError(
            f"Missing emission columns={missing_emissions}; factor columns="
            f"{missing_factors}; population columns={missing_population}"
        )
    if pollutant_emissions["Market"].astype(str).eq("Total").any():
        raise ValueError("Mortality detail must not include a derived Total market")

    geography = ["Province"] if "Province" in pollutant_emissions.columns else []
    group_columns = geography + ["Year", "Market", "Scope", "Stack", "Pollutant"]
    emissions = (
        pollutant_emissions.groupby(group_columns, as_index=False)["Emission_t"].sum()
    )
    emissions["Pollutant"] = emissions["Pollutant"].map(normalize_pollutant)

    factors = mortality_factors.loc[:, list(factor_required)].copy()
    factors["Pollutant"] = factors["Pollutant"].map(normalize_pollutant)
    factors["Deaths_per_t"] = pd.to_numeric(factors["Deaths_per_t"], errors="raise")
    if factors.duplicated(["Pollutant", "Stack"]).any():
        raise ValueError("Mortality factors must be unique by pollutant and stack")
    if (factors["Deaths_per_t"] < 0.0).any():
        raise ValueError("Mortality factors cannot be negative")
    detail = emissions.merge(
        factors,
        on=["Pollutant", "Stack"],
        how="left",
        validate="many_to_one",
        indicator=True,
    )
    missing = detail.loc[detail["_merge"] != "both", ["Pollutant", "Stack"]]
    if not missing.empty:
        raise ValueError(f"Missing mortality factors:\n{missing.drop_duplicates()}")
    detail = detail.drop(columns="_merge")
    detail["Deaths"] = detail["Emission_t"] * detail["Deaths_per_t"]
    detail["Aggregation"] = "Scope-pollutant"

    population_keys = geography + ["Year"]
    population_data = population.copy()
    missing_geo = sorted(set(geography) - set(population_data.columns))
    if missing_geo:
        raise ValueError(f"Population table is missing geography columns: {missing_geo}")
    population_data["PopulationPersons"] = pd.to_numeric(
        population_data["PopulationPersons"], errors="raise"
    )
    if (population_data["PopulationPersons"] <= 0.0).any():
        raise ValueError("PopulationPersons must be positive")
    if population_data.duplicated(population_keys).any():
        raise ValueError("Population must be unique by geography and year")

    totals = detail.groupby(population_keys, as_index=False)["Deaths"].sum()
    totals = totals.merge(
        population_data.loc[:, population_keys + ["PopulationPersons"]],
        on=population_keys,
        how="left",
        validate="one_to_one",
    )
    if totals["PopulationPersons"].isna().any():
        raise ValueError("Missing population for at least one mortality total")
    totals["MortalityRate_per_100000"] = (
        totals["Deaths"] / totals["PopulationPersons"] * 100_000.0
    )
    totals["Market"] = "Total"
    totals["Aggregation"] = "Market total"
    return MortalityResult(detail=detail, totals=totals)
