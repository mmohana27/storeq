import { useState } from "react";
import { login, signup } from "../api";

export default function AuthForm({ onLoggedIn }) {
  const [mode, setMode] = useState("login"); // "login" or "signup"
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");
    setMessage("");
    try {
      if (mode === "signup") {
        await signup(email, password);
        setMessage("Account created. You can log in now.");
        setMode("login");
        setPassword("");
      } else {
        await login(email, password);
        onLoggedIn();
      }
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <form className="auth-form" onSubmit={handleSubmit} data-testid="auth-form">
      <h2>{mode === "login" ? "Log in" : "Sign up"}</h2>

      {error && (
        <div className="error" data-testid="auth-error">
          {error}
        </div>
      )}
      {message && (
        <div className="success" data-testid="auth-message">
          {message}
        </div>
      )}

      <label>
        Email
        <input
          data-testid="email-input"
          type="text"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
      </label>

      <label>
        Password
        <input
          data-testid="password-input"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
      </label>

      <button type="submit" data-testid="auth-submit">
        {mode === "login" ? "Log in" : "Sign up"}
      </button>

      <button
        type="button"
        className="link-button"
        data-testid="auth-toggle"
        onClick={() => {
          setMode(mode === "login" ? "signup" : "login");
          setError("");
          setMessage("");
        }}
      >
        {mode === "login"
          ? "No account? Sign up"
          : "Have an account? Log in"}
      </button>
    </form>
  );
}