"""Selected province-generic SOP-CN functions; runtime inputs are supplied by the parent model."""

from __future__ import annotations


def _sales_model_logit(probability):
    probability = float(np.clip(probability, 1e-12, 1.0 - 1e-12))
    return float(np.log(probability / (1.0 - probability)))


def _sales_model_logistic(utility):
    utility = float(np.clip(utility, -700.0, 700.0))
    return float(1.0 / (1.0 + np.exp(-utility)))


def _predict_province_sales_anchor2025(year):
    year = int(year)
    if SOP_SALES_CALIBRATION_PREPASS:
        return _sales_prepass_result(year)
    calibration_panel = _build_sales_model_panel_for_province()
    alpha_i = float(calibration_panel["alpha_i"].iloc[0])
    anchor_adjustment = float(
        calibration_panel["Anchor adjustment (logit)"].iloc[0]
    )
    base_gdp = _gdp_for_year(SALES_MODEL_NORMALIZATION_BASE_YEAR)
    base_population = _population_persons_for_year(SALES_MODEL_NORMALIZATION_BASE_YEAR)
    base_pco = float(
        calibration_panel.loc[
            calibration_panel["Year"] == SALES_MODEL_NORMALIZATION_BASE_YEAR,
            "PCO excluding Constant (CNY/vehicle)",
        ].iloc[0]
    )

    population_persons = _population_persons_for_year(year)
    current_gdp = _gdp_for_year(year)
    current_pco_info = _weighted_pco_excluding_constant(year)
    current_pco = current_pco_info["PCO excluding Constant (CNY/vehicle)"]
    gdp_norm = current_gdp / base_gdp
    pco_norm = current_pco / base_pco
    pco_norm_div_gdp_norm = pco_norm / gdp_norm
    unanchored_utility = (
        alpha_i
        + SALES_MODEL_BETA_PCO_NORM_OVER_GDP_NORM
        * pco_norm_div_gdp_norm
    )
    anchored_utility = unanchored_utility + anchor_adjustment
    pbuy = _sales_model_logistic(anchored_utility)
    total_sales = population_persons * pbuy

    observed_sales = np.nan
    if year in SALES_MODEL_CALIBRATION_YEARS:
        observed_sales = _historical_total_sales_vehicles(year)
        total_sales = float(observed_sales)
        pbuy = total_sales / population_persons
        anchored_utility = _sales_model_logit(pbuy)

    result = {
        "Model": SALES_MODEL_NAME,
        "Year": year,
        "Predicted total sales (vehicles)": float(total_sales),
        "Predicted total Pbuy (vehicles/person/year)": float(pbuy),
        "Unanchored binary-logit utility U_buy": float(unanchored_utility),
        "Binary-logit utility U_buy": float(anchored_utility),
        "Anchor adjustment (logit)": anchor_adjustment,
        "alpha_i": alpha_i,
        "beta_PCOnorm_over_GDPnorm": (
            SALES_MODEL_BETA_PCO_NORM_OVER_GDP_NORM
        ),
        "PCO_norm_div_GDP_norm": float(pco_norm_div_gdp_norm),
        "GDP (100 million CNY)": float(current_gdp),
        "GDP base 2025 (100 million CNY)": float(base_gdp),
        "GDP normalized": float(gdp_norm),
        "Population (persons)": float(population_persons),
        "Population (10,000 persons)": float(population_persons / 10000.0),
        "Population base 2025 (persons)": float(base_population),
        "Population normalized": float(population_persons / base_population),
        "PCO base 2025 excluding Constant (CNY/vehicle)": float(base_pco),
        "PCO normalized": float(pco_norm),
        "Observed total sales (vehicles)": float(observed_sales)
        if np.isfinite(observed_sales)
        else np.nan,
        "Sales source": (
            "Observed provincial total sales from source workbooks for "
            "2021-2025; Scheme 3 projection from 2026"
        ),
        "Calibration years": ",".join(map(str, SALES_MODEL_CALIBRATION_YEARS)),
        **current_pco_info,
    }
    return result, calibration_panel


def _private_owned_sales_ratio(year):
    year = int(year)
    if year not in private_owned_ratio:
        raise ValueError(
            f"private_owned_ratio does not cover simulation year {year}"
        )
    ratio = float(private_owned_ratio[year])
    if not 0.0 <= ratio <= 1.0:
        raise ValueError(f"Invalid private-owned ratio for {year}: {ratio}")
    return ratio


def _set_sales_from_market_share(market_df, total_sales_1000):
    index = market_df.loc[:23].index
    shares = pd.to_numeric(
        market_df.loc[index, "Market share"],
        errors="coerce",
    ).fillna(0.0).clip(lower=0.0)
    share_sum = float(shares.sum())
    if share_sum <= 0:
        raise ValueError(f"Market shares sum to zero for {PROVINCE_NAME}")
    normalized_shares = shares / share_sum
    market_df.loc[index, "Sales (1000)"] = (
        normalized_shares.to_numpy(dtype=float) * float(total_sales_1000)
    )
