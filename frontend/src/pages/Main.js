// src/pages/Main.js
import React, { useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function Main() {
  const navigate = useNavigate();
  const { user, logoutUser } = useContext(AuthContext);

  if (!user) return <p>Cargando...</p>;

  const handleLogout = () => {
    logoutUser();
    navigate("/login");
  };

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-neutral-light px-6">
      <div className="bg-white p-10 rounded-2xl shadow-soft w-full max-w-2xl text-center">
        <h1 className="text-4xl font-bold text-primary mb-4">
          Bienvenido, {user.username || user.email}
        </h1>

        {user.is_superuser && (
          <p className="text-secondary-dark font-medium mb-6">
            ¡Estás logueado como superusuario!
          </p>
        )}

        {}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 mb-6">
          <button
            onClick={() => navigate("/resultados")}
            className="bg-primary text-white px-6 py-3 rounded-lg shadow-soft hover:bg-primary-light transition font-semibold"
          >
            Ver Resultados
          </button>

          {}
          {user.is_superuser && (
            <button
              onClick={() => navigate("/register")}
              className="bg-secondary text-white px-6 py-3 rounded-lg shadow-soft hover:bg-secondary-dark transition font-semibold"
            >
              Registrar Usuario
            </button>
          )}

          {}
          {user.is_superuser && (
            <button
              onClick={() => navigate("/crud")}
              className="bg-primary-dark text-white px-6 py-3 rounded-lg shadow-soft hover:bg-primary transition font-semibold"
            >
              Ir a CRUD
            </button>
          )}

          <button
            onClick={() => navigate("/blog")}
            className="bg-neutral text-white px-6 py-3 rounded-lg shadow-soft hover:bg-neutral-light transition font-semibold"
          >
            Ir a Blog
          </button>

          <button
            onClick={() => navigate("/powerbi")}
            className="bg-indigo-600 text-white px-6 py-3 rounded-lg shadow-soft hover:bg-indigo-500 transition font-semibold"
          >
            Ir a Power BI
          </button>
        </div>

        {}
        <button
          onClick={handleLogout}
          className="bg-red-600 text-white px-6 py-3 rounded-lg shadow-soft hover:bg-red-700 transition font-semibold mt-4"
        >
          Cerrar Sesión
        </button>
      </div>
    </div>
  );
}
