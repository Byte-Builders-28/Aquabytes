from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

def get_location_details(address):
    """
    Fetches location details for a given address using the Nominatim geocoder.
    Cleans the address and retries if the first attempt fails.
    """
    geolocator = Nominatim(user_agent="location_fetcher")

    def _sanitize_address(addr: str) -> str:
        blacklist = [
            "community development block",
            "district",
            "tehsil",
            "subdivision",
            "state",
            "city"
        ]
        for word in blacklist:
            addr = addr.replace(word, "").strip(", ")
        return addr

    try:
        clean_address = _sanitize_address(address)
        print(f"[DEBUG] Nominatim query: {clean_address}")

        location = geolocator.geocode(clean_address, timeout=10)

        # fallback: try only last part (often city/town)
        if not location and "," in clean_address:
            fallback = clean_address.split(",")[0].strip()
            print(f"[DEBUG] Retrying with fallback: {fallback}")
            location = geolocator.geocode(fallback, timeout=10)

        if location:
            print(f"[DEBUG] Raw location response: {location.raw}")
            return {
                "address": location.address,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "raw_data": location.raw
            }
        else:
            print(f"[ERROR] Could not find coordinates for: {address}")
            return None

    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"[ERROR] Geocoding service error: {e}")
        return None

def get_address_from_coords(lat: float, lng: float):
    """
    Fetches address details for given latitude and longitude using Nominatim.
    Returns city, state, full address, and raw data.
    """
    geolocator = Nominatim(user_agent="location_fetcher")
    try:
        location = geolocator.reverse((lat, lng), timeout=10)
        if location:
            components = location.raw.get("address", {})
            city = components.get("city") or components.get("town") or components.get("village") or components.get("county")
            state = components.get("state")
            return {
                "city": city,
                "state": state,
                "address": location.address,
                "raw_data": location.raw
            }
        else:
            print(f"[ERROR] Could not find address for coordinates: {lat}, {lng}")
            return None
    except (GeocoderTimedOut, GeocoderServiceError) as e:
        print(f"[ERROR] Reverse geocoding service error: {e}")
        return None
