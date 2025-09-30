import { useState } from "react";
import api from "../api/client.js";

export default function Login({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
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
      onLogin();
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "100vw",
        height: "100vh",
        display: "flex",
        justifyContent: "center",
        alignItems: "center",
        backgroundColor: "rgba(43, 43, 43, 0.8)",
        backdropFilter: "blur(16px)",
        zIndex: 9999,
      }}
    >
      <div
        style={{
          width: "90%",
          maxWidth: "400px",
          backgroundColor: "rgba(145, 145, 145, 0.4)",
          borderRadius: "16px",
          padding: "30px",
          display: "flex",
          flexDirection: "column",
          gap: "20px",
          boxShadow: "0 8px 24px rgba(146, 146, 146, 0.30)",
        }}
      >
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
            style={{
              fontWeight: isLogin ? "bold" : "normal",
              padding: "8px 12px",
            }}
          >
            Login
          </button>
          <button
            onClick={() => {
              setIsLogin(false);
              setError("");
            }}
            style={{
              fontWeight: !isLogin ? "bold" : "normal",
              padding: "8px 12px",
            }}
          >
            Register
          </button>
        </div>

        <form
          onSubmit={handleSubmit}
          style={{ display: "flex", flexDirection: "column", gap: "15px" }}
        >
          <h2 style={{ textAlign: "center" }}>
            {isLogin ? "Login" : "Register"}
          </h2>

          {error && (
            <p style={{ color: "red", textAlign: "center" }}>{error}</p>
          )}

          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            style={{
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid #999",
              backgroundColor: "rgba(66, 66, 66, 1.0)",
              color: "white",
            }}
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            style={{
              padding: "10px",
              borderRadius: "8px",
              border: "1px solid #999",
              backgroundColor: "rgba(66, 66, 66, 1.0)",
              color: "white",
            }}
          />

          <button
            type="submit"
            disabled={loading}
            style={{
              padding: "10px",
              borderRadius: "8px",
              backgroundColor: "#4f46e5",
              color: "white",
              fontWeight: "bold",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.6 : 1,
            }}
          >
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
    </div>
  );
}
