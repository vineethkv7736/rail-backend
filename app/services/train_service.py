from datetime import datetime

import httpx

from app.core.config import settings
from app.schemas.train import (
    BookingResponse,
    PNRStatus,
    SeatAvailabilityDay,
    SeatAvailabilityResponse,
    TrainStatus,
)


class ProviderConfigError(Exception):
    pass


class ExternalAPIError(Exception):
    pass


class TrainService:
    def __init__(self):
        self.railradar_api_key = settings.RAILRADAR_API_KEY or settings.RAILWAY_API_KEY
        self.indian_rail_api_key = settings.INDIAN_RAIL_API_KEY
        self.base_url = settings.RAILWAY_API_BASE_URL.rstrip("/")
        self.live_status_base_url = settings.RAILWAY_LIVE_STATUS_BASE_URL.rstrip("/")

    def has_api_key(self) -> bool:
        return bool(self.railradar_api_key or self.indian_rail_api_key)

    async def get_live_status(self, train_number: str) -> TrainStatus:
        """
        Fetch live status from RailRadar if configured, otherwise return a deterministic mock.
        """
        if not self.railradar_api_key:
            return self._get_mock_status(train_number)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.live_status_base_url}/trains/{train_number}",
                    params={"dataType": "live"},
                    headers={"X-API-Key": self.railradar_api_key},
                    timeout=10.0,
                )

                if response.status_code != 200:
                    return self._get_mock_status(train_number)

                data = response.json()
                if not data.get("success") or not data.get("data"):
                    return self._get_mock_status(train_number)

                live_data = data["data"]
                current_station = live_data.get("currentStation", {}).get("name", "Unknown")
                delay = int(live_data.get("delay", 0) or 0)
                status_enum = "DELAYED" if delay > 15 else "ON_TIME"

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
                    updated_at=datetime.now(),
                    message=msg,
                )
        except Exception:
            return self._get_mock_status(train_number)

        return self._get_mock_status(train_number)

    async def search_stations(self, query: str) -> list[dict]:
        """
        Search for stations by name or code using the existing live-status provider.
        """
        if not self.railradar_api_key:
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.live_status_base_url}/search/stations",
                    params={"query": query},
                    headers={"X-API-Key": self.railradar_api_key},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    return data if isinstance(data, list) else []
        except Exception:
            return []

        return []

    async def get_trains_between_stations(self, from_code: str, to_code: str) -> list[dict]:
        """
        Get trains between two stations using the existing live-status provider.
        """
        if not self.railradar_api_key:
            return []

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.live_status_base_url}/trains/between",
                    params={"from": from_code, "to": to_code},
                    headers={"X-API-Key": self.railradar_api_key},
                    timeout=10.0,
                )
                if response.status_code == 200:
                    data = response.json()
                    if isinstance(data, dict) and "data" in data:
                        return data["data"]
                    return data
        except Exception:
            return []

        return []

    async def get_pnr_status(self, pnr: str) -> PNRStatus:
        """
        Fetch PNR status from indianrailapi.com.
        """
        if not self.indian_rail_api_key:
            raise ProviderConfigError(
                "INDIAN_RAIL_API_KEY is not configured. PNR lookup requires a separate provider key."
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/PNRCheck/apikey/{self.indian_rail_api_key}/PNRNumber/{pnr}/",
                    timeout=15.0,
                )
                if response.status_code != 200:
                    raise ExternalAPIError(
                        f"PNR provider returned HTTP {response.status_code}."
                    )

                data = response.json()
                if not self._api_call_succeeded(data):
                    raise ExternalAPIError(
                        data.get("Message")
                        or data.get("Error")
                        or "PNR provider rejected the request."
                    )

                passengers = data.get("Passengers", []) or data.get("passengers", [])
                first_passenger = passengers[0] if passengers else {}

                return PNRStatus(
                    pnr=pnr,
                    train_number=str(data.get("TrainNumber") or data.get("train_number") or ""),
                    train_name=data.get("TrainName") or data.get("train_name"),
                    journey_date=data.get("JourneyDate") or data.get("journey_date"),
                    from_station=data.get("From") or data.get("from_station"),
                    to_station=data.get("To") or data.get("to_station"),
                    booking_status=str(
                        first_passenger.get("BookingStatus")
                        or first_passenger.get("booking_status")
                        or data.get("BookingStatus")
                        or "UNKNOWN"
                    ),
                    current_status=str(
                        first_passenger.get("CurrentStatus")
                        or first_passenger.get("current_status")
                        or data.get("CurrentStatus")
                        or "UNKNOWN"
                    ),
                    chart_prepared=bool(data.get("ChartPrepared") or data.get("chart_prepared")),
                    passengers=passengers,
                    api_source="indianrailapi.com",
                )
        except httpx.HTTPError as exc:
            raise ExternalAPIError(f"PNR provider request failed: {exc}") from exc

    async def get_seat_availability(
        self,
        train_number: str,
        from_station: str,
        to_station: str,
        journey_date: str,
        class_code: str,
        quota: str = "GN",
    ) -> SeatAvailabilityResponse:
        """
        Fetch seat availability from indianrailapi.com.
        """
        if not self.indian_rail_api_key:
            raise ProviderConfigError(
                "INDIAN_RAIL_API_KEY is not configured. Seat availability requires a separate provider key."
            )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    (
                        f"{self.base_url}/SeatAvailability/apikey/{self.indian_rail_api_key}/"
                        f"TrainNumber/{train_number}/From/{from_station}/To/{to_station}/"
                        f"Date/{journey_date}/Quota/{quota}/Class/{class_code}/"
                    ),
                    timeout=15.0,
                )
                if response.status_code != 200:
                    raise ExternalAPIError(
                        f"Seat availability provider returned HTTP {response.status_code}."
                    )

                data = response.json()
                if not self._api_call_succeeded(data):
                    raise ExternalAPIError(
                        data.get("Message")
                        or data.get("Error")
                        or "Seat availability provider rejected the request."
                    )

                availability_items = data.get("Availability") or data.get("availability") or []
                availability = [
                    SeatAvailabilityDay(
                        date=str(item.get("Date") or item.get("date") or journey_date),
                        status=str(item.get("Status") or item.get("status") or "UNKNOWN"),
                        probability=item.get("Probability") or item.get("probability"),
                    )
                    for item in availability_items
                ]

                return SeatAvailabilityResponse(
                    train_number=train_number,
                    train_name=data.get("TrainName") or data.get("train_name"),
                    from_station=from_station,
                    to_station=to_station,
                    journey_date=journey_date,
                    class_code=class_code,
                    quota=quota,
                    availability=availability,
                    api_source="indianrailapi.com",
                )
        except httpx.HTTPError as exc:
            raise ExternalAPIError(f"Seat availability request failed: {exc}") from exc

    async def get_booking_support(self) -> BookingResponse:
        """
        Booking is intentionally not implemented via a free API because Indian Railways
        ticketing requires an IRCTC-authorized provider.
        """
        return BookingResponse(
            supported=False,
            provider=None,
            message=(
                "Ticket booking is not available through a free public API. "
                "You need an IRCTC-authorized booking partner or official B2B integration."
            ),
        )

    def _api_call_succeeded(self, data: dict) -> bool:
        response_code = str(data.get("ResponseCode", "")).strip()
        return response_code in {"200", "1", "SUCCESS"} or bool(data.get("Availability") or data.get("Passengers"))

    def _get_mock_status(self, train_number: str) -> TrainStatus:
        is_late = int(train_number) % 2 == 0 if train_number.isdigit() else False
        delay = 35 if is_late else 5
        status_enum = "DELAYED" if delay > 15 else "ON_TIME"

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
            message=msg,
        )

    def _get_mock_pnr_status(self, pnr: str) -> PNRStatus:
        return PNRStatus(
            pnr=pnr,
            train_number="12627",
            train_name="Karnataka Express",
            journey_date=datetime.now().strftime("%d-%m-%Y"),
            from_station="SBC",
            to_station="NDLS",
            booking_status="WL 12",
            current_status="RAC 3",
            chart_prepared=False,
            passengers=[
                {
                    "Passenger": 1,
                    "BookingStatus": "WL 12",
                    "CurrentStatus": "RAC 3",
                }
            ],
            api_source="mock",
        )

    def _get_mock_seat_availability(
        self,
        train_number: str,
        from_station: str,
        to_station: str,
        journey_date: str,
        class_code: str,
        quota: str,
    ) -> SeatAvailabilityResponse:
        return SeatAvailabilityResponse(
            train_number=train_number,
            train_name="Sample Express",
            from_station=from_station,
            to_station=to_station,
            journey_date=journey_date,
            class_code=class_code,
            quota=quota,
            availability=[
                SeatAvailabilityDay(date=journey_date, status="AVAILABLE 23", probability="High"),
                SeatAvailabilityDay(date=journey_date, status="RAC 11", probability="Medium"),
            ],
            api_source="mock",
        )


train_service = TrainService()
