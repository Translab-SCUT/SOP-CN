"""End-to-end public accounting pipeline using already supplied sales."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .cohort import build_cohort_stock
from .emissions import calculate_co2_emissions
from .energy import calculate_cohort_energy


@dataclass(frozen=True)
class AccountingResult:
    """Intermediate tables retained for transparent public inspection."""

    cohort_stock: pd.DataFrame
    cohort_energy: pd.DataFrame
    cohort_emissions: pd.DataFrame


def run_accounting_pipeline(
    sales: pd.DataFrame,
    survival: pd.DataFrame,
    assumptions: pd.DataFrame,
    emission_factors: pd.DataFrame,
    start_year: int,
    end_year: int,
) -> AccountingResult:
    """Run public stock, energy and source-specific CO2 accounting.

    New-vehicle sales are explicit inputs to this accounting layer. They may be
    supplied directly or generated with the public ``sopcn_public.sales`` API.
    """

    cohort_stock = build_cohort_stock(sales, survival, start_year, end_year)
    cohort_energy = calculate_cohort_energy(cohort_stock, assumptions)
    cohort_emissions = calculate_co2_emissions(cohort_energy, emission_factors)
    return AccountingResult(
        cohort_stock=cohort_stock,
        cohort_energy=cohort_energy,
        cohort_emissions=cohort_emissions,
    )
