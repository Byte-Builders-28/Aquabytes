import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini with API key from .env
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def classify_location(location: str, regions: list[str]) -> str:
    """
    Uses Gemini 2.5 to classify which region a location belongs to.
    
    Args:
        location (str): The location name to check.
        regions (list[str]): A list of possible regions.
        
    Returns:
        str: The region name from the list that best matches the location.
    """
    prompt = f"""
    I have the following regions: {regions}.
    The location is: "{location}".
    
    Your task: return EXACTLY which region from the list this location belongs to.
    Only return the region name, nothing else.
    """

    model = genai.GenerativeModel("gemini-2.5-flash-lite")
    response = model.generate_content(prompt)

    return response.text.strip()


# # Example usage
# regions = ["North India", "South India", "West India", "East India"]
# location = "Goa"

# print("Region:", classify_location(location, regions))