import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  useNavigate,
} from "react-router-dom";
import Login from "./pages/Login";
import Projects from "./pages/Projects";
import ProjectDetail from "./pages/ProjectDetail";
import ProtectedRoute from "./components/ProtectedRoute";

function AppWrapper() {
  const navigate = useNavigate();

  const handleLogin = () => {
    navigate("/projects");
  };

  return <App onLogin={handleLogin} />;
}

function App({ onLogin }) {
  return (
    <Routes>
      <Route path="/login" element={<Login onLogin={onLogin} />} />
      <Route
        path="/projects"
        element={
          <ProtectedRoute>
            <Projects />
          </ProtectedRoute>
        }
      />
      <Route
        path="/projects/:projectId"
        element={
          <ProtectedRoute>
            <ProjectDetail />
          </ProtectedRoute>
        }
      />
      <Route path="*" element={<Navigate to="/projects" replace />} />
    </Routes>
  );
}

export default function AppRouter() {
  return (
    <Router>
      <AppWrapper />
    </Router>
  );
}
