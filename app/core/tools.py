import httpx
from app.core.config import settings
from app.services.train_service import train_service

BASE_URL = "https://api.railradar.in/api/v1"
API_KEY = settings.RAILWAY_API_KEY

def check_train_status(train_number: str) -> dict:
    """
    Get the live running status of a train by its number.
    Returns delay, location, and status message.
    """
    if not API_KEY:
        return train_service._get_mock_status(train_number).model_dump()

    try:
        response = httpx.get(
            f"{BASE_URL}/trains/{train_number}",
            params={"dataType": "live"},
            headers={"X-API-Key": API_KEY},
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            if data.get("success") and data.get("data"):
                # We can reuse the logic from TrainService or just return raw data 
                # and let LLM interpret it. LLM is good at interpreting JSON.
                # But for consistency with the prompt, let's return the raw data 
                # and let the LLM do the "Humanizing" based on its system prompt.
                return data["data"]
        return train_service._get_mock_status(train_number).model_dump()
    except Exception as e:
        print(f"Tool Error: {e}")
        return train_service._get_mock_status(train_number).model_dump()

def search_stations(query: str) -> list[dict]:
    """
    Search for a railway station by name or code.
    Returns a list of matching stations with their codes.
    """
    if not API_KEY: return []
    try:
        response = httpx.get(
            f"{BASE_URL}/search/stations",
            params={"query": query},
            headers={"X-API-Key": API_KEY},
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            if not data:
                return [{"error": f"No stations found matching '{query}'. Please ask the user for the exact Station Code."}]
            return data
        return [{"error": "API Error converting station name."}]
    except Exception as e:
        print(f"Tool Error: {e}")
        return [{"error": str(e)}]

def get_trains_between_stations(from_station_code: str, to_station_code: str) -> list[dict]:
    """
    Find trains running between two stations.
    CRITICAL: Requires **Station Codes** (e.g., 'CNGR', 'TVC').
    DO NOT pass full station names (e.g. 'Chengannur'). You MUST search for codes first.
    """
    if not API_KEY: return []
    try:
        response = httpx.get(
            f"{BASE_URL}/trains/between",
            params={"from": from_station_code, "to": to_station_code},
            headers={"X-API-Key": API_KEY},
            timeout=10.0
        )
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, dict) and "data" in data:
                return data["data"]
            return data
        return []
    except Exception as e:
        print(f"Tool Error: {e}")
        return []

railway_tools = [check_train_status, search_stations, get_trains_between_stations]
