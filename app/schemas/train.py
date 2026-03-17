from pydantic import BaseModel, Field
from datetime import datetime

class TrainStatus(BaseModel):
    train_number: str
    station_code: str
    current_location: str | None = None
    delay_minutes: int
    status: str # "ON_TIME", "DELAYED", "CANCELLED"
    updated_at: datetime
    message: str | None = None # The "Humanized" message

class PNRStatus(BaseModel):
    pnr: str
    train_number: str | None = None
    train_name: str | None = None
    journey_date: str | None = None
    from_station: str | None = None
    to_station: str | None = None
    booking_status: str # "CNF", "RAC 12", "WL 45"
    current_status: str # "CNF", "RAC 5"
    chart_prepared: bool
    passengers: list[dict] = Field(default_factory=list)
    api_source: str | None = None

class SeatAvailabilityDay(BaseModel):
    date: str
    status: str
    probability: str | None = None

class SeatAvailabilityResponse(BaseModel):
    train_number: str
    train_name: str | None = None
    from_station: str
    to_station: str
    journey_date: str
    class_code: str
    quota: str
    availability: list[SeatAvailabilityDay]
    api_source: str | None = None

class BookingRequest(BaseModel):
    train_number: str
    from_station: str
    to_station: str
    journey_date: str
    class_code: str
    quota: str = "GN"
    pnr: str | None = None

class BookingResponse(BaseModel):
    supported: bool
    message: str
    provider: str | None = None
