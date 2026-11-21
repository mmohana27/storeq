# StoreQ Requirements

## Overview
StoreQ is a retail web app where customers browse products, reserve them
for in-store pickup, and book support appointments.

## Functional Requirements

### R1: Product browse and search
- R1.1 Users can view a list of products (name, category, price, stock).
- R1.2 Users can search products by name (case-insensitive, partial match).
- R1.3 Users can filter by category.
- R1.4 Users can filter by price range (min and max).
- R1.5 If no products match, the message "No products found" is shown.

### R2: Cart
- R2.1 Users can add a product to the cart.
- R2.2 Quantity per product must be between 1 and 5.
- R2.3 Users can update quantity or remove an item.
- R2.4 Cart total is recalculated on every change.
- R2.5 A product with zero stock cannot be added.
- R2.6 The cart belongs to a logged-in user.
- R2.7 Quantity cannot exceed available stock.
### R3: In-store pickup reservation
- R3.1 A logged-in user can reserve cart items for pickup at a chosen store.
- R3.2 Pickup slots are 30 minutes long, from 10:00 to 18:00.
- R3.3 A slot allows a maximum of 3 reservations.
- R3.4 Reserving reduces product stock by the reserved quantity.
- R3.5 A past time slot cannot be selected.
- R3.6 A reservation requires a non-empty cart; a successful reservation empties the cart.
- R3.7 A slot must start on the hour or half hour (10:00, 10:30 ... 17:30).
- R3.8 The 3-reservation limit applies per store, per slot.
### R4: Support appointment booking
- R4.1 A logged-in user can book a support appointment at a chosen store.
- R4.2 Appointment slots are 30 minutes long, from 10:00 to 18:00.
- R4.3 A slot can be booked by only one user (no double booking).
- R4.4 A user can have at most 2 active appointments.
- R4.5 A past time slot cannot be booked.
- R4.6 A slot must start on the hour or half hour (10:00, 10:30 ... 17:30).
- R4.7 The one-booking-per-slot rule applies per store.
### R5: Authentication
- R5.1 Users can sign up with an email and a password.
- R5.2 Email must be valid and unique.
- R5.3 Password must be 8 to 20 characters with at least one uppercase
      letter, one lowercase letter, and one digit.
- R5.4 Users can log in with valid credentials.
- R5.5 After 5 consecutive failed logins, the account is locked for
      15 minutes.

### R6: Reservation and appointment history
- R6.1 Logged-in users can view their reservations and appointments.
- R6.2 A user can cancel a reservation or appointment up to 2 hours
      before the slot.
- R6.3 Cancelling a reservation restores product stock.
- R6.4 Cancellation within 2 hours of the slot is not allowed.
- R6.5 Cancelling exactly 2 hours before the slot is allowed.
- R6.6 A user can only cancel their own bookings (others get "not found").
- R6.7 Cancelling an already cancelled booking is rejected.
- R6.8 A cancelled slot becomes available again.

## Non-Functional Requirements
- NFR1 API responses return in under 500 ms for list endpoints.
- NFR2 The web app works on the latest Chrome, Firefox and Safari.
- NFR3 Pages meet basic accessibility standards (no critical axe
  violations).
- NFR4 Passwords are never stored or returned in plain text.

## Out of Scope
Payments, shipping, admin dashboard, email notifications.