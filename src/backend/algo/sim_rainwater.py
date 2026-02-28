def dynamic_coefficient(base, humidity):
    """
    Adjust collection efficiency based on humidity (0-100%).
    High humidity → less evaporation → higher efficiency.
    """
    # Normalize humidity to 0-1
    h = humidity / 100.0
    # Scale between base*0.7 (dry) and base*1.1 (humid)
    return max(0, min(1, base * (0.7 + 0.4 * h)))


def evaporation_loss(temp, days, surface_area):
    """
    Estimate evaporation loss (liters) based on temp (°C),
    days in month, and water surface area (m²).
    """
    # Simple empirical rate: higher temp → higher evaporation
    # Evap (mm/day) ≈ 0.5 + 0.05 * (temp - 20)
    evap_rate_mm_day = max(0, 0.5 + 0.05 * (temp - 20))
    evap_mm = evap_rate_mm_day * days
    # mm * m² = liters
    return evap_mm * surface_area

def estimate_rainwater_potential(area_m2, rainfall_mm, humidity, temp, roof_type):
    roof_coefficients = {
    "Concrete (RCC)": 0.75,
    "Cement Tiles": 0.70,
    "Clay Tiles": 0.60,
    "Metal Sheet": 0.85,
    "GI Sheet": 0.80,
    "Asbestos Sheet": 0.75,
    "Slate": 0.65,
    "Stone Slab": 0.65,
    "Corrugated Sheet": 0.80,
    "Thatched": 0.35,
    "Plastic Sheet / PVC": 0.85,
    "Glass": 0.90,
    "Green Roof (vegetated)": 0.30,
    "Other": 0.75
    }

    coefficient = roof_coefficients[roof_type]

    """Estimate annual harvestable rainwater (liters) considering humidity & evaporation."""
    efficiency = dynamic_coefficient(coefficient, humidity)
    rain_collected = area_m2 * rainfall_mm * efficiency

    # evaporation loss (tank surface ≈ 10% of roof area, assume 365 days)
    evap = evaporation_loss(temp, 365, area_m2 * 0.1)
    return max(0, rain_collected - evap)


def estimate_water_demand(population, usage_per_day=135):
    """Estimate annual water demand (liters)."""
    return population * usage_per_day * 365



def simulate_system_annual(
    avg_rainfall,  # mm/year
    avg_temp,      # °C
    avg_humidity,  # %
    area_m2,
    population,
    tank_capacity,
    rooftype,
    usage_per_day=135,
    groundwater_capacity=50000,
    soil_infiltration=0.5
):
    """Simulate rainwater harvesting + groundwater recharge using annual averages (no loop)."""

    # Total annual demand
    demand_total = estimate_water_demand(population, usage_per_day)
    # Rainwater collected over the year
    rain_collected = estimate_rainwater_potential(area_m2, avg_rainfall, avg_humidity, avg_temp, roof_type=rooftype)

    # Start tank and groundwater
    tank_level = rain_collected
    gw_level = min(demand_total, groundwater_capacity * 0.5)
    recharge_total = 0  # track recharge

    tank_capacity *= 12  # so it spans 1 y.. tank is for 30 days

    # Handle tank overflow
    if tank_level > tank_capacity:
        recharge = (tank_level - tank_capacity) * soil_infiltration
        recharge_total += recharge
        gw_level = min(groundwater_capacity, gw_level + recharge)
        tank_level = tank_capacity

    # NEW: Natural infiltration recharge from rainfall
    natural_recharge = rain_collected * 0.1 * soil_infiltration  # 10% of collected rain goes into ground
    gw_level = min(groundwater_capacity, gw_level + natural_recharge)
    recharge_total += natural_recharge

    # Supply demand from tank first
    if tank_level >= demand_total:
        tank_level -= demand_total
        total_supply = demand_total
        unmet = 0
        reliability_ratio = 1
    else:
        demand_left = demand_total - tank_level
        total_supply = tank_level
        tank_level = 0

        if gw_level >= demand_left:
            gw_level -= demand_left
            total_supply += demand_left
            unmet = 0
            reliability_ratio = 1
        else:
            total_supply += gw_level
            unmet = demand_left - gw_level
            gw_level = 0
            reliability_ratio = total_supply / demand_total

    return total_supply, demand_total, reliability_ratio, unmet, recharge_total
