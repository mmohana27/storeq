from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import (
    appointments, auth, cart, products, reservations, stores,
)

app = FastAPI(title="StoreQ API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(auth.router)
app.include_router(cart.router)
app.include_router(reservations.router)
app.include_router(appointments.router)
app.include_router(stores.router)


@app.get("/health")
def health():
    return {"status": "ok"}