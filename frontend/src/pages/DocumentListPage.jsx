import { useEffect, useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { createApiClient } from "../api";
import { useAuth } from "../components/auth";
import StatusBadge from "../components/StatusBadge";

export default function DocumentListPage() {
  const auth = useAuth();
  const api = useMemo(() => createApiClient(auth), [auth]);

  const [documents, setDocuments] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let active = true;

    async function load() {
      try {
        const payload = await api.listDocuments();
        if (active) {
          setDocuments(payload);
          setError("");
        }
      } catch (loadError) {
        if (active) {
          setError(loadError.message);
        }
      } finally {
        if (active) {
          setIsLoading(false);
        }
      }
    }

    load();
    const intervalId = window.setInterval(load, 5000);
    return () => {
      active = false;
      window.clearInterval(intervalId);
    };
  }, [api]);

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Documents</p>
          <h2>Processing queue</h2>
        </div>
        <Link to="/upload" className="button">
          Upload new
        </Link>
      </div>

      {error && <div className="alert alert-error">{error}</div>}
      {isLoading ? <p className="muted">Loading documents...</p> : null}

      {!isLoading && documents.length === 0 ? (
        <div className="empty-state">
          <h3>No documents yet</h3>
          <p>Start with an upload and the worker will process it asynchronously.</p>
        </div>
      ) : null}

      {documents.length > 0 ? (
        <div className="table-wrapper">
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Status</th>
                <th>Type</th>
                <th>Size</th>
                <th>Created</th>
              </tr>
            </thead>
            <tbody>
              {documents.map((document) => (
                <tr key={document.id}>
                  <td>
                    <Link to={`/documents/${document.id}`} className="table-link">
                      {document.filename}
                    </Link>
                  </td>
                  <td>
                    <StatusBadge status={document.status} />
                  </td>
                  <td>{document.content_type}</td>
                  <td>{Math.ceil(document.size_bytes / 1024)} KB</td>
                  <td>{new Date(document.created_at).toLocaleString()}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : null}
    </section>
  );
}
