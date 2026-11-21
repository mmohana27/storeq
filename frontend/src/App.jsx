import { useEffect, useState } from "react";
import {
  addToCart,
  fetchCart,
  fetchCategories,
  fetchMe,
  fetchProducts,
  logout,
  removeCartItem,
  updateCartItem,
} from "./api";
import Appointment from "./components/Appointment";
import AuthForm from "./components/AuthForm";
import Cart from "./components/Cart";
import Reservation from "./components/Reservation";
import "./App.css";

function stockLabel(stock) {
  if (stock === 0) return <span className="stock-out">Out of stock</span>;
  if (stock <= 5)
    return <span className="stock-low">Only {stock} left</span>;
  return <span className="stock-ok">In stock</span>;
}

export default function App() {
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [q, setQ] = useState("");
  const [category, setCategory] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const [user, setUser] = useState(null);
  const [showAuth, setShowAuth] = useState(false);
  const [cart, setCart] = useState({ items: [], total: 0 });
  const [cartError, setCartError] = useState("");
  const [refreshKey, setRefreshKey] = useState(0);

  function loadCart() {
    fetchCart()
      .then(setCart)
      .catch(() => setCart({ items: [], total: 0 }));
  }

  function loadUser() {
    fetchMe()
      .then((u) => {
        setUser(u);
        loadCart();
      })
      .catch(() => setUser(null));
  }

  async function cartAction(action) {
    setCartError("");
    try {
      setCart(await action());
    } catch (e) {
      setCartError(e.message);
    }
  }

  function handleAdd(productId) {
    if (!user) {
      setCartError("Please log in to add items to your cart");
      return;
    }
    cartAction(() => addToCart(productId, 1));
  }

  useEffect(() => {
    if (localStorage.getItem("token")) loadUser();
  }, []);

  useEffect(() => {
    fetchCategories()
      .then(setCategories)
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchProducts({ q, category, minPrice, maxPrice })
      .then((data) => {
        setProducts(data);
        setError("");
      })
      .catch((e) => {
        setProducts([]);
        setError(e.message);
      })
      .finally(() => setLoading(false));
  }, [q, category, minPrice, maxPrice, refreshKey]);

  return (
    <div className="container">
      <div className="header">
        <h1>StoreQ</h1>
        <div>
          {user ? (
            <>
              <span data-testid="user-email">{user.email}</span>
              <button
                data-testid="logout-button"
                onClick={() => {
                  logout();
                  setUser(null);
                  setCart({ items: [], total: 0 });
                  setCartError("");
                }}
              >
                Log out
              </button>
            </>
          ) : (
            <button
              data-testid="login-button"
              onClick={() => setShowAuth(!showAuth)}
            >
              Log in / Sign up
            </button>
          )}
        </div>
      </div>

      {!user && showAuth && (
        <AuthForm
          onLoggedIn={() => {
            loadUser();
            setShowAuth(false);
          }}
        />
      )}

      {user && (
        <Cart
          cart={cart}
          onUpdate={(id, qty) => cartAction(() => updateCartItem(id, qty))}
          onRemove={(id) => cartAction(() => removeCartItem(id))}
        />
      )}

      {cartError && (
        <div className="error" data-testid="cart-error">
          {cartError}
        </div>
      )}

      {user && (
        <Reservation
          cartCount={cart.items.length}
          onReserved={() => {
            loadCart();
            setRefreshKey((k) => k + 1);
          }}
        />
      )}

      {user && <Appointment />}

      <div className="filters">
        <label>
          Search
          <input
            data-testid="search-input"
            placeholder="Search products"
            value={q}
            onChange={(e) => setQ(e.target.value)}
          />
        </label>

        <label>
          Category
          <select
            data-testid="category-select"
            value={category}
            onChange={(e) => setCategory(e.target.value)}
          >
            <option value="">All</option>
            {categories.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>

        <label>
          Min price
          <input
            data-testid="min-price"
            type="number"
            min="0"
            value={minPrice}
            onChange={(e) => setMinPrice(e.target.value)}
          />
        </label>

        <label>
          Max price
          <input
            data-testid="max-price"
            type="number"
            min="0"
            value={maxPrice}
            onChange={(e) => setMaxPrice(e.target.value)}
          />
        </label>
      </div>

      {error && (
        <div className="error" data-testid="error-message">
          {error}
        </div>
      )}

      {!loading && !error && products.length === 0 && (
        <div className="empty" data-testid="no-products">
          No products found
        </div>
      )}

      <div className="grid" data-testid="product-grid">
        {products.map((p) => (
          <div className="card" key={p.id} data-testid="product-card">
            <h3>{p.name}</h3>
            <div className="category">{p.category}</div>
            <div className="price">₹{p.price.toFixed(2)}</div>
            {stockLabel(p.stock)}
            <div>
              <button
                className="add-button"
                data-testid="add-to-cart"
                disabled={p.stock === 0}
                onClick={() => handleAdd(p.id)}
              >
                Add to cart
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}