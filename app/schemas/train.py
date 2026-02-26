from pydantic import BaseModel
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
    train_number: str
    booking_status: str # "CNF", "RAC 12", "WL 45"
    current_status: str # "CNF", "RAC 5"
    chart_prepared: bool
