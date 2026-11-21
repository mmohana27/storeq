from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Product
from schemas import ProductOut

router = APIRouter(prefix="/products", tags=["Products"])


@router.get("", response_model=list[ProductOut])
def list_products(
    q: str | None = Query(None, description="Search by name"),
    category: str | None = Query(None),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    db: Session = Depends(get_db),
):
    if (
        min_price is not None
        and max_price is not None
        and min_price > max_price
    ):
        raise HTTPException(
            status_code=400,
            detail="min_price cannot be greater than max_price",
        )

    query = db.query(Product)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))        # R1.2
    if category:
        query = query.filter(Product.category == category)        # R1.3
    if min_price is not None:
        query = query.filter(Product.price >= min_price)          # R1.4
    if max_price is not None:
        query = query.filter(Product.price <= max_price)          # R1.4
    return query.order_by(Product.id).all()


@router.get("/categories", response_model=list[str])
def list_categories(db: Session = Depends(get_db)):
    rows = db.query(Product.category).distinct().order_by(Product.category)
    return [r[0] for r in rows]


@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = db.get(Product, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")
    return product