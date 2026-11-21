from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import Appointment, Store, User
from routers.reservations import CLOSE_HOUR, OPEN_HOUR, is_valid_slot
from schemas import AppointmentIn, AppointmentOut, SlotOut
from rules import can_cancel
router = APIRouter(prefix="/appointments", tags=["Appointments"])

MAX_ACTIVE_PER_USER = 2


def slot_taken(db: Session, store_id: int, slot: datetime) -> bool:
    return (
        db.query(Appointment)
        .filter(
            Appointment.store_id == store_id,
            Appointment.slot_start == slot,
            Appointment.status == "active",
        )
        .count()
        > 0
    )


@router.get("/slots", response_model=list[SlotOut])
def list_slots(
    store_id: int, day: date, db: Session = Depends(get_db)
):
    if db.get(Store, store_id) is None:
        raise HTTPException(status_code=404, detail="Store not found")
    now = datetime.now()
    slots = []
    current = datetime(day.year, day.month, day.day, OPEN_HOUR, 0)
    end = datetime(day.year, day.month, day.day, CLOSE_HOUR, 0)
    while current < end:
        taken = slot_taken(db, store_id, current)
        slots.append(SlotOut(
            slot_start=current,
            available=(not taken) and current > now,
            remaining=0 if taken else 1,
        ))
        current += timedelta(minutes=30)
    return slots


@router.post("", response_model=AppointmentOut, status_code=201)
def book_appointment(
    data: AppointmentIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if db.get(Store, data.store_id) is None:
        raise HTTPException(status_code=404, detail="Store not found")

    slot = data.slot_start
    if slot.tzinfo is not None:
        raise HTTPException(
            status_code=400,
            detail="Send slot_start without a timezone, e.g. 2026-12-01T10:00:00",
        )
    if not is_valid_slot(slot):  # R4.2, R4.6
        raise HTTPException(
            status_code=400,
            detail="Slot must be 10:00 to 17:30 on the hour or half hour",
        )
    if slot <= datetime.now():  # R4.5
        raise HTTPException(
            status_code=400, detail="Cannot book a past time slot"
        )

    if slot_taken(db, data.store_id, slot):  # R4.3
        raise HTTPException(status_code=409, detail="Slot is already booked")

    active = (
        db.query(Appointment)
        .filter(
            Appointment.user_id == user.id,
            Appointment.status == "active",
        )
        .count()
    )
    if active >= MAX_ACTIVE_PER_USER:  # R4.4
        raise HTTPException(
            status_code=400,
            detail="Maximum 2 active appointments per user",
        )

    appointment = Appointment(
        user_id=user.id, store_id=data.store_id, slot_start=slot
    )
    db.add(appointment)
    db.commit()
    db.refresh(appointment)
    return appointment


@router.get("", response_model=list[AppointmentOut])
def my_appointments(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return (
        db.query(Appointment)
        .filter(Appointment.user_id == user.id)
        .order_by(Appointment.slot_start)
        .all()
    )
@router.post("/{appointment_id}/cancel", response_model=AppointmentOut)
def cancel_appointment(
    appointment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    a = db.get(Appointment, appointment_id)
    if a is None or a.user_id != user.id:  # R6.6
        raise HTTPException(status_code=404, detail="Appointment not found")
    if a.status == "cancelled":  # R6.7
        raise HTTPException(
            status_code=409, detail="Appointment is already cancelled"
        )
    if not can_cancel(a.slot_start):  # R6.2, R6.4
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel within 2 hours of the slot",
        )
    a.status = "cancelled"  # R6.8
    db.commit()
    db.refresh(a)
    return a