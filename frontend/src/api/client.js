import axios from "axios";

// Create a reusable axios instance
const api = axios.create({
  baseURL: "http://localhost:8000", // FastAPI backend URL
  withCredentials: true, // include cookies if needed
});

export default api;
