import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { createApiClient } from "../api";
import { useAuth } from "../components/auth";
import StatusBadge from "../components/StatusBadge";

export default function DocumentDetailsPage() {
  const { documentId } = useParams();
  const auth = useAuth();
  const api = useMemo(() => createApiClient(auth), [auth]);
  const navigate = useNavigate();

  const [document, setDocument] = useState(null);
  const [error, setError] = useState("");
  const [busyAction, setBusyAction] = useState("");

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const payload = await api.getDocument(documentId);
        if (active) {
          setDocument(payload);
          setError("");
        }
      } catch (loadError) {
        if (active) {
          setError(loadError.message);
        }
      }
    }

    load();
    const intervalId = window.setInterval(load, 4000);
    return () => {
      active = false;
      window.clearInterval(intervalId);
    };
  }, [api, documentId]);

  async function handleDownload() {
    setBusyAction("download");
    try {
      const payload = await api.getDownloadUrl(documentId);
      window.open(payload.download_url, "_blank", "noopener,noreferrer");
    } catch (downloadError) {
      setError(downloadError.message);
    } finally {
      setBusyAction("");
    }
  }

  async function handleDelete() {
    setBusyAction("delete");
    try {
      await api.deleteDocument(documentId);
      navigate("/documents");
    } catch (deleteError) {
      setError(deleteError.message);
      setBusyAction("");
    }
  }

  if (!document && !error) {
    return <p className="muted">Loading document...</p>;
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <Link to="/documents" className="back-link">
            Back to documents
          </Link>
          <h2>{document?.filename || "Document"}</h2>
        </div>
        {document ? <StatusBadge status={document.status} /> : null}
      </div>

      {error && <div className="alert alert-error">{error}</div>}

      {document ? (
        <>
          <div className="details-grid">
            <div className="detail-card">
              <span className="muted">Document ID</span>
              <strong>{document.id}</strong>
            </div>
            <div className="detail-card">
              <span className="muted">Type</span>
              <strong>{document.content_type}</strong>
            </div>
            <div className="detail-card">
              <span className="muted">Size</span>
              <strong>{Math.ceil(document.size_bytes / 1024)} KB</strong>
            </div>
            <div className="detail-card">
              <span className="muted">Updated</span>
              <strong>{new Date(document.updated_at).toLocaleString()}</strong>
            </div>
          </div>

          <div className="actions-row">
            <button
              className="button"
              onClick={handleDownload}
              disabled={busyAction !== "" || document.status !== "COMPLETED"}
            >
              {busyAction === "download" ? "Preparing..." : "Download"}
            </button>
            <button
              className="button button-danger"
              onClick={handleDelete}
              disabled={busyAction !== ""}
            >
              {busyAction === "delete" ? "Deleting..." : "Delete"}
            </button>
          </div>

          <div className="result-section">
            <h3>Summary</h3>
            <p>{document.result_payload?.summary || "Processing has not produced a summary yet."}</p>
          </div>

          <div className="result-section">
            <h3>Extracted metadata</h3>
            <pre>{JSON.stringify(document.result_payload || {}, null, 2)}</pre>
          </div>

          <div className="result-section">
            <h3>Extracted text</h3>
            <pre>{document.extracted_text || "No extracted text available yet."}</pre>
          </div>

          {document.error_message ? (
            <div className="result-section">
              <h3>Error</h3>
              <pre>{document.error_message}</pre>
            </div>
          ) : null}
        </>
      ) : null}
    </section>
  );
}
