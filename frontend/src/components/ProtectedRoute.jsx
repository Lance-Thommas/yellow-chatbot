import { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import api from "./api/client";

export default function ProtectedRoute({ children }) {
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await api.get("/check_session/", { withCredentials: true });
        setAuthenticated(res.ok);
      } catch {
        setAuthenticated(false);
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, []);

  if (loading) return <p>Checking authentication...</p>;
  if (!authenticated) return <Navigate to="/login" replace />;
  return children;
}
