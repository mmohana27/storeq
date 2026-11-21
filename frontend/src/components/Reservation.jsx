import { useEffect, useState } from "react";
import { createReservation, fetchSlots, fetchStores } from "../api";

function todayString() {
  return new Date().toLocaleDateString("en-CA"); // YYYY-MM-DD
}

export default function Reservation({ cartCount, onReserved }) {
  const [stores, setStores] = useState([]);
  const [storeId, setStoreId] = useState("");
  const [day, setDay] = useState(todayString());
  const [slots, setSlots] = useState([]);
  const [selected, setSelected] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [reload, setReload] = useState(0);

  useEffect(() => {
    fetchStores()
      .then((list) => {
        setStores(list);
        if (list.length > 0) setStoreId(String(list[0].id));
      })
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    if (!storeId || !day) {
      setSlots([]);
      return;
    }
    fetchSlots(storeId, day)
      .then((data) => {
        setSlots(data);
        setError("");
      })
      .catch((e) => {
        setSlots([]);
        setError(e.message);
      });
  }, [storeId, day, reload]);

  async function handleReserve() {
    setError("");
    setSuccess("");
    try {
      const r = await createReservation(Number(storeId), selected);
      setSuccess(
        `Reservation #${r.id} confirmed for ${r.slot_start.slice(0, 10)} at ${r.slot_start.slice(11, 16)}`
      );
      setSelected("");
      setReload((n) => n + 1);
      onReserved();
    } catch (e) {
      setError(e.message);
      setReload((n) => n + 1);
    }
  }

  return (
    <div className="reservation" data-testid="reservation">
      <h2>Reserve for in-store pickup</h2>

      <div className="filters">
        <label>
          Store
          <select
            data-testid="store-select"
            value={storeId}
            onChange={(e) => {
              setStoreId(e.target.value);
              setSelected("");
              setSuccess("");
            }}
          >
            {stores.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name} ({s.city})
              </option>
            ))}
          </select>
        </label>

        <label>
          Date
          <input
            data-testid="date-input"
            type="date"
            min={todayString()}
            value={day}
            onChange={(e) => {
              setDay(e.target.value);
              setSelected("");
              setSuccess("");
            }}
          />
        </label>
      </div>

      {error && (
        <div className="error" data-testid="reservation-error">
          {error}
        </div>
      )}
      {success && (
        <div className="success" data-testid="reservation-success">
          {success}
        </div>
      )}

      <div className="slots" data-testid="slot-list">
        {slots.map((s) => {
          const time = s.slot_start.slice(11, 16);
          const isSelected = selected === s.slot_start;
          return (
            <button
              key={s.slot_start}
              type="button"
              data-testid="slot"
              className={isSelected ? "slot selected" : "slot"}
              disabled={!s.available}
              onClick={() => setSelected(s.slot_start)}
            >
              {time}
              <small>{s.remaining === 0 ? "Full" : `${s.remaining} left`}</small>
            </button>
          );
        })}
      </div>

      {cartCount === 0 && (
        <div className="empty" data-testid="reservation-empty-cart">
          Add items to your cart first
        </div>
      )}

      <button
        data-testid="reserve-button"
        disabled={!selected || cartCount === 0}
        onClick={handleReserve}
      >
        Reserve
      </button>
    </div>
  );
}