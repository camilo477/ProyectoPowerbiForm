import React, { useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

const PowerBI = () => {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate(); 

  if (!user) return <p>Cargando...</p>;

  console.log("Usuario logeado:", user);
  console.log("ID del usuario:", user.id);
  console.log("Email del usuario:", user.email);
  console.log("Link de Power BI del usuario:", user.powerbi_link);

  if (!user.powerbi_link) {
    return (
      <div className="flex flex-col justify-center items-center h-[90vh]">
        {}
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

  return (
    <div style={{ height: "90vh", width: "100%" }} className="flex flex-col">
      {}
      <button
        onClick={() => navigate(-1)}
        className="mb-2 bg-gray-700 text-white px-4 py-2 rounded hover:bg-gray-800 self-start"
      >
        Volver
      </button>

      <iframe
        title="Power BI Report"
        width="100%"
        height="100%"
        src={user.powerbi_link}
        frameBorder="0"
        allowFullScreen={true}
      />
    </div>
  );
};

export default PowerBI;
