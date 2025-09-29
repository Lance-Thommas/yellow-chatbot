import { useEffect, useState, useRef } from "react";
import { useParams, Link, useNavigate } from "react-router-dom";
import { marked } from "marked";
import DOMPurify from "dompurify";
import api from "../api/client.js";

export default function ProjectDetail({ onLogout }) {
  const { projectId: paramProjectId } = useParams();
  const navigate = useNavigate();

  const [projects, setProjects] = useState([]);
  const [project, setProject] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [error, setError] = useState("");
  const [isTyping, setIsTyping] = useState(false);
  const [projectId, setProjectId] = useState(
    paramProjectId && paramProjectId !== "new" ? paramProjectId : null
  );
  const [creating, setCreating] = useState(false);

  const messagesEndRef = useRef(null);
  const eventSourceRef = useRef(null);

  const scrollToBottom = () =>
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  useEffect(scrollToBottom, [messages, isTyping]);

  useEffect(() => {
    return () => {
      if (eventSourceRef.current) {
        try {
          eventSourceRef.current.close();
        } catch {}
      }
    };
  }, []);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const data = await api.get("/projects/");
        setProjects(data.data || data);
      } catch (err) {
        console.error(err);
        setError("Failed to load projects");
      }
    };
    fetchProjects();
  }, []);

  useEffect(() => {
    if (!projectId) return;
    const fetchProject = async () => {
      try {
        const data = await api.get(`/projects/${projectId}`);
        setProject(data.data || data);
      } catch (err) {
        setError(err.message);
      }
    };
    fetchProject();
  }, [projectId]);

  useEffect(() => {
    if (!projectId) return;
    const fetchMessages = async () => {
      try {
        const data = await api.get(`/projects/${projectId}/messages`);
        setMessages(data.data || data);
      } catch (err) {
        console.error(err);
        setMessages([]);
      }
    };
    fetchMessages();
  }, [projectId]);

  const createNewProject = async () => {
    if (creating) return;
    setCreating(true);

    try {
      const tempName = `New Conversation ${Date.now()}`;
      const newProject = await api.post("/projects/", {
        name: tempName,
        description: "Auto-created conversation",
      });
      const projectData = newProject.data || newProject;

      setProject(projectData);
      setProjects((prev) => [...prev, projectData]);
      setProjectId(projectData.id);
      navigate(`/projects/${projectData.id}`, { replace: true });

      return projectData.id;
    } catch (err) {
      console.error(err);
      return null;
    } finally {
      setCreating(false);
    }
  };

  const handleSend = async () => {
    if (!input.trim()) return;

    if (eventSourceRef.current) {
      try {
        eventSourceRef.current.close();
      } catch {}
      eventSourceRef.current = null;
    }

    let currentProjectId = projectId;
    let isFirstMessage = false;

    if (!currentProjectId) {
      const newId = await createNewProject();
      if (!newId) return;
      currentProjectId = newId;
      isFirstMessage = true;
    } else if (project && project.name.startsWith("New Conversation")) {
      isFirstMessage = true;
    }

    const userMessage = {
      role: "user",
      content: input,
      id: crypto.randomUUID(),
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsTyping(true);

    const assistantMessageId = crypto.randomUUID();
    setMessages((prev) => [
      ...prev,
      { role: "assistant", content: "", id: assistantMessageId },
    ]);

    const evtSource = new EventSource(
      `${
        api.defaults.baseURL
      }/projects/${currentProjectId}/messages/stream?content=${encodeURIComponent(
        userMessage.content
      )}`,
      { withCredentials: true }
    );

    eventSourceRef.current = evtSource;

    evtSource.onmessage = (e) => {
      try {
        const data = JSON.parse(e.data);
        if (data.delta) {
          setMessages((prev) => {
            const idx = prev.findIndex((m) => m.id === assistantMessageId);
            if (idx === -1) {
              return [
                ...prev,
                {
                  id: assistantMessageId,
                  role: "assistant",
                  content: data.delta,
                },
              ];
            }
            const updated = [...prev];
            updated[idx] = {
              ...updated[idx],
              content: (updated[idx].content || "") + data.delta,
            };
            return updated;
          });
        } else if (data.content) {
          setMessages((prev) =>
            prev.map((m) =>
              m.id === assistantMessageId ? { ...m, content: data.content } : m
            )
          );
        }
      } catch (err) {
        console.error("Failed to parse SSE chunk", err);
      }
    };

    evtSource.onerror = () => {
      try {
        evtSource.close();
      } catch {}
      setIsTyping(false);
      eventSourceRef.current = null;
    };

    evtSource.addEventListener("end", async () => {
      try {
        evtSource.close();
      } catch {}
      setIsTyping(false);
      eventSourceRef.current = null;

      if (isFirstMessage) {
        const assistantContent =
          messages.find((m) => m.id === assistantMessageId)?.content || "";

        try {
          const updated = await api.post(
            `/projects/${currentProjectId}/generate_name`,
            {
              messages: [
                { role: "user", content: userMessage.content },
                { role: "assistant", content: assistantContent },
              ],
            }
          );
          const data = updated.data || updated;
          setProject((prev) => ({ ...prev, name: data.name }));
          setProjects((prev) =>
            prev.map((p) => (p.id === data.id ? { ...p, name: data.name } : p))
          );
        } catch (err) {
          console.error("Failed to generate project name:", err);
        }
      }
    });
  };

  const handleLogoutClick = async () => {
    // Stop SSE if active
    if (eventSourceRef.current) {
      try {
        eventSourceRef.current.close();
      } catch {}
      eventSourceRef.current = null;
    }

    // Reset UI state immediately so component stops trying to fetch
    setProjects([]);
    setProject(null);
    setMessages([]);
    setInput("");
    setError("");

    try {
      await api.post("/logout/");
    } catch (err) {
      console.error("Logout failed", err);
    }

    // Now navigate after cleanup
    navigate("/login", { replace: true });
  };

  if (error) return <p style={{ color: "red" }}>{error}</p>;

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
          width: "75%",
          maxWidth: "1000px",
          maxHeight: "85vh",
          backgroundColor: "rgba(145, 145, 145, 0.4)",
          borderRadius: "16px",
          padding: "20px",
          overflowY: "auto",
          display: "flex",
          gap: "20px",
          boxShadow: "0 8px 24px rgba(146, 146, 146, 0.30)",
        }}
      >
        <div
          style={{
            width: "250px",
            borderRight: "1px solid #ccc",
            paddingRight: "10px",
          }}
        >
          <div style={{ display: "flex", justifyContent: "space-between" }}>
            <h3>Your Projects</h3>
            <button onClick={handleLogoutClick}>Logout</button>
          </div>
          <ul>
            {projects.map((p) => (
              <li key={p.id} style={{ marginBottom: "8px" }}>
                <Link
                  to={`/projects/${p.id}`}
                  onClick={() => setProjectId(p.id)}
                  style={{
                    textDecoration: "none",
                    color:
                      p.id === projectId
                        ? "rgba(255, 255, 255, 0.75)"
                        : "black",
                  }}
                >
                  {p.name}
                </Link>
              </li>
            ))}
          </ul>
          <button
            onClick={createNewProject}
            disabled={creating}
            style={{
              marginTop: "10px",
              width: "100%",
              opacity: creating ? 0.6 : 1,
            }}
          >
            {creating ? "Creating..." : "+ Create New Project"}
          </button>
        </div>

        <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
          <h2>{project ? project.name : "New Conversation"}</h2>
          <div
            style={{
              border: "1px solid gray",
              padding: "10px",
              height: "400px",
              overflowY: "auto",
              marginBottom: "10px",
            }}
          >
            {messages.length === 0 && !isTyping && (
              <p style={{ fontStyle: "italic", color: "#242424ff" }}>
                What are you working on today?
              </p>
            )}
            {messages.map((m) => (
              <div
                key={m.id}
                style={{
                  textAlign: m.role === "user" ? "right" : "left",
                  margin: "5px 0",
                }}
              >
                <strong>{m.role === "user" ? "You" : "Assistant"}:</strong>
                <div
                  dangerouslySetInnerHTML={{
                    __html: DOMPurify.sanitize(marked.parse(m.content || "")),
                  }}
                />
              </div>
            ))}
            {isTyping && (
              <p style={{ fontStyle: "italic" }}>Assistant is typing...</p>
            )}
            <div ref={messagesEndRef} />
          </div>

          <div style={{ display: "flex", gap: "10px" }}>
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
              style={{
                flex: 1,
                padding: "8px",
                backgroundColor: "rgba(66, 66, 66, 1.0)",
              }}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />
            <button onClick={handleSend} style={{ padding: "8px 16px" }}>
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
