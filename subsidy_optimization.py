"""Selected province-generic SOP-CN functions; runtime inputs are supplied by the parent model."""

from __future__ import annotations


def _stable_ga_seed(province_name, year):
    """Return a cross-process-stable seed and its auditable key."""
    seed_key = (
        f"SOP-CN-provincial-V4|{str(province_name).strip()}|{int(year)}"
    )
    digest = hashlib.sha256(seed_key.encode("utf-8")).digest()
    seed = int.from_bytes(digest[:8], byteorder="big") % (2 ** 32)
    return seed, seed_key


def _ga_annual_total_profit():
    """Annual manufacturer profit in CNY."""
    private_sales_1000 = _ga_as_float_array(
        df_model_private_owned_vehicle_market.loc[:23, "Sales (1000)"]
    )
    non_private_sales_1000 = _ga_as_float_array(
        df_model_non_private_vehicle_market.loc[:23, "Sales (1000)"]
    )
    private_price = _ga_as_float_array(
        df_model_private_owned_vehicle_market.loc[:23, "Price to consumers (\uffe5)"]
    )
    non_private_price = _ga_as_float_array(
        df_model_non_private_vehicle_market.loc[:23, "Price to consumers (\uffe5)"]
    )
    additional_subsidy = _ga_as_float_array(
        df_model.loc[:23, "Additional Subsidy to Consumers (\uffe5)"]
    )
    central_subsidy = _ga_as_float_array(
        df_model.loc[:23, "Central Gov Sub to Consumers (\uffe5)"]
    )
    local_subsidy = _ga_as_float_array(
        df_model.loc[:23, "Avg Local Gov Sub to Consumers (\uffe5)"]
    )
    production_cost = _ga_as_float_array(
        df_model.loc[:23, "Production Cost (\uffe5)"]
    )
    purchase_tax_column = next(
        column for column in df_model.columns
        if str(column).startswith("Purchase Tax to Consumers")
    )
    insurance_column = next(
        column for column in df_model.columns
        if str(column).startswith("Insurance to Consumers")
    )
    purchase_tax = _ga_as_float_array(df_model.loc[:23, purchase_tax_column])
    insurance = _ga_as_float_array(df_model.loc[:23, insurance_column])
    government_subsidy = additional_subsidy + central_subsidy + local_subsidy
    private_margin = (
        private_price - purchase_tax - insurance
        + government_subsidy - production_cost
    )
    non_private_margin = (
        non_private_price - purchase_tax - insurance
        + government_subsidy - production_cost
    )
    return float(
        1000.0 * (
            np.sum(private_sales_1000 * private_margin)
            + np.sum(non_private_sales_1000 * non_private_margin)
        )
    )




    private_sales = _ga_as_float_array(df_model_private_owned_vehicle_market.loc[:23, "Sales (1000)"])
    non_private_sales = _ga_as_float_array(df_model_non_private_vehicle_market.loc[:23, "Sales (1000)"])
    total_sales = private_sales + non_private_sales
    total_sales_sum = float(total_sales.sum())
    if total_sales_sum <= 0:
        return -1e18

    private_price = _ga_as_float_array(df_model_private_owned_vehicle_market.loc[:23, "Price to consumers (￥)"])
    non_private_price = _ga_as_float_array(df_model_non_private_vehicle_market.loc[:23, "Price to consumers (￥)"])
    additional_subsidy = _ga_as_float_array(df_model.loc[:23, "Additional Subsidy to Consumers (￥)"])
    central_subsidy = _ga_as_float_array(df_model.loc[:23, "Central Gov Sub to Consumers (￥)"])
    local_subsidy = _ga_as_float_array(df_model.loc[:23, "Avg Local Gov Sub to Consumers (￥)"])
    internal_subsidy = _ga_as_float_array(df_model.loc[:23, "Internal Subsidy to Consumer(￥)"])
    production_cost = _ga_as_float_array(df_model.loc[:23, "Production Cost (￥)"])

    purchase_tax_column = next(
        column for column in df_model.columns
        if str(column).startswith("Purchase Tax to Consumers")
    )
    insurance_column = next(
        column for column in df_model.columns
        if str(column).startswith("Insurance to Consumers")
    )
    purchase_tax = _ga_as_float_array(df_model.loc[:23, purchase_tax_column])
    insurance = _ga_as_float_array(df_model.loc[:23, insurance_column])
    government_subsidy = additional_subsidy + central_subsidy + local_subsidy
    
    
    private_margin = private_price - purchase_tax - insurance + government_subsidy - production_cost
    non_private_margin = non_private_price - purchase_tax - insurance + government_subsidy - production_cost
    profit_cny = (
        np.sum(private_sales * private_margin)
        + np.sum(non_private_sales * non_private_margin)
    ) * 1000.0
    return profit_cny / total_sales_sum / 1000.0


def _ga_sanitize_individual(individual):
    lower = float(_ga_projection_value("GA_Subsidy_Lower_Bound"))
    upper = float(_ga_projection_value("GA_Subsidy_Upper_Bound"))
    step = max(float(_ga_projection_value("GA_Subsidy_Step")), 1.0)
    values = np.asarray(individual, dtype=float)
    values = np.clip(values, lower, upper)
    values = np.round(values / step) * step
    values = values.tolist()
    if values:
        values[int(np.argmin(values))] = 0.0
    return values


def _ga_simulate_individual(individual):
    return float(_ga_simulate_population([individual])[0])


def _ga_random_individual(n_vehicles, rng):
    lower = int(_ga_projection_value("GA_Subsidy_Lower_Bound"))
    upper = int(_ga_projection_value("GA_Subsidy_Upper_Bound"))
    step = max(int(_ga_projection_value("GA_Subsidy_Step")), 1)
    if upper <= lower:
        return [0.0] * n_vehicles
    return [
        float(rng.randrange(lower, upper + step, step))
        for _ in range(n_vehicles)
    ]


def _ga_run_internal_subsidy_optimization():
    rng = random.Random(GA_RANDOM_SEED)
    n_vehicles = len(df_model.loc[:23])
    population_size = int(_ga_projection_value("GA_Population_Size"))
    cxpb = float(_ga_projection_value("GA_Crossover_Probability"))
    mutpb = float(_ga_projection_value("GA_Mutation_Probability"))
    max_stalled_generations = int(_ga_projection_value("GA_Max_Stalled_Generations"))
    min_improvement = float(_ga_projection_value("GA_Min_Improvement"))
    mutation_sigma = float(_ga_projection_value("GA_Mutation_Sigma"))
    mutation_indpb = float(_ga_projection_value("GA_Mutation_Indpb"))
    tournament_size = int(_ga_projection_value("GA_Tournament_Size"))

    zero = [0.0] * n_vehicles
    population = [zero] + [
        _ga_random_individual(n_vehicles, rng)
        for _ in range(max(population_size - 1, 0))
    ]
    fitness = _ga_simulate_population(population).tolist()
    best_idx = int(np.argmax(fitness))
    best = list(population[best_idx])
    best_fitness = float(fitness[best_idx])
    stalled_count = 0
    generation = 0
    start_time = time.time()

    while stalled_count < max_stalled_generations:
        generation += 1
        selected = []
        for _ in range(population_size):
            contenders = rng.sample(
                range(population_size),
                k=min(tournament_size, population_size),
            )
            selected.append(list(population[max(contenders, key=lambda idx: fitness[idx])]))

        offspring = []
        for i in range(0, population_size, 2):
            parent1 = list(selected[i])
            parent2 = list(selected[(i + 1) % population_size])
            if rng.random() < cxpb and n_vehicles > 2:
                point1 = rng.randint(1, n_vehicles - 2)
                point2 = rng.randint(point1 + 1, n_vehicles - 1)
                child1 = parent1[:point1] + parent2[point1:point2] + parent1[point2:]
                child2 = parent2[:point1] + parent1[point1:point2] + parent2[point2:]
            else:
                child1, child2 = parent1, parent2
            offspring.extend([child1, child2])
        offspring = offspring[:population_size]

        for individual in offspring:
            if rng.random() < mutpb:
                for idx in range(n_vehicles):
                    if rng.random() < mutation_indpb:
                        individual[idx] += rng.gauss(0.0, mutation_sigma)

        population = [best] + [_ga_sanitize_individual(ind) for ind in offspring[:-1]]
        fitness = _ga_simulate_population(population).tolist()
        current_idx = int(np.argmax(fitness))
        current_fitness = float(fitness[current_idx])
        print(f"GA generation {generation} best profit: {current_fitness:.6f}", flush=True)
        if current_fitness - best_fitness >= min_improvement:
            best = list(population[current_idx])
            best_fitness = current_fitness
            stalled_count = 0
        else:
            stalled_count += 1

    print(
        f"Internal subsidy GA ended at generation {generation} "
        f"in {time.time() - start_time:.1f}s"
    )
    return _ga_sanitize_individual(best), best_fitness, generation
