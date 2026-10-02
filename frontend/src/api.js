// In local dev, Vite's proxy (see vite.config.js) forwards "/api" to the
// backend, so an empty base URL works. Once deployed, set VITE_API_BASE_URL
// in your frontend hosting env (e.g. Vercel) to your backend's public URL,
// such as https://krishi-sahayak-backend.onrender.com
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

async function handleResponse(res) {
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `Request failed with status ${res.status}`);
  }
  return res.json();
}

export async function sendTextQuery(teluguText) {
  const res = await fetch(`${API_BASE_URL}/api/text-query`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ telugu_text: teluguText }),
  });
  return handleResponse(res);
}

export async function sendVoiceQuery(audioBlob) {
  const formData = new FormData();
  formData.append("audio", audioBlob, "recording.webm");

  const res = await fetch(`${API_BASE_URL}/api/voice-query`, {
    method: "POST",
    body: formData,
  });
  return handleResponse(res);
}
