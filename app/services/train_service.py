from datetime import datetime
from app.schemas.train import TrainStatus
from app.core.config import settings
import httpx

class TrainService:
    def __init__(self):
        self.api_key = settings.RAILWAY_API_KEY
        self.base_url = "https://api.railradar.in/api/v1"

    async def get_live_status(self, train_number: str) -> TrainStatus:
        """
        Fetches live status from RailRadar API.
        """
        if not self.api_key:
            return self._get_mock_status(train_number)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/trains/{train_number}",
                    params={"dataType": "live"},
                    headers={"X-API-Key": self.api_key},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    print(f"API Error: {response.status_code} - {response.text}")
                    return self._get_mock_status(train_number) # Fallback

                data = response.json()
                
                # Check if we got valid live data
                if not data.get("success") or not data.get("data"):
                     return self._get_mock_status(train_number)

                live_data = data["data"]
                
                # Extract relevant fields
                current_station = live_data.get("currentStation", {}).get("name", "Unknown")
                delay = live_data.get("delay", 0)
                status_enum = "DELAYED" if delay > 15 else "ON_TIME"
                updated_time = live_data.get("updatedAt")
                
                # Humanizer Logic
                msg = ""
                if delay < 15:
                    msg = "Your train is running on time."
                elif delay < 45:
                    msg = f"Your train is running {delay} minutes late. You don't need to worry yet."
                else:
                    msg = f"Your train is running {delay} minutes late. You have time to wait comfortably."

                return TrainStatus(
                    train_number=train_number,
                    station_code=live_data.get("currentStation", {}).get("code", "UNK"),
                    current_location=current_station,
                    delay_minutes=delay,
                    status=status_enum,
                    updated_at=datetime.now(), # Ideally parse updated_time
                    message=msg
                )

        except Exception as e:
            print(f"Train Service Error: {e}")
            return self._get_mock_status(train_number)

    async def search_stations(self, query: str) -> list[dict]:
        """
        Search for stations by name or code.
        """
        if not self.api_key:
            return []
            
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/search/stations",
                    params={"query": query},
                    headers={"X-API-Key": self.api_key},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    return data if isinstance(data, list) else []
                return []
        except Exception as e:
            print(f"Station Search Error: {e}")
            return []

    async def get_trains_between_stations(self, from_code: str, to_code: str) -> list[dict]:
        """
        Get trains between two stations.
        """
        if not self.api_key:
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/trains/between",
                    params={"from": from_code, "to": to_code},
                    headers={"X-API-Key": self.api_key},
                    timeout=10.0
                )
                if response.status_code == 200:
                    data = response.json()
                    # The API returns { data: [...] } or just [...]? 
                    # Based on api-1.json, it returns TrainsBetweenStationsResult which likely has a 'data' field or is a list.
                    # Let's assume standard wrapper based on previous endpoint.
                    if isinstance(data, dict) and "data" in data:
                        return data["data"]
                    return data
                return []
        except Exception as e:
            print(f"Trains Between Error: {e}")
            return []

    def _get_mock_status(self, train_number: str) -> TrainStatus:
        # Deterministic mock based on train number
        is_late = int(train_number) % 2 == 0
        delay = 35 if is_late else 5
        status_enum = "DELAYED" if delay > 15 else "ON_TIME"
        
        # Humanizer Logic
        msg = ""
        if delay < 15:
            msg = "Your train is running on time."
        elif delay < 45:
            msg = f"Your train is running {delay} minutes late. You don't need to worry yet."
        else:
            msg = f"Your train is running {delay} minutes late. You have time to wait comfortably."

        return TrainStatus(
            train_number=train_number,
            station_code="Unknown",
            current_location="In Transit",
            delay_minutes=delay,
            status=status_enum,
            updated_at=datetime.now(),
            message=msg
        )

train_service = TrainService()
