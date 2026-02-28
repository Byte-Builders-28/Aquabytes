from  .sim_rainwater import simulate_system_annual, estimate_rainwater_potential,estimate_water_demand

def estimate_tank_size(
    potential,
    demand,
    population,
    days_of_storage=30,
    per_person_min=135,
    scale_factor=0.5
):
    """
    Suggest a realistic tank size:
    - Minimum: family storage for given days.
    - Maximum: whichever is smaller (annual potential or demand).
    - Recommended: somewhere between min and max, controlled by scale_factor (0-1).
    """

    min_tank = population * per_person_min * days_of_storage
    ceiling = min(potential, demand)

    if ceiling <= min_tank:
        # Not much potential → just stick with minimum
        return min_tank

    # Scale between min_tank and ceiling
    tank_size = min_tank + (ceiling - min_tank) * scale_factor

    return tank_size



def estimate_cost(tank_size, cost_per_liter=8.5):
    """Rough cost based on tank size."""
    return tank_size * cost_per_liter


def feasibility_score(area_m2, rainfall_mm, temp, humidity, population,
                      roof_type, budget=None, tank_capacity=20000, groundwater_capacity=50000):
    """
    Compute feasibility using the detailed annual simulation.
    Returns a score (0-100) and key stats.
    """
    total_supply, demand_total, reliability_ratio, unmet, gw_recharge = simulate_system_annual(
        avg_rainfall=rainfall_mm,
        avg_temp=temp,
        avg_humidity=humidity,
        area_m2=area_m2,
        population=population,
        tank_capacity=tank_capacity,
        groundwater_capacity=groundwater_capacity,
        rooftype=roof_type
    )

    cost = estimate_cost(tank_capacity/30)

    # Start with reliability (main indicator)
    score = reliability_ratio * 70  # 0.0-1.0 → 0-70 points

    # Penalize unmet demand (10 points max)
    unmet_ratio = unmet / demand_total if demand_total > 0 else 0
    score += max(0, 10 * (1 - unmet_ratio))

    # Budget factor (20 points max)
    if budget:
        if cost <= budget:
            score += 20
        else:
            score += max(0, 20 * (budget / cost))
    else:
        score += 20

    return {
        "score": min(score, 100),
        "supply": total_supply,
        "demand": demand_total,
        "unmet": unmet,
        "reliability": reliability_ratio,
        "cost_estimate": cost,
        "gw_recharge": gw_recharge
    }


def recommend_system(area_m2, rainfall_mm, temp, humidity, population, roof_type,
                     budget=None, groundwater_capacity=50000):

    # Step 1: estimate potential & demand
    potential = estimate_rainwater_potential(area_m2, rainfall_mm, humidity, temp, roof_type)
    demand = estimate_water_demand(population)

    # Step 2: estimate required tank size
    tank_capacity = estimate_tank_size(potential, demand, population)

    # Step 3: get feasibility with this tank size
    result = feasibility_score(area_m2, rainfall_mm, temp, humidity,
                               population, roof_type, budget, tank_capacity, groundwater_capacity)

    supply = result["supply"]
    recharge = result["gw_recharge"]

    # Step 4: decision rules
    if supply >= demand * 0.9:
        system_type = "storage"
        reason = "Rainwater supply can meet most of the demand."
    elif recharge > groundwater_capacity * 0.05:
        system_type = "recharge"
        reason = "Significant recharge potential detected."
    else:
        system_type = "hybrid"
        reason = "Rainwater alone is not enough; recharge + storage recommended."

    # Final output
    result.update({
        "system_type": system_type,
        "reason": reason,
        "tank_size": tank_capacity/30,
    })

    return result

