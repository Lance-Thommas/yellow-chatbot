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
import { useState } from "react";

export default function AppRouter() {
  const [loggedIn, setLoggedIn] = useState(false);

  const handleLogin = () => setLoggedIn(true);

  return (
    <Router>
      <Routes>
        <Route
          path="/login"
          element={
            !loggedIn ? (
              <Login onLogin={handleLogin} />
            ) : (
              <Navigate to="/projects" replace />
            )
          }
        />
        <Route
          path="/projects"
          element={
            <ProtectedRoute isAuthenticated={loggedIn}>
              <Projects />
            </ProtectedRoute>
          }
        />
        <Route
          path="/projects/:projectId"
          element={
            <ProtectedRoute isAuthenticated={loggedIn}>
              <ProjectDetail />
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
