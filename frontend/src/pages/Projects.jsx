import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import api from "./client";

export default function Projects() {
  const [projects, setProjects] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await api.get("/projects/");
        setProjects(data.data || data);
      } catch (err) {
        setError(err.response?.data?.detail || err.message);
      }
    };
    fetchProjects();
  }, []);

  if (error) return <p style={{ color: "red" }}>{error}</p>;
  if (!projects.length) return <p>Loading projects...</p>;

  return (
    <div style={{ maxWidth: "600px", margin: "0 auto", padding: "20px" }}>
      <h2>Your Projects</h2>
      <ul>
        {projects.map((p) => (
          <li key={p.id} style={{ marginBottom: "10px" }}>
            <Link to={`/projects/${p.id}`} style={{ textDecoration: "none" }}>
              {p.name}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
