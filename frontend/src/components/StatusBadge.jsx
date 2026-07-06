const STATUS_CLASS = {
  PENDING_UPLOAD: "status-pending",
  UPLOADED: "status-uploaded",
  PROCESSING: "status-processing",
  COMPLETED: "status-completed",
  FAILED: "status-failed",
};

export default function StatusBadge({ status }) {
  return <span className={`status-pill ${STATUS_CLASS[status] || "status-pending"}`}>{status}</span>;
}
