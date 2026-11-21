from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models import CartItem, Product, User
from schemas import CartItemIn, CartItemUpdate, CartLineOut, CartOut

router = APIRouter(prefix="/cart", tags=["Cart"])

MAX_QTY = 5


def build_cart(db: Session, user: User) -> CartOut:
    items = (
        db.query(CartItem)
        .filter(CartItem.user_id == user.id)
        .order_by(CartItem.id)
        .all()
    )
    lines = [
        CartLineOut(
            product_id=i.product_id,
            name=i.product.name,
            price=i.product.price,
            quantity=i.quantity,
            line_total=round(i.product.price * i.quantity, 2),
        )
        for i in items
    ]
    total = round(sum(line.line_total for line in lines), 2)  # R2.4
    return CartOut(items=lines, total=total)


@router.get("", response_model=CartOut)
def view_cart(
    user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    return build_cart(db, user)


@router.post("/items", response_model=CartOut, status_code=201)
def add_item(
    data: CartItemIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    product = db.get(Product, data.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    if product.stock == 0:  # R2.5
        raise HTTPException(status_code=400, detail="Product is out of stock")

    existing = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user.id,
            CartItem.product_id == data.product_id,
        )
        .first()
    )
    new_qty = data.quantity + (existing.quantity if existing else 0)
    if new_qty > MAX_QTY:  # R2.2
        raise HTTPException(
            status_code=400, detail="Maximum 5 per product in the cart"
        )
    if new_qty > product.stock:  # R2.7
        raise HTTPException(
            status_code=400, detail="Quantity exceeds available stock"
        )

    if existing:
        existing.quantity = new_qty
    else:
        db.add(CartItem(
            user_id=user.id, product_id=data.product_id, quantity=new_qty
        ))
    db.commit()
    return build_cart(db, user)


@router.patch("/items/{product_id}", response_model=CartOut)
def update_item(
    product_id: int,
    data: CartItemUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user.id, CartItem.product_id == product_id
        )
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Item not in cart")
    if data.quantity > item.product.stock:  # R2.7
        raise HTTPException(
            status_code=400, detail="Quantity exceeds available stock"
        )
    item.quantity = data.quantity  # R2.3
    db.commit()
    return build_cart(db, user)


@router.delete("/items/{product_id}", response_model=CartOut)
def remove_item(
    product_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    item = (
        db.query(CartItem)
        .filter(
            CartItem.user_id == user.id, CartItem.product_id == product_id
        )
        .first()
    )
    if item is None:
        raise HTTPException(status_code=404, detail="Item not in cart")
    db.delete(item)  # R2.3
    db.commit()
    return build_cart(db, user)