import { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
  Link,
} from "react-router-dom";
import Login from "./pages/Login";
import Projects from "./pages/Projects";
import ProjectDetail from "./pages/ProjectDetail";

function App() {
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
              <Navigate to="/projects/new" />
            )
          }
        />
        <Route
          path="/projects"
          element={loggedIn ? <Projects /> : <Navigate to="/login" />}
        />
        <Route
          path="/projects/:projectId"
          element={loggedIn ? <ProjectDetail /> : <Navigate to="/login" />}
        />
        <Route
          path="*"
          element={<Navigate to={loggedIn ? "/projects" : "/login"} />}
        />
      </Routes>
    </Router>
  );
}

export default App;
