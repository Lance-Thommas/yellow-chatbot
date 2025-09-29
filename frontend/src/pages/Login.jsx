import { useState } from "react";
import api from "./client";

export default function Auth({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true); // toggle login/register
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    try {
      if (!isLogin) {
        const registerRes = await api.post("/users/", { email, password });
      }

      const loginRes = await api.post("/login/", { email, password });

      onLogin("cookie"); // notify App.jsx
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    }
  };

  return (
    <div style={{ maxWidth: "400px", margin: "auto" }}>
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
        <button type="submit">{isLogin ? "Login" : "Register & Login"}</button>
      </form>
    </div>
  );
}
