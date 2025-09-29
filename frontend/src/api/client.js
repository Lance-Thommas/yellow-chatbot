import axios from "axios";

// Create a reusable axios instance
const api = axios.create({
  baseURL: "https://yellow-chatbot.onrender.com/api", // Render backend URL
  withCredentials: true, // include cookies if needed
});

export default api;
