"""Selected province-generic SOP-CN functions; runtime inputs are supplied by the parent model."""

from __future__ import annotations


def _initial_stock_age_from_column(column):
    if isinstance(column, (int, np.integer)):
        return int(column)
    if isinstance(column, (float, np.floating)) and float(column).is_integer():
        return int(column)
    text = str(column).strip()
    return int(text) if text.isdigit() else None


def _load_initial_stock_2026_matrix(sheet_name):
    if not INITIAL_STOCK_2026_PATH.exists():
        raise FileNotFoundError(
            f"Cannot find initial stock matrix: {INITIAL_STOCK_2026_PATH}"
        )

    raw = pd.read_excel(
        INITIAL_STOCK_2026_PATH,
        sheet_name=sheet_name,
        index_col=0,
    )
    raw.index = raw.index.map(lambda value: str(value).strip())

    age_columns = {}
    for column in raw.columns:
        age = _initial_stock_age_from_column(column)
        if age is not None:
            age_columns[age] = column

    ages = list(range(31))
    missing_vehicle_types = [
        vehicle_type
        for vehicle_type in VEHICLE_TYPES
        if vehicle_type not in raw.index
    ]
    missing_ages = [
        age for age in ages
        if age not in age_columns
    ]
    if missing_vehicle_types or missing_ages:
        raise ValueError(
            f"{INITIAL_STOCK_2026_PATH.name}::{sheet_name} is missing "
            f"vehicle types {missing_vehicle_types} or ages {missing_ages}."
        )

    matrix = raw.loc[
        list(VEHICLE_TYPES),
        [age_columns[age] for age in ages],
    ].apply(pd.to_numeric, errors="coerce")
    if matrix.isna().any().any():
        raise ValueError(
            f"{INITIAL_STOCK_2026_PATH.name}::{sheet_name} contains "
            "non-numeric stock values."
        )
    if (matrix < 0).any().any():
        raise ValueError(
            f"{INITIAL_STOCK_2026_PATH.name}::{sheet_name} contains "
            "negative stock values."
        )

    return (
        matrix.to_numpy(dtype=float)
        * INITIAL_STOCK_2026_UNIT_SCALE_TO_1000
    )


def _calculate_stock(
    year,
    is_private_owned_market=True,
    is_non_private_market=False,
    previous_stock_by_age=None,
    market_df=None,
    private_owned_sales_matrix=None,
    survival_data=None,
    vehicle_types=None,
    powertrain_map=None,
    initial_stock_data_private_owned=None,
    initial_stock_data_non_private=None,
    initial_stock_data=None,
):
    if survival_data is None:
        survival_data = UNIFIED_SURVIVAL_DATA
    (
        survival_ice,
        survival_bev,
        survival_phev,
        survival_fcev,
    ) = survival_data

    if (
        vehicle_types is None
        or powertrain_map is None
        or initial_stock_data_private_owned is None
        or initial_stock_data_non_private is None
    ):
        (
            vehicle_types,
            powertrain_map,
            initial_stock_data_private_owned,
            initial_stock_data_non_private,
            initial_stock_data,
        ) = _initialize_vehicle_data()

    ages = list(range(31))
    if is_private_owned_market and not is_non_private_market:
        initial_data = initial_stock_data_private_owned
    elif is_non_private_market and not is_private_owned_market:
        initial_data = initial_stock_data_non_private
    else:
        initial_data = initial_stock_data

    if previous_stock_by_age is None:
        stock_by_age = pd.DataFrame(
            initial_data,
            index=vehicle_types,
            columns=ages,
        )
    else:
        stock_by_age = previous_stock_by_age.copy()
        stock_by_age = stock_by_age.reindex(
            index=vehicle_types,
            columns=ages,
            fill_value=0.0,
        )

    if market_df is None or market_df.empty:
        return {vehicle_type: 0.0 for vehicle_type in vehicle_types}, stock_by_age

    market = market_df.copy()
    if "Year" in market.columns:
        market = market.loc[market["Year"] == int(year)].copy()

    required_columns = {"Makes & Models", "Vehicle Product", "Sales (1000)"}
    missing_columns = required_columns - set(market.columns)
    if missing_columns:
        raise ValueError(
            f"market_df is missing required columns: {missing_columns}"
        )

    def _vehicle_full_name(row):
        prefix = (
            "Sed-"
            if "Sedan" in str(row["Makes & Models"])
            else "SUV-"
        )
        return prefix + str(row["Vehicle Product"])

    market["Vehicle Full Name"] = market.apply(
        _vehicle_full_name,
        axis=1,
    )
    annual_sales = (
        market.groupby("Vehicle Full Name")["Sales (1000)"]
        .sum()
        .reindex(vehicle_types)
        .fillna(0.0)
    )

    survival_index = int(year) - 2021

    def _survival_array(powertrain):
        if powertrain == "ICE":
            matrix = survival_ice
        elif powertrain == "BEV":
            matrix = survival_bev
        elif powertrain == "PHEV":
            matrix = survival_phev
        else:
            matrix = survival_fcev
        index = min(max(survival_index, 0), len(matrix) - 1)
        return matrix[index]

    for age in range(30, 0, -1):
        for vehicle_type in vehicle_types:
            survival_rates = _survival_array(
                powertrain_map[vehicle_type]
            )
            denominator = survival_rates[age - 1]
            previous_value = stock_by_age.at[vehicle_type, age - 1]
            stock_by_age.at[vehicle_type, age] = (
                previous_value * survival_rates[age] / denominator
                if denominator > 0
                else 0.0
            )

    for vehicle_type in vehicle_types:
        survival_at_age_zero = _survival_array(
            powertrain_map[vehicle_type]
        )[0]
        stock_by_age.at[vehicle_type, 0] = (
            float(annual_sales[vehicle_type]) * survival_at_age_zero
        )

    return stock_by_age.sum(axis=1).to_dict(), stock_by_age


def _calculate_provincial_stock():
    (
        vehicle_types,
        powertrain_map,
        initial_private_owned,
        initial_non_private,
    ) = _scaled_2025_initial_stock()
    ages = list(range(31))

    
    if int(Year) < 2025:
        stock_df = _historical_stock(vehicle_types)
        return stock_df, {
            "stock": stock_df,
            "stock_by_age_private_owned": None,
            "stock_by_age_non_private": None,
        }

    if int(Year) == 2025:
        private_owned_by_age = pd.DataFrame(
            initial_private_owned,
            index=vehicle_types,
            columns=ages,
        )
        non_private_by_age = pd.DataFrame(
            initial_non_private,
            index=vehicle_types,
            columns=ages,
        )
    else:
        previous_private_owned_path = _stock_file("personal", int(Year) - 1)
        previous_non_private_path = _stock_file("fleet", int(Year) - 1)

        
        
        if int(Year) == 2026 and (
            not os.path.exists(previous_private_owned_path)
            or not os.path.exists(previous_non_private_path)
        ):
            previous_private_owned = pd.DataFrame(
                initial_private_owned,
                index=vehicle_types,
                columns=ages,
            )
            previous_non_private = pd.DataFrame(
                initial_non_private,
                index=vehicle_types,
                columns=ages,
            )
        else:
            missing = [
                path
                for path in [previous_private_owned_path, previous_non_private_path]
                if not os.path.exists(path)
            ]
            if missing:
                raise FileNotFoundError(
                    "Previous-year provincial stock is missing. "
                    "Run the period notebook sequentially from 2025. "
                    f"Missing: {missing}"
                )
            with open(previous_private_owned_path, "rb") as file:
                previous_private_owned = pickle.load(file)
            with open(previous_non_private_path, "rb") as file:
                previous_non_private = pickle.load(file)

        private_owned_stock, private_owned_by_age = _calculate_stock(
            year=int(Year),
            is_private_owned_market=True,
            is_non_private_market=False,
            previous_stock_by_age=previous_private_owned,
            market_df=df_model_private_owned_vehicle_market,
            private_owned_sales_matrix=None,
            survival_data=UNIFIED_SURVIVAL_DATA,
            vehicle_types=vehicle_types,
            powertrain_map=powertrain_map,
            initial_stock_data_private_owned=initial_private_owned,
            initial_stock_data_non_private=initial_non_private,
            initial_stock_data=initial_private_owned + initial_non_private,
        )
        non_private_stock, non_private_by_age = _calculate_stock(
            year=int(Year),
            is_private_owned_market=False,
            is_non_private_market=True,
            previous_stock_by_age=previous_non_private,
            market_df=df_model_non_private_vehicle_market,
            private_owned_sales_matrix=None,
            survival_data=UNIFIED_SURVIVAL_DATA,
            vehicle_types=vehicle_types,
            powertrain_map=powertrain_map,
            initial_stock_data_private_owned=initial_private_owned,
            initial_stock_data_non_private=initial_non_private,
            initial_stock_data=initial_private_owned + initial_non_private,
        )

    private_owned_stock = private_owned_by_age.sum(axis=1).to_dict()
    non_private_stock = non_private_by_age.sum(axis=1).to_dict()
    stock_df = _stock_dataframe(
        vehicle_types,
        private_owned_stock,
        non_private_stock,
    )

    with open(_stock_file("personal", Year), "wb") as file:
        pickle.dump(private_owned_by_age, file)
    with open(_stock_file("fleet", Year), "wb") as file:
        pickle.dump(non_private_by_age, file)
    with open(_stock_file("total", Year), "wb") as file:
        pickle.dump(
            private_owned_by_age.add(non_private_by_age, fill_value=0.0),
            file,
        )

    return stock_df, {
        "stock": stock_df,
        "stock_by_age_private_owned": private_owned_by_age,
        "stock_by_age_non_private": non_private_by_age,
    }
