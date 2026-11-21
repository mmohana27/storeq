const API_URL = "http://127.0.0.1:8000";

function authHeaders() {
  const token = localStorage.getItem("token");
  return token ? { Authorization: `Bearer ${token}` } : {};
}

async function readError(res) {
  const body = await res.json().catch(() => ({}));
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail) && body.detail.length > 0) {
    // FastAPI validation errors: show the first message
    return body.detail[0].msg.replace(/^Value error, /, "");
  }
  return "Something went wrong";
}

// ---------- Products ----------

export async function fetchProducts({ q, category, minPrice, maxPrice }) {
  const params = new URLSearchParams();
  if (q) params.set("q", q);
  if (category) params.set("category", category);
  if (minPrice !== "") params.set("min_price", minPrice);
  if (maxPrice !== "") params.set("max_price", maxPrice);

  const res = await fetch(`${API_URL}/products?${params}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    const detail =
      typeof body.detail === "string" ? body.detail : "Invalid filter values";
    throw new Error(detail);
  }
  return res.json();
}

export async function fetchCategories() {
  const res = await fetch(`${API_URL}/products/categories`);
  if (!res.ok) throw new Error("Could not load categories");
  return res.json();
}

// ---------- Auth ----------

export async function signup(email, password) {
  const res = await fetch(`${API_URL}/auth/signup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function login(email, password) {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });
  if (!res.ok) throw new Error(await readError(res));
  const data = await res.json();
  localStorage.setItem("token", data.access_token);
  return data;
}

export function logout() {
  localStorage.removeItem("token");
}

export async function fetchMe() {
  const res = await fetch(`${API_URL}/auth/me`, { headers: authHeaders() });
  if (!res.ok) throw new Error("Not logged in");
  return res.json();
}

// ---------- Cart ----------

export async function fetchCart() {
  const res = await fetch(`${API_URL}/cart`, { headers: authHeaders() });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function addToCart(productId, quantity = 1) {
  const res = await fetch(`${API_URL}/cart/items`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ product_id: productId, quantity }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function updateCartItem(productId, quantity) {
  const res = await fetch(`${API_URL}/cart/items/${productId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ quantity }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function removeCartItem(productId) {
  const res = await fetch(`${API_URL}/cart/items/${productId}`, {
    method: "DELETE",
    headers: authHeaders(),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// ---------- Stores and pickup reservations ----------

export async function fetchStores() {
  const res = await fetch(`${API_URL}/stores`);
  if (!res.ok) throw new Error("Could not load stores");
  return res.json();
}

export async function fetchSlots(storeId, day) {
  const res = await fetch(
    `${API_URL}/reservations/slots?store_id=${storeId}&day=${day}`
  );
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function createReservation(storeId, slotStart) {
  const res = await fetch(`${API_URL}/reservations`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ store_id: storeId, slot_start: slotStart }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

// ---------- Support appointments ----------

export async function fetchAppointmentSlots(storeId, day) {
  const res = await fetch(
    `${API_URL}/appointments/slots?store_id=${storeId}&day=${day}`
  );
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}

export async function bookAppointment(storeId, slotStart) {
  const res = await fetch(`${API_URL}/appointments`, {
    method: "POST",
    headers: { "Content-Type": "application/json", ...authHeaders() },
    body: JSON.stringify({ store_id: storeId, slot_start: slotStart }),
  });
  if (!res.ok) throw new Error(await readError(res));
  return res.json();
}