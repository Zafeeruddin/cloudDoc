import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "./auth";

function linkClassName({ isActive }) {
  return isActive ? "nav-link nav-link-active" : "nav-link";
}

export default function Layout() {
  const { userId, email, logout } = useAuth();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">DocOps</p>
          <h1>Document processing control plane</h1>
          <p className="muted">
            Upload documents, track asynchronous processing, and fetch results.
          </p>
        </div>

        <nav className="nav-list">
          <NavLink to="/documents" className={linkClassName}>
            Documents
          </NavLink>
          <NavLink to="/upload" className={linkClassName}>
            Upload
          </NavLink>
        </nav>

        <div className="user-card">
          <strong>{userId}</strong>
          <span>{email}</span>
          <button className="button button-secondary" onClick={logout}>
            Sign out
          </button>
        </div>
      </aside>

      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
