import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./components/Layout";
import { AuthProvider, useAuth } from "./components/auth";
import DocumentDetailsPage from "./pages/DocumentDetailsPage";
import DocumentListPage from "./pages/DocumentListPage";
import LoginPage from "./pages/LoginPage";
import UploadPage from "./pages/UploadPage";

function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

function AppRoutes() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/"
        element={
          <ProtectedRoute>
            <Layout />
          </ProtectedRoute>
        }
      >
        <Route index element={<Navigate to="/documents" replace />} />
        <Route path="upload" element={<UploadPage />} />
        <Route path="documents" element={<DocumentListPage />} />
        <Route path="documents/:documentId" element={<DocumentDetailsPage />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <AuthProvider>
      <AppRoutes />
    </AuthProvider>
  );
}
