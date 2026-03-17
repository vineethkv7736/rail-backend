import httpx
from app.core.config import settings
from app.services.train_service import train_service

BASE_URL = settings.RAILWAY_LIVE_STATUS_BASE_URL.rstrip("/")
RAILRADAR_API_KEY = settings.RAILRADAR_API_KEY or settings.RAILWAY_API_KEY
INDIAN_RAIL_API_KEY = settings.INDIAN_RAIL_API_KEY
PNR_BASE_URL = settings.RAILWAY_API_BASE_URL.rstrip("/")

def check_train_status(train_number: str) -> dict:
    """
    Get the live running status of a train by its number.
    Returns delay, location, and status message.
    """
    if not RAILRADAR_API_KEY:
        return train_service._get_mock_status(train_number).model_dump()

    try:
        response = httpx.get(
            f"{BASE_URL}/trains/{train_number}",
            params={"dataType": "live"},
            headers={"X-API-Key": RAILRADAR_API_KEY},
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
    if not RAILRADAR_API_KEY: return []
    try:
        response = httpx.get(
            f"{BASE_URL}/search/stations",
            params={"query": query},
            headers={"X-API-Key": RAILRADAR_API_KEY},
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
    if not RAILRADAR_API_KEY: return []
    try:
        response = httpx.get(
            f"{BASE_URL}/trains/between",
            params={"from": from_station_code, "to": to_station_code},
            headers={"X-API-Key": RAILRADAR_API_KEY},
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

def check_pnr_status(pnr: str) -> dict:
    """
    Fetch PNR status for a 10-digit PNR number.
    """
    if not INDIAN_RAIL_API_KEY:
        return {"error": "INDIAN_RAIL_API_KEY is not configured."}
    try:
        response = httpx.get(
            f"{PNR_BASE_URL}/PNRCheck/apikey/{INDIAN_RAIL_API_KEY}/PNRNumber/{pnr}/",
            timeout=15.0,
        )
        if response.status_code == 200:
            data = response.json()
            if train_service._api_call_succeeded(data):
                return data
        return {
            "error": f"PNR provider returned HTTP {response.status_code}.",
            "provider": "indianrailapi.com",
        }
    except Exception as e:
        print(f"Tool Error: {e}")
        return {"error": str(e), "provider": "indianrailapi.com"}

def check_seat_availability(
    train_number: str,
    from_station: str,
    to_station: str,
    journey_date: str,
    class_code: str,
    quota: str = "GN",
) -> dict:
    """
    Check seat availability for a train.
    journey_date must be DD-MM-YYYY.
    """
    if not INDIAN_RAIL_API_KEY:
        return {"error": "INDIAN_RAIL_API_KEY is not configured."}
    try:
        response = httpx.get(
            (
                f"{PNR_BASE_URL}/SeatAvailability/apikey/{INDIAN_RAIL_API_KEY}/"
                f"TrainNumber/{train_number}/From/{from_station}/To/{to_station}/"
                f"Date/{journey_date}/Quota/{quota}/Class/{class_code}/"
            ),
            timeout=15.0,
        )
        if response.status_code == 200:
            data = response.json()
            if train_service._api_call_succeeded(data):
                return data
        return {
            "error": f"Seat availability provider returned HTTP {response.status_code}.",
            "provider": "indianrailapi.com",
        }
    except Exception as e:
        print(f"Tool Error: {e}")
        return {"error": str(e), "provider": "indianrailapi.com"}

railway_tools = [
    check_train_status,
    search_stations,
    get_trains_between_stations,
    check_pnr_status,
    check_seat_availability,
]
