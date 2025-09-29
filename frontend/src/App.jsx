import { useState } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Login from "./pages/Login";
import Projects from "./pages/Projects";
import ProjectDetail from "./pages/ProjectDetail";
import ProtectedRoute from "./components/ProtectedRoute";

export default function AppRouter() {
  const [loggedIn, setLoggedIn] = useState(false);

  const handleLogin = () => setLoggedIn(true);
  const handleLogout = () => setLoggedIn(false);

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            loggedIn ? (
              <Navigate to="/projects" replace />
            ) : (
              <Login onLogin={handleLogin} />
            )
          }
        />
        <Route
          path="/projects"
          element={
            <ProtectedRoute loggedIn={loggedIn}>
              <Projects onLogout={handleLogout} />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId"
          element={
            <ProtectedRoute loggedIn={loggedIn}>
              <ProjectDetail onLogout={handleLogout} />
            </ProtectedRoute>
          }
        />
        <Route
          path="*"
          element={<Navigate to={loggedIn ? "/projects" : "/login"} replace />}
        />
      </Routes>
    </Router>
  );
}
