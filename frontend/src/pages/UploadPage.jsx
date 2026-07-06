import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createApiClient, uploadFileToPresignedUrl } from "../api";
import { useAuth } from "../components/auth";

const MIME_BY_EXTENSION = {
  ".pdf": "application/pdf",
  ".txt": "text/plain",
  ".md": "text/markdown",
  ".csv": "text/csv",
  ".json": "application/json",
};

export default function UploadPage() {
  const auth = useAuth();
  const api = useMemo(() => createApiClient(auth), [auth]);
  const navigate = useNavigate();

  const [file, setFile] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  function resolveContentType(selectedFile) {
    if (selectedFile.type) {
      return selectedFile.type;
    }

    const match = selectedFile.name.toLowerCase().match(/\.[^.]+$/);
    return MIME_BY_EXTENSION[match?.[0] || ""] || "application/octet-stream";
  }

  async function handleSubmit(event) {
    event.preventDefault();
    if (!file) {
      setError("Select a file first.");
      return;
    }

    setError("");
    setSuccess("");
    setIsSubmitting(true);

    try {
      const resolvedContentType = resolveContentType(file);
      const uploadSession = await api.initUpload({
        filename: file.name,
        content_type: resolvedContentType,
        size_bytes: file.size,
      });

      await uploadFileToPresignedUrl(uploadSession.upload_url, file, resolvedContentType);
      const document = await api.completeUpload(uploadSession.document_id);

      setSuccess(`Upload completed. Document ${document.id} is queued for processing.`);
      navigate(`/documents/${document.id}`);
    } catch (uploadError) {
      setError(uploadError.message);
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <p className="eyebrow">Upload</p>
          <h2>Submit a document</h2>
        </div>
      </div>

      <form className="upload-form" onSubmit={handleSubmit}>
        <div className="field">
          <label htmlFor="document">Document</label>
          <input
            id="document"
            type="file"
            accept=".txt,.pdf,.md,.csv,.json"
            onChange={(event) => setFile(event.target.files?.[0] || null)}
          />
        </div>

        {file && (
          <div className="file-summary">
            <span>{file.name}</span>
            <span>{resolveContentType(file)}</span>
            <span>{Math.ceil(file.size / 1024)} KB</span>
          </div>
        )}

        {error && <div className="alert alert-error">{error}</div>}
        {success && <div className="alert alert-success">{success}</div>}

        <button className="button" type="submit" disabled={isSubmitting || !file}>
          {isSubmitting ? "Uploading..." : "Upload and Process"}
        </button>
      </form>
    </section>
  );
}
