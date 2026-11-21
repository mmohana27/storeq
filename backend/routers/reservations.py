from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import (
    CartItem, Reservation, ReservationItem, Store, User,
)
from schemas import ReservationIn, ReservationOut, SlotOut
from rules import can_cancel
router = APIRouter(prefix="/reservations", tags=["Reservations"])

OPEN_HOUR = 10
CLOSE_HOUR = 18
MAX_PER_SLOT = 3


def is_valid_slot(dt: datetime) -> bool:  # R3.2, R3.7
    return (
        dt.minute in (0, 30)
        and dt.second == 0
        and dt.microsecond == 0
        and OPEN_HOUR <= dt.hour < CLOSE_HOUR
    )


def count_active(db: Session, store_id: int, slot: datetime) -> int:
    return (
        db.query(Reservation)
        .filter(
            Reservation.store_id == store_id,
            Reservation.slot_start == slot,
            Reservation.status == "active",
        )
        .count()
    )


def to_out(r: Reservation) -> ReservationOut:
    return ReservationOut(
        id=r.id,
        store_id=r.store_id,
        slot_start=r.slot_start,
        status=r.status,
        items=[
            {
                "product_id": i.product_id,
                "name": i.product.name,
                "quantity": i.quantity,
            }
            for i in r.items
        ],
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
        used = count_active(db, store_id, current)
        remaining = max(0, MAX_PER_SLOT - used)
        slots.append(SlotOut(
            slot_start=current,
            available=remaining > 0 and current > now,
            remaining=remaining,
        ))
        current += timedelta(minutes=30)
    return slots


@router.post("", response_model=ReservationOut, status_code=201)
def create_reservation(
    data: ReservationIn,
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
    if not is_valid_slot(slot):  # R3.2, R3.7
        raise HTTPException(
            status_code=400,
            detail="Slot must be 10:00 to 17:30 on the hour or half hour",
        )
    if slot <= datetime.now():  # R3.5
        raise HTTPException(
            status_code=400, detail="Cannot reserve a past time slot"
        )

    cart = db.query(CartItem).filter(CartItem.user_id == user.id).all()
    if not cart:  # R3.6
        raise HTTPException(status_code=400, detail="Cart is empty")

    if count_active(db, data.store_id, slot) >= MAX_PER_SLOT:  # R3.3
        raise HTTPException(status_code=409, detail="Slot is full")

    for item in cart:
        if item.quantity > item.product.stock:
            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for {item.product.name}",
            )

    reservation = Reservation(
        user_id=user.id, store_id=data.store_id, slot_start=slot
    )
    for item in cart:
        reservation.items.append(
            ReservationItem(
                product_id=item.product_id, quantity=item.quantity
            )
        )
        item.product.stock -= item.quantity  # R3.4
        db.delete(item)  # R3.6
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return to_out(reservation)


@router.get("", response_model=list[ReservationOut])
def my_reservations(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    rows = (
        db.query(Reservation)
        .filter(Reservation.user_id == user.id)
        .order_by(Reservation.slot_start)
        .all()
    )
    return [to_out(r) for r in rows]
@router.post("/{reservation_id}/cancel", response_model=ReservationOut)
def cancel_reservation(
    reservation_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    r = db.get(Reservation, reservation_id)
    if r is None or r.user_id != user.id:  # R6.6
        raise HTTPException(status_code=404, detail="Reservation not found")
    if r.status == "cancelled":  # R6.7
        raise HTTPException(
            status_code=409, detail="Reservation is already cancelled"
        )
    if not can_cancel(r.slot_start):  # R6.2, R6.4
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel within 2 hours of the slot",
        )
    for item in r.items:
        item.product.stock += item.quantity  # R6.3
    r.status = "cancelled"  # R6.8: slot count only uses active bookings
    db.commit()
    db.refresh(r)
    return to_out(r)