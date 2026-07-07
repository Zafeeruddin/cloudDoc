import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../components/auth";

export default function LoginPage() {
  const { isAuthenticated, login } = useAuth();
  const [userId, setUserId] = useState("00000000-0000-0000-0000-000000000001");
  const [email, setEmail] = useState("demo@docops.dev");
  const [name, setName] = useState("Demo User");
  const [token, setToken] = useState("docops:00000000-0000-0000-0000-000000000001:demo@docops.dev:Demo User");

  if (isAuthenticated) {
    return <Navigate to="/documents" replace />;
  }

  return (
    <div className="login-page">
      <div className="login-card">
        <p className="eyebrow">DocOps</p>
        <h1>Login placeholder</h1>
        <p className="muted">
          This form simulates the identity propagated by API Gateway and the Lambda authorizer.
        </p>
        <p className="muted">
          Token format: <code>docops:&lt;user-id&gt;:&lt;email&gt;:&lt;display-name&gt;</code>
        </p>

        <div className="field">
          <label htmlFor="userId">User ID</label>
          <input id="userId" value={userId} onChange={(event) => setUserId(event.target.value)} />
        </div>

        <div className="field">
          <label htmlFor="email">Email</label>
          <input id="email" value={email} onChange={(event) => setEmail(event.target.value)} />
        </div>

        <div className="field">
          <label htmlFor="name">Display name</label>
          <input id="name" value={name} onChange={(event) => setName(event.target.value)} />
        </div>

        <div className="field">
          <label htmlFor="token">Mock token</label>
          <input id="token" value={token} onChange={(event) => setToken(event.target.value)} />
        </div>

        <button
          className="button"
          onClick={() => login({ userId, email, name, token })}
          disabled={!userId || !email || !name || !token}
        >
          Continue
        </button>
      </div>
    </div>
  );
}
