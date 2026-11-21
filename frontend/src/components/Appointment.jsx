import { useEffect, useState } from "react";
import { bookAppointment, fetchAppointmentSlots, fetchStores } from "../api";

function todayString() {
  return new Date().toLocaleDateString("en-CA"); // YYYY-MM-DD
}

export default function Appointment() {
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
    fetchAppointmentSlots(storeId, day)
      .then((data) => {
        setSlots(data);
        setError("");
      })
      .catch((e) => {
        setSlots([]);
        setError(e.message);
      });
  }, [storeId, day, reload]);

  async function handleBook() {
    setError("");
    setSuccess("");
    try {
      const a = await bookAppointment(Number(storeId), selected);
      setSuccess(
        `Appointment #${a.id} confirmed for ${a.slot_start.slice(0, 10)} at ${a.slot_start.slice(11, 16)}`
      );
      setSelected("");
      setReload((n) => n + 1);
    } catch (e) {
      setError(e.message);
      setReload((n) => n + 1);
    }
  }

  return (
    <div className="reservation" data-testid="appointment">
      <h2>Book a support appointment</h2>

      <div className="filters">
        <label>
          Store
          <select
            data-testid="appt-store-select"
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
            data-testid="appt-date-input"
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
        <div className="error" data-testid="appointment-error">
          {error}
        </div>
      )}
      {success && (
        <div className="success" data-testid="appointment-success">
          {success}
        </div>
      )}

      <div className="slots" data-testid="appt-slot-list">
        {slots.map((s) => {
          const time = s.slot_start.slice(11, 16);
          const isSelected = selected === s.slot_start;
          return (
            <button
              key={s.slot_start}
              type="button"
              data-testid="appt-slot"
              className={isSelected ? "slot selected" : "slot"}
              disabled={!s.available}
              onClick={() => setSelected(s.slot_start)}
            >
              {time}
              <small>{s.remaining === 0 ? "Taken" : "Open"}</small>
            </button>
          );
        })}
      </div>

      <button
        data-testid="book-button"
        disabled={!selected}
        onClick={handleBook}
      >
        Book appointment
      </button>
    </div>
  );
}