const API_BASE_URL =
  window.__DOCOPS_CONFIG__?.API_BASE_URL ||
  import.meta.env.VITE_API_BASE_URL ||
  "/api";

export function createApiClient(auth) {
  async function request(path, options = {}) {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${auth.token}`,
        "X-User-Id": auth.userId,
        "X-User-Email": auth.email,
        "X-User-Name": auth.name,
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      let detail = "Request failed";
      try {
        const payload = await response.json();
        detail = payload.detail || detail;
      } catch {
        detail = response.statusText || detail;
      }
      throw new Error(detail);
    }

    if (response.status === 204) {
      return null;
    }

    return response.json();
  }

  return {
    health: () => request("/health", { method: "GET" }),
    listDocuments: () => request("/documents", { method: "GET" }),
    getDocument: (documentId) => request(`/documents/${documentId}`, { method: "GET" }),
    initUpload: (payload) =>
      request("/documents/init-upload", {
        method: "POST",
        body: JSON.stringify(payload),
      }),
    completeUpload: (documentId) =>
      request("/documents/complete-upload", {
        method: "POST",
        body: JSON.stringify({ document_id: documentId }),
      }),
    getDownloadUrl: (documentId) =>
      request(`/documents/${documentId}/download-url`, {
        method: "GET",
      }),
    deleteDocument: (documentId) =>
      request(`/documents/${documentId}`, {
        method: "DELETE",
      }),
  };
}

export async function uploadFileToPresignedUrl(uploadUrl, file, contentType) {
  const response = await fetch(uploadUrl, {
    method: "PUT",
    body: file,
    headers: {
      "Content-Type": contentType || file.type || "application/octet-stream",
    },
  });

  if (!response.ok) {
    throw new Error("File upload failed");
  }
}
