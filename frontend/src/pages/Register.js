// src/pages/Register.js
import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../context/AuthContext";

export default function Register() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [formLink1, setFormLink1] = useState("");
  const [formLink2, setFormLink2] = useState("");
  const [formLink3, setFormLink3] = useState("");
  const [powerbiLink, setPowerbiLink] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setSuccess("");

    if (!user?.is_superuser) {
      setError("Solo los superusuarios pueden registrar usuarios normales");
      return;
    }

    try {
      const res = await fetch("http://127.0.0.1:8000/api/accounts/register/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          email,
          username,
          password,
          form_link1: formLink1,
          form_link2: formLink2,
          form_link3: formLink3,
          powerbi_link: powerbiLink,
        }),
      });

      const data = await res.json();

      if (res.status === 201) {
        setSuccess("Usuario normal creado exitosamente");
        setEmail("");
        setUsername("");
        setPassword("");
        setFormLink1("");
        setFormLink2("");
        setFormLink3("");
        setPowerbiLink("");
      } else {
        setError(data.error || "Ocurrió un error al registrar el usuario");
      }
    } catch (err) {
      setError("Error en la conexión con el servidor");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-light px-4">
      <form
        onSubmit={handleSubmit}
        className="bg-white p-8 rounded-xl shadow-soft w-full max-w-md"
      >
        {/* Botón volver */}
        <button
          type="button"
          onClick={() => navigate(-1)}
          className="mb-4 bg-neutral text-white px-4 py-2 rounded-lg shadow-soft hover:bg-neutral-light transition font-medium"
        >
          Volver
        </button>

        <h1 className="text-2xl font-bold mb-6 text-center text-primary">
          Registrar Usuario
        </h1>

        {success && (
          <p className="text-green-600 mb-3 text-center font-medium">
            {success}
          </p>
        )}
        {error && (
          <p className="text-red-600 mb-3 text-center font-medium">{error}</p>
        )}

        {/* Campos básicos */}
        <input
          type="email"
          placeholder="Correo electrónico"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="border p-2 mb-4 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          required
        />
        <input
          type="text"
          placeholder="Nombre de usuario"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="border p-2 mb-4 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          required
        />
        <input
          type="password"
          placeholder="Contraseña"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="border p-2 mb-4 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
          required
        />

        {/* 3 Formularios */}
        <input
          type="url"
          placeholder="Link del formulario 1"
          value={formLink1}
          onChange={(e) => setFormLink1(e.target.value)}
          className="border p-2 mb-4 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <input
          type="url"
          placeholder="Link del formulario 2"
          value={formLink2}
          onChange={(e) => setFormLink2(e.target.value)}
          className="border p-2 mb-4 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        />
        <input
          type="url"
          placeholder="Link del formulario 3"
          value={formLink3}
          onChange={(e) => setFormLink3(e.target.value)}
          className="border p-2 mb-4 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        />

        {/* PowerBI */}
        <input
          type="url"
          placeholder="Link Power BI"
          value={powerbiLink}
          onChange={(e) => setPowerbiLink(e.target.value)}
          className="border p-2 mb-6 w-full rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
        />

        <button
          type="submit"
          className="bg-primary text-white px-4 py-2 w-full rounded-lg shadow-soft hover:bg-primary-dark transition font-semibold"
        >
          Registrar
        </button>
      </form>
    </div>
  );
}
