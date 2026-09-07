import axios from "axios";

const host = typeof window !== "undefined" && window.location.hostname ? window.location.hostname : "localhost";
export const API_BASE_URL = import.meta.env.VITE_API_URL && !import.meta.env.VITE_API_URL.includes("localhost")
  ? import.meta.env.VITE_API_URL
  : `http://${host}:8000/api/v1`;

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
});

// Global 401 Error Interceptor
const handleAuthError = (error: any) => {
  if (error.response?.status === 401) {
    const pathParts = window.location.pathname.split("/").filter(Boolean);
    const code = pathParts.length > 0 ? pathParts[0] : "";
    if (window.location.pathname.indexOf("/login") === -1) {
      if (code && code !== "login") {
        window.location.href = `/${code}/login`;
      } else {
        window.location.href = "/";
      }
    }
  }
  return Promise.reject(error);
};

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use((res) => res, handleAuthError);
