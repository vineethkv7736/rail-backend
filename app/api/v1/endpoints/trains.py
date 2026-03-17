from fastapi import APIRouter, HTTPException, Query

from app.schemas.train import (
    BookingRequest,
    BookingResponse,
    PNRStatus,
    SeatAvailabilityResponse,
    TrainStatus,
)
from app.services.train_service import ExternalAPIError, ProviderConfigError, train_service

router = APIRouter()


@router.get("/status", response_model=TrainStatus)
async def train_status(
    train_number: str = Query(..., min_length=5, max_length=6),
):
    return await train_service.get_live_status(train_number)


@router.get("/pnr", response_model=PNRStatus)
async def pnr_status(
    pnr: str = Query(..., min_length=10, max_length=10),
):
    try:
        return await train_service.get_pnr_status(pnr)
    except ProviderConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ExternalAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/seat-availability", response_model=SeatAvailabilityResponse)
async def seat_availability(
    train_number: str = Query(..., min_length=5, max_length=6),
    from_station: str = Query(..., min_length=2, max_length=5),
    to_station: str = Query(..., min_length=2, max_length=5),
    journey_date: str = Query(..., description="DD-MM-YYYY"),
    class_code: str = Query(..., min_length=1, max_length=3),
    quota: str = Query("GN", min_length=1, max_length=4),
):
    try:
        return await train_service.get_seat_availability(
            train_number=train_number,
            from_station=from_station.upper(),
            to_station=to_station.upper(),
            journey_date=journey_date,
            class_code=class_code.upper(),
            quota=quota.upper(),
        )
    except ProviderConfigError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except ExternalAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.post("/booking", response_model=BookingResponse)
async def booking_info(_: BookingRequest):
    return await train_service.get_booking_support()
