import { useState } from "react";

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
        // Register first
        const registerRes = await fetch("/api/users/", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
          credentials: "include",
        });

        if (!registerRes.ok) {
          const data = await registerRes.json();
          throw new Error(data.detail || "Registration failed");
        }
      }

      // Login
      const loginRes = await fetch("/api/login/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
        credentials: "include",
      });

      if (!loginRes.ok) {
        const data = await loginRes.json();
        throw new Error(data.detail || "Login failed");
      }

      onLogin("cookie"); // notify App.jsx
    } catch (err) {
      setError(err.message);
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
