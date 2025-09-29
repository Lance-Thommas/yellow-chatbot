import { useState } from "react";
import api from "../api/client.js";

export default function Login({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true); // toggle login/register
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      if (!isLogin) {
        await api.post("/users/", { email, password });
      }

      await api.post("/login/", { email, password });

      // Navigate after login/register
      onLogin();
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "auto", marginTop: "100px" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-around",
          marginBottom: "1rem",
        }}
      >
        <button
          onClick={() => {
            setIsLogin(true);
            setError("");
          }}
          style={{ fontWeight: isLogin ? "bold" : "normal" }}
        >
          Login
        </button>
        <button
          onClick={() => {
            setIsLogin(false);
            setError("");
          }}
          style={{ fontWeight: !isLogin ? "bold" : "normal" }}
        >
          Register
        </button>
      </div>

      <form onSubmit={handleSubmit}>
        <h2>{isLogin ? "Login" : "Register"}</h2>
        {error && <p style={{ color: "red" }}>{error}</p>}

        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />

        <button type="submit" disabled={loading}>
          {loading
            ? isLogin
              ? "Logging in..."
              : "Registering..."
            : isLogin
            ? "Login"
            : "Register & Login"}
        </button>
      </form>
    </div>
  );
}
