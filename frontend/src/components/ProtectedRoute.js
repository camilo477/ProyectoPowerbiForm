import React, { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function ProtectedRoute({ children, role }) {
  const { user, loading } = useContext(AuthContext);

  if (loading) return <p className="text-center mt-10">Cargando...</p>;

  if (!user) return <Navigate to="/login" />;

  if (role === "admin" && !user.is_superuser) return <Navigate to="/login" />;

  return children;
}
