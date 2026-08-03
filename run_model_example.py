"""Run the SOP-CN model components with synthetic example inputs."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from sopcn_public.accounting import (
    calculate_attributable_mortality,
    calculate_pollutant_emissions,
    derive_power_pollutant_factors,
    run_accounting_pipeline,
    scale_fuel_pollutant_factors,
)
from sopcn_public.economics import (
    GAConfig,
    calculate_annual_manufacturer_profit,
    calculate_consumer_costs,
    calculate_ownership_cost,
    optimize_internal_subsidy,
)
from sopcn_public.sales import fit_scheme3_fixed_effects, predict_scheme3_sales

ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data/example"


def project_sales() -> pd.DataFrame:
    panel = pd.read_csv(DATA_DIR / "illustrative_sales_projection.csv")
    observed = panel.dropna(subset=["ObservedSales"])
    fit = fit_scheme3_fixed_effects(observed, calibration_years=range(2021, 2026))
    result = predict_scheme3_sales(
        panel,
        fit,
        observed_through_year=2025,
    )
    print("\nScheme 3 sales projection")
    print(f"Example fitted beta: {fit.beta:.6f}")
    print(
        result.loc[
            result["Year"].isin([2025, 2030]),
            ["Province", "Year", "PurchaseProbability", "PredictedSales"],
        ].to_string(index=False, float_format=lambda value: f"{value:,.4f}")
    )
    return result


def optimize_subsidies() -> None:
    raw_costs = pd.read_csv(DATA_DIR / "illustrative_costs.csv")
    total_sales = float(raw_costs["SalesVehicles"].sum())

    def annual_profit(candidate: np.ndarray) -> float:
        trial = raw_costs.copy()
        trial["InternalSubsidy_CNY"] = candidate
        trial = calculate_ownership_cost(calculate_consumer_costs(trial))
        utility = -trial["OwnershipTotalCost_CNY"].to_numpy(dtype=float) / 30_000.0
        exp_utility = np.exp(utility - utility.max())
        trial["SalesVehicles"] = total_sales * exp_utility / exp_utility.sum()
        _, profit = calculate_annual_manufacturer_profit(trial)
        return profit

    result = optimize_internal_subsidy(
        annual_profit,
        number_of_genes=len(raw_costs),
        seed_key="SOP-CN-example|Province-A|2030",
        config=GAConfig(
            population_size=30,
            maximum_generations=30,
            maximum_stalled_generations=5,
        ),
    )
    print("\nAnnual internal-subsidy GA")
    print(f"Stable seed: {result.seed}")
    print(f"Generations: {result.generations}")
    print(f"Subsidies (CNY/vehicle): {result.subsidy.tolist()}")
    print(f"Annual manufacturer profit (CNY): {result.objective_cny:,.0f}")


def account_for_health() -> None:
    accounting = run_accounting_pipeline(
        sales=pd.read_csv(DATA_DIR / "illustrative_sales.csv"),
        survival=pd.read_csv(DATA_DIR / "illustrative_survival.csv"),
        assumptions=pd.read_csv(DATA_DIR / "illustrative_technology.csv"),
        emission_factors=pd.read_csv(DATA_DIR / "illustrative_emission_factors.csv"),
        start_year=2025,
        end_year=2030,
    )
    energy_2025 = accounting.cohort_energy.loc[
        accounting.cohort_energy["Year"] == 2025
    ].copy()
    reference = pd.read_csv(DATA_DIR / "illustrative_pollutant_factors.csv")
    fuel_factors = scale_fuel_pollutant_factors(
        reference,
        fuel_co2_kg_per_l=2.75,
        reference_fuel_co2_kg_per_l=2.75,
    )
    power_factors = derive_power_pollutant_factors(
        reference,
        electricity_co2_kg_per_kwh=0.55,
    )
    pathway_factors = fuel_factors.merge(
        power_factors[["Pollutant", "Power_WTP_mg_per_kWh"]],
        on="Pollutant",
        validate="one_to_one",
    )
    pollutant_emissions = calculate_pollutant_emissions(
        energy_2025,
        pathway_factors,
        non_exhaust_pm25_g_per_km_at_reference_mass=0.01,
    )
    mortality = calculate_attributable_mortality(
        pollutant_emissions,
        pd.read_csv(DATA_DIR / "illustrative_mortality_factors.csv"),
        pd.read_csv(DATA_DIR / "illustrative_population.csv").query("Year == 2025"),
    )
    print("\nHealth-relevant emissions by pathway in 2025 (example tonnes)")
    print(
        pollutant_emissions.groupby(["Scope", "Pollutant"], as_index=False)[
            "Emission_t"
        ]
        .sum()
        .to_string(index=False, float_format=lambda value: f"{value:,.6f}")
    )
    print("\nAttributable-mortality total")
    print(mortality.totals.to_string(index=False, float_format=lambda value: f"{value:,.8f}"))


def main() -> None:
    project_sales()
    optimize_subsidies()
    account_for_health()


if __name__ == "__main__":
    main()
