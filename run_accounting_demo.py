"""Run the public cohort-energy-CO2 accounting demo with illustrative data."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from sopcn_public.accounting import run_accounting_pipeline

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA_DIR = ROOT / "data/example"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DEFAULT_DATA_DIR)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    sales = pd.read_csv(args.data_dir / "illustrative_sales.csv")
    survival = pd.read_csv(args.data_dir / "illustrative_survival.csv")
    assumptions = pd.read_csv(args.data_dir / "illustrative_technology.csv")
    factors = pd.read_csv(args.data_dir / "illustrative_emission_factors.csv")

    result = run_accounting_pipeline(
        sales=sales,
        survival=survival,
        assumptions=assumptions,
        emission_factors=factors,
        start_year=2025,
        end_year=2030,
    )
    summary = (
        result.cohort_emissions.groupby(["Year", "Technology"], as_index=False)
        .agg(
            StockVehicles=("StockVehicles", "sum"),
            Fuel_L=("Fuel_L", "sum"),
            Electricity_kWh=("Electricity_kWh", "sum"),
            Fuel_CO2_kg=("Fuel_CO2_kg", "sum"),
            Electricity_CO2_kg=("Electricity_CO2_kg", "sum"),
            Total_CO2_kg=("Total_CO2_kg", "sum"),
        )
        .sort_values(["Year", "Technology"])
    )

    print(summary.to_string(index=False, float_format=lambda value: f"{value:,.2f}"))
    if args.output is not None:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        summary.to_csv(args.output, index=False)
        print(f"Saved illustrative accounting output: {args.output}")


if __name__ == "__main__":
    main()

