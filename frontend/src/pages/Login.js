import React, { useState, useContext, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const { user, loginUser } = useContext(AuthContext);
  const navigate = useNavigate();

  useEffect(() => {
    if (user) navigate("/main");
  }, [user, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await loginUser(email, password);
      navigate("/main");
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-light px-6">

      <form
        onSubmit={handleSubmit}
        className="bg-background-card p-10 rounded-2xl shadow-medium w-full max-w-md"
      >
        <h1 className="text-3xl font-bold mb-6 text-center text-primary">
          Iniciar Sesión
        </h1>

        {user?.is_superuser && (
          <p className="text-success text-center mb-4 font-medium">
            ¡Superusuario ya está logueado! Puedes registrar usuarios.
          </p>
        )}

        {error && (
          <p className="text-error text-center mb-4 font-medium">{error}</p>
        )}

        <input
          type="email"
          placeholder="Correo electrónico"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border border-neutral-light p-3 mb-4 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          required
        />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border border-neutral-light p-3 mb-6 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          required
        />

        <button
          type="submit"
          className="bg-primary text-white px-6 py-3 w-full rounded-lg shadow-soft hover:bg-primary-light transition font-semibold"
        >
          Entrar
        </button>
      </form>
    </div>
  );
}
