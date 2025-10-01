import React, { useContext, useEffect, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const PowerBI = () => {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [formLinks, setFormLinks] = useState(null);

  useEffect(() => {
    const fetchLinks = async () => {
      if (!user?.email) return;
      try {
        const res = await fetch(
          `http://127.0.0.1:8000/api/accounts/user-links/?email=${user.email}`
        );
        const data = await res.json();
        console.log("Links recibidos", data);
        setFormLinks(data);
      } catch (error) {
        console.error("Error al obtener los links:", error);
      }
    };

    fetchLinks();
  }, [user]);

  if (!user) return <p>Cargando...</p>;

  if (!user.powerbi_link) {
    return (
      <div className="flex flex-col justify-center items-center h-[90vh]">
        <button
          onClick={() => navigate(-1)}
          className="mb-4 bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-800"
        >
          Volver
        </button>
        <p className="text-red-500 text-lg">
          No se encontró un link de Power BI para este usuario.
        </p>
        <p className="text-gray-500 mt-2">
          Usuario logeado: {user.username || user.email}
        </p>
        <p className="text-gray-500 mt-1">ID del usuario: {user.id}</p>
      </div>
    );
  }

  const queryParams = formLinks
    ? `?form1=${encodeURIComponent(
        formLinks.form_link1
      )}&form2=${encodeURIComponent(
        formLinks.form_link2
      )}&form3=${encodeURIComponent(formLinks.form_link3)}`
    : "";

  return (
    <div className="flex flex-col h-[90vh]">
      <button
        onClick={() => navigate(-1)}
        className="mb-2 bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-800 self-start"
      >
        Volver
      </button>

      <div className="flex flex-row flex-1 gap-2">
        <iframe
          title="Power BI Report"
          src={user.powerbi_link}
          className="flex-1 border rounded"
          allowFullScreen
        />

        <iframe
          title="IA Streamlit"
          src={`http://localhost:8501/?email=${user.email}`}
          className="flex-1 border rounded"
        />
      </div>
    </div>
  );
};

export default PowerBI;
