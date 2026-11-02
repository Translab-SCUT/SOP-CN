

from __future__ import annotations


def Constant_Private_Owned_Vehicle(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15, x16, x17, x18, x19, x20, x21, x22, x23):
    idx = np.searchsorted(x2, Year)  
    idx = np.clip(idx, 0, len(x2) - 1)
    
    equation_results = np.zeros(24, dtype=float)
    
    equation_results[:2] = x1[idx]
    equation_results[2] = x3[idx]
    equation_results[3] = x4[idx]
    equation_results[4] = x5[idx]
    equation_results[5] = x6[idx]
    equation_results[6] = x20[idx]
    equation_results[7] = x21[idx]
    equation_results[8] = x7[idx]
    equation_results[9] = x8[idx]
    equation_results[10] = x9[idx]
    equation_results[11] = x10[idx]
    equation_results[12:14] = x11[idx]
    equation_results[14] = x12[idx]
    equation_results[15] = x13[idx]
    equation_results[16] = x14[idx]
    equation_results[17] = x15[idx]
    equation_results[18] = x22[idx]
    equation_results[19] = x23[idx]
    equation_results[20] = x16[idx]
    equation_results[21] = x17[idx]
    equation_results[22] = x18[idx]
    equation_results[23] = x19[idx]

    return equation_results


def Constant_Non_Private_Vehicle(x1, x2, x3, x4, x5, x6, x7, x8, x9, x10, x11, x12, x13, x14, x15, x16, x17, x18, x19, x20, x21, x22, x23):
    idx = np.searchsorted(x2, Year)  
    idx = np.clip(idx, 0, len(x2) - 1)
    
    equation_results = np.zeros(24, dtype=float)
    
    equation_results[:2] = x1[idx]
    equation_results[2] = x3[idx]
    equation_results[3] = x4[idx]
    equation_results[4] = x5[idx]
    equation_results[5] = x6[idx]
    equation_results[6] = x20[idx]
    equation_results[7] = x21[idx]
    equation_results[8] = x7[idx]
    equation_results[9] = x8[idx]
    equation_results[10] = x9[idx]
    equation_results[11] = x10[idx]
    
    equation_results[12:14] = x11[idx]
    equation_results[14] = x12[idx]
    equation_results[15] = x13[idx]
    equation_results[16] = x14[idx]
    equation_results[17] = x15[idx]
    equation_results[18] = x22[idx]
    equation_results[19] = x23[idx]
    equation_results[20] = x16[idx]
    equation_results[21] = x17[idx]
    equation_results[22] = x18[idx]
    equation_results[23] = x19[idx]

    return equation_results


def _build_sales_model_panel_for_province():
    _capture_current_sales_state()
    if not _sales_state_has_calibration_years():
        raise ValueError(
            f"Incomplete 2021-2025 in-run sales state for "
            f"{PROVINCE_NAME}: {SALES_STATE_PATH}"
        )
    base_gdp = _gdp_for_year(SALES_MODEL_NORMALIZATION_BASE_YEAR)
    base_population = _population_persons_for_year(SALES_MODEL_NORMALIZATION_BASE_YEAR)
    base_pco = _weighted_pco_excluding_constant(SALES_MODEL_NORMALIZATION_BASE_YEAR)[
        "PCO excluding Constant (CNY/vehicle)"
    ]

    rows = []
    for year in SALES_MODEL_CALIBRATION_YEARS:
        population_persons = _population_persons_for_year(year)
        observed_sales = _historical_total_sales_vehicles(year)
        pco_info = _weighted_pco_excluding_constant(year)
        pbuy = observed_sales / population_persons
        current_gdp = _gdp_for_year(year)
        current_pco = pco_info["PCO excluding Constant (CNY/vehicle)"]
        gdp_norm = current_gdp / base_gdp
        pco_norm = current_pco / base_pco
        pco_norm_div_gdp_norm = pco_norm / gdp_norm
        observed_logit = _sales_model_logit(pbuy)
        unanchored_without_alpha = (
            SALES_MODEL_BETA_PCO_NORM_OVER_GDP_NORM
            * pco_norm_div_gdp_norm
        )
        rows.append(
            {
                "Year": int(year),
                "Observed total sales (vehicles)": observed_sales,
                "Population (persons)": population_persons,
                "Population (10,000 persons)": population_persons / 10000.0,
                "GDP (100 million CNY)": current_gdp,
                "PCO excluding Constant (CNY/vehicle)": current_pco,
                "Observed total Pbuy (vehicles/person/year)": pbuy,
                "Observed logit Pbuy": observed_logit,
                "GDP normalized": gdp_norm,
                "PCO normalized": pco_norm,
                "PCO_norm_div_GDP_norm": pco_norm_div_gdp_norm,
                "Unanchored utility without alpha": unanchored_without_alpha,
                **pco_info,
            }
        )

    panel = pd.DataFrame(rows)
    alpha_i = float(
        (
            panel["Observed logit Pbuy"]
            - panel["Unanchored utility without alpha"]
        ).mean()
    )
    panel["alpha_i"] = alpha_i
    panel["Unanchored binary-logit utility U_buy"] = (
        alpha_i + panel["Unanchored utility without alpha"]
    )
    anchor_row = panel.loc[
        panel["Year"] == SALES_MODEL_ANCHOR_YEAR
    ].iloc[0]
    anchor_adjustment = float(
        anchor_row["Observed logit Pbuy"]
        - anchor_row["Unanchored binary-logit utility U_buy"]
    )
    panel["Anchor adjustment (logit)"] = anchor_adjustment
    panel["Anchored binary-logit utility U_buy"] = (
        panel["Unanchored binary-logit utility U_buy"]
        + anchor_adjustment
    )
    panel["Anchored fitted Pbuy (vehicles/person/year)"] = panel[
        "Anchored binary-logit utility U_buy"
    ].map(_sales_model_logistic)
    panel["Anchored fitted total sales (vehicles)"] = (
        panel["Population (persons)"]
        * panel["Anchored fitted Pbuy (vehicles/person/year)"]
    )
    return panel


def _set_frozen_constants(market, constant_vector):
    constant_vector = np.asarray(constant_vector, dtype=float)
    if constant_vector.shape != (24,) or not np.isfinite(constant_vector).all():
        raise ValueError(
            f"Invalid {market} constant-freeze vector: "
            f"shape={constant_vector.shape}"
        )
    dataframe = _constant_freeze_market_dataframe(market)
    dataframe.loc[:23, "Constant"] = constant_vector


def _apply_existing_constant_freezes():
    
    if ETHANOL_TARGET_2060 > 0:
        if "_SOP_E0_CONSTANTS_BY_YEAR" not in globals():
            raise RuntimeError("Ethanol scenarios require E0 constants; run the 31-province scenario runner first.")
        for market in ("Personal", "Fleet"):
            frame = _constant_freeze_market_dataframe(market)
            keys = frame.loc[:23, ["Makes & Models", "Vehicle Product"]].astype(str).values.tolist()
            if keys != _SOP_E0_CONSTANT_KEYS[market]:
                raise ValueError(f"E0 Constant vehicle ordering mismatch: {market}")
            _set_frozen_constants(market, _SOP_E0_CONSTANTS_BY_YEAR[market][int(Year)])
        _reset_constant_freeze_dependent_caches()
        return ["Personal", "Fleet"]
    state = _load_sales_state()
    freeze_state = state.get("constant_freeze", {})
    applied = []
    
    for market in ("Personal",):
        record = freeze_state.get(market)
        if not record or not record.get("active", False):
            continue
        active_from_year = int(record["active_from_year"])
        if int(Year) < active_from_year:
            continue
        _set_frozen_constants(market, record["constant_vector"])
        applied.append(market)
        print(
            f"[CONSTANT FREEZE] {PROVINCE_NAME} {Year} {market}: "
            f"using constants frozen from {record['source_year']} onward."
        )
    if applied:
        _reset_constant_freeze_dependent_caches()
    return applied


def _activate_new_constant_freezes():
    if ETHANOL_TARGET_2060 > 0:
        return []
    year = int(Year)
    if year in ICEV_HEV_CONSTANT_FREEZE_EXCLUDED_TRIGGER_YEARS:
        return []

    previous_year = year - 1
    state = _load_sales_state()
    freeze_state = state.setdefault("constant_freeze", {})
    triggered = []

    
    for market in ("Personal",):
        existing = freeze_state.get(market)
        if existing and existing.get("active", False):
            continue

        previous_share_vector = _sales_state_metric_vector(
            market,
            "Market Share",
            previous_year,
        )
        previous_constant_vector = _sales_state_metric_vector(
            market,
            "Constant",
            previous_year,
        )
        previous_share = _constant_freeze_share(
            market,
            previous_share_vector,
        )
        current_share = _constant_freeze_share(market)

        if current_share <= previous_share + ICEV_HEV_SHARE_TOLERANCE:
            continue

        freeze_state[market] = {
            "active": True,
            "active_from_year": year,
            "source_year": previous_year,
            "constant_vector": previous_constant_vector.tolist(),
            "trigger_previous_ICEV_HEV_share": previous_share,
            "trigger_current_ICEV_HEV_share_before_freeze": current_share,
        }
        _set_frozen_constants(market, previous_constant_vector)
        triggered.append(market)
        print(
            f"[CONSTANT FREEZE] {PROVINCE_NAME} {year} {market}: "
            f"ICEV+HEV share {current_share:.12f} > "
            f"{previous_share:.12f}; constants frozen at {previous_year} "
            "values for this and all future years."
        )

    if triggered:
        state["constant_freeze"] = freeze_state
        _save_sales_state(state)
        _reset_constant_freeze_dependent_caches()
    return triggered
