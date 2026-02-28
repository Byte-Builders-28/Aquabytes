from utils.weather import get_info_from_location
from utils.get_region import classify_location
from utils.get_rain import get_mean_rainfall
from algo.get_task import recommend_system

reg = ['ANDAMAN & NICOBAR ISLANDS', 'ARUNACHAL PRADESH', 'ASSAM & MEGHALAYA', 'BIHAR', 'CHHATTISGARH', 'COASTAL ANDHRA PRADESH', 'COASTAL KARNATAKA', 'EAST MADHYA PRADESH', 'EAST RAJASTHAN', 'EAST UTTAR PRADESH', 'GANGETIC WEST BENGAL', 'GUJARAT REGION', 'HARYANA DELHI & CHANDIGARH', 'HIMACHAL PRADESH', 'JAMMU & KASHMIR', 'JHARKHAND', 'KERALA', 'KONKAN & GOA', 'LAKSHADWEEP', 'MADHYA MAHARASHTRA', 'MATATHWADA', 'NAGA MANI MIZO TRIPURA', 'NORTH INTERIOR KARNATAKA', 'ORISSA', 'PUNJAB', 'RAYALSEEMA', 'SAURASHTRA & KUTCH', 'SOUTH INTERIOR KARNATAKA', 'SUB HIMALAYAN WEST BENGAL & SIKKIM', 'TAMIL NADU', 'TELANGANA', 'UTTARAKHAND', 'VIDARBHA', 'WEST MADHYA PRADESH', 'WEST RAJASTHAN', 'WEST UTTAR PRADESH']

def get_RTWH(
    area_m2: float,
    population: int,
    state: str,
    city: str,
    rooftype: str,
    budget: float = None,
):
    """
    Get Rainwater Tank + Water Harvesting (RTWH) recommendation.
    """

    print("[DEBUG] Starting get_RTWH...")
    print(f"[DEBUG] Inputs: area_m2={area_m2}, population={population}, state={state}, city={city}, budget={budget}")

    # Fetch weather info
    info = get_info_from_location(state=state, city=city)
    print(f"[DEBUG] Weather info fetched: {info}")
    temp = info["temperature"]
    humidity = info["humidity"]

    # Classify region
    region = classify_location(f"{city}, {state}", reg)
    print(f"[DEBUG] Classified region: {region}")

    # Get rainfall
    rainfall_mm = get_mean_rainfall(region)
    print(f"[DEBUG] Mean rainfall for region {region}: {rainfall_mm} mm")

    # Run recommendation
    result = recommend_system(
        area_m2=area_m2,
        rainfall_mm=rainfall_mm,
        temp=temp,
        humidity=humidity,
        population=population,
        budget=budget,
        roof_type=rooftype
        # groundwater_capacity=groundwater_capacity
    )
    print(f"[DEBUG] Recommendation result: {result}")

    return result
