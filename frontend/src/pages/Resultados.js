import React, { useContext, useEffect, useState } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import jsPDF from "jspdf";
import autoTable from "jspdf-autotable";

const Resultados = () => {
  const { user } = useContext(AuthContext);
  const navigate = useNavigate();
  const [datos, setDatos] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [selectedForm, setSelectedForm] = useState("");

  const fetchData = async (formLink) => {
    if (!formLink) {
      setError("Selecciona un formulario");
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const sheetIdMatch = formLink.match(/[-\w]{25,}/);
      if (!sheetIdMatch) throw new Error("ID de Google Sheet no válido");

      const sheetId = sheetIdMatch[0];
      const url = `https://docs.google.com/spreadsheets/d/${sheetId}/gviz/tq?tqx=out:json`;

      const response = await fetch(url);
      const text = await response.text();

      if (!text.startsWith("/*O_o*/")) {
        throw new Error("Formato inesperado en la respuesta");
      }

      const jsonText = text.substring(47, text.length - 2);
      const data = JSON.parse(jsonText);

      if (!data.table || !data.table.rows) {
        throw new Error("No se encontraron datos en la hoja de cálculo");
      }

      const rows = data.table.rows.map((row) =>
        row.c.map((cell) => cell?.v || "")
      );
      setDatos(rows);
    } catch (err) {
      console.error("Error al obtener los datos:", err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const exportarCSV = () => {
    if (datos.length === 0) return;
    const csvContent = datos
      .map((row) => row.map((cell) => `"${cell}"`).join(","))
      .join("\n");
    const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.setAttribute("href", url);
    link.setAttribute("download", `resultados_${user.email}.csv`);
    link.click();
  };

  const exportarPDF = () => {
    if (datos.length === 0) return;

    const doc = new jsPDF();
    doc.setFontSize(18);
    doc.text("Resultados del Formulario", 14, 22);
    doc.setFontSize(12);

    autoTable(doc, {
      head: [datos[0]],
      body: datos.slice(1),
      startY: 30,
      styles: { fontSize: 10 },
    });

    doc.save(`resultados_${user.email}.pdf`);
  };

  if (!user) return <p className="text-center mt-10">Cargando usuario...</p>;

  console.log("Usuario con formularios:", user);
  const formularios = [
    { id: "form_link1", url: user.form_link1 },
    { id: "form_link2", url: user.form_link2 },
    { id: "form_link3", url: user.form_link3 },
  ].filter((f) => f.url);

  return (
    <div className="min-h-screen bg-neutral-light py-10 px-4">
      <div className="max-w-6xl mx-auto bg-white p-6 rounded-xl shadow-soft">
        <h2 className="text-3xl font-bold text-center text-primary mb-6">
          Resultados de Formularios
        </h2>

        <div className="mb-4 p-4 bg-gray-100 rounded">
          <p>
            <strong>Form Link 1:</strong> {user.form_link1 || "No asignado"}
          </p>
          <p>
            <strong>Form Link 2:</strong> {user.form_link2 || "No asignado"}
          </p>
          <p>
            <strong>Form Link 3:</strong> {user.form_link3 || "No asignado"}
          </p>
        </div>

        <div className="mb-6">
          <button
            onClick={() => navigate(-1)}
            className="px-4 py-2 bg-neutral text-white rounded-lg shadow-soft hover:bg-neutral-light transition"
          >
            Volver
          </button>
        </div>

        {formularios.length > 0 ? (
          <div className="mb-6 flex flex-col md:flex-row items-center gap-4">
            <select
              value={selectedForm}
              onChange={(e) => {
                setSelectedForm(e.target.value);
                fetchData(e.target.value);
              }}
              className="border px-3 py-2 rounded-lg"
            >
              <option value="">-- Selecciona un formulario --</option>
              {formularios.map((f, idx) => (
                <option key={f.id} value={f.url}>
                  Formulario {idx + 1}
                </option>
              ))}
            </select>

            <button
              onClick={exportarCSV}
              className="px-5 py-2 bg-green-600 text-white rounded-lg shadow-soft hover:bg-green-700 transition font-medium"
            >
              Descargar CSV
            </button>
            <button
              onClick={exportarPDF}
              className="px-5 py-2 bg-red-600 text-white rounded-lg shadow-soft hover:bg-red-700 transition font-medium"
            >
              Descargar PDF
            </button>
          </div>
        ) : (
          <p className="text-red-600 text-center">
            No se encontraron links de formularios para este usuario.
          </p>
        )}

        {loading ? (
          <p className="text-gray-500 text-lg text-center">Cargando datos...</p>
        ) : error ? (
          <p className="text-red-600 text-lg text-center font-medium">
            Error: {error}
          </p>
        ) : datos.length === 0 ? (
          <p className="text-gray-500 text-lg text-center">
            No hay datos disponibles.
          </p>
        ) : (
          <div className="overflow-x-auto rounded-lg border border-gray-200 shadow-md">
            <table className="w-full border-collapse bg-white text-sm">
              <thead>
                <tr className="bg-primary text-white">
                  {datos[0].map((header, index) => (
                    <th
                      key={index}
                      className="px-6 py-3 text-left font-semibold"
                    >
                      {header}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {datos.slice(1).map((row, rowIndex) => (
                  <tr
                    key={rowIndex}
                    className={`${
                      rowIndex % 2 === 0 ? "bg-gray-50" : "bg-white"
                    } hover:bg-gray-100 transition`}
                  >
                    {row.map((cell, cellIndex) => (
                      <td
                        key={cellIndex}
                        className="px-6 py-3 border-t border-gray-200"
                      >
                        {cell}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};

export default Resultados;
