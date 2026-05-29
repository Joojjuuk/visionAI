// Base URL of the VisionAI backend API.
//
// - Empty string (default) = same origin. Used when the backend serves the
//   built frontend itself (local `python run.py`, or the backend host).
// - On Vercel (frontend-only), set the env var VITE_API_URL to your backend's
//   public URL, e.g. https://visionai-api.onrender.com
//
// Vite inlines import.meta.env.* at build time, so VITE_API_URL must be set in
// the Vercel project settings BEFORE the build.
export const API_BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/+$/, "");

/** Prefix a backend-relative path (e.g. "/api/analyze", "/uploads/x.png") with API_BASE. */
export const apiUrl = (path) => `${API_BASE}${path}`;
