import React, { useEffect, useState, useContext } from "react";
import { AuthContext } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Crud() {
  const { user } = useContext(AuthContext);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [editingUserId, setEditingUserId] = useState(null);
  const [formData, setFormData] = useState({
    username: "",
    email: "",
    form_link1: "",
    form_link2: "",
    form_link3: "",
    powerbi_link: "",
  });

  const navigate = useNavigate();

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(
        "http://127.0.0.1:8000/api/accounts/users/",
        {
          credentials: "include",
        }
      );
      if (!response.ok) throw new Error("Error al obtener usuarios");
      const data = await response.json();
      setUsers(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (user?.is_superuser) fetchUsers();
  }, [user]);

  const handleDelete = async (id) => {
    if (!window.confirm("¿Estás seguro de eliminar este usuario?")) return;
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/accounts/users/${id}/`,
        {
          method: "DELETE",
          credentials: "include",
        }
      );
      if (!response.ok) throw new Error("Error al eliminar usuario");
      setUsers(users.filter((u) => u.id !== id));
    } catch (err) {
      alert(err.message);
    }
  };

  const handleEdit = (u) => {
    setEditingUserId(u.id);
    setFormData({
      username: u.username,
      email: u.email,
      form_link1: u.profile?.form_link1 || "",
      form_link2: u.profile?.form_link2 || "",
      form_link3: u.profile?.form_link3 || "",
      powerbi_link: u.profile?.powerbi_link || "",
    });
  };

  const handleCancel = () => {
    setEditingUserId(null);
    setFormData({
      username: "",
      email: "",
      form_link1: "",
      form_link2: "",
      form_link3: "",
      powerbi_link: "",
    });
  };

  const handleSave = async () => {
    try {
      const response = await fetch(
        `http://127.0.0.1:8000/api/accounts/users/${editingUserId}/`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify({
            username: formData.username,
            email: formData.email,
            profile: {
              form_link1: formData.form_link1,
              form_link2: formData.form_link2,
              form_link3: formData.form_link3,
              powerbi_link: formData.powerbi_link,
            },
          }),
        }
      );

      const data = await response.json();
      if (!response.ok)
        throw new Error(data.detail || "Error al actualizar usuario");

      setUsers(users.map((u) => (u.id === editingUserId ? data : u)));
      handleCancel();
    } catch (err) {
      alert(err.message);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  if (!user) return <p>Cargando...</p>;
  if (!user.is_superuser) return <p>No tienes permisos para ver esta página</p>;

  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-light px-6 py-10">
      <div className="bg-white p-8 rounded-2xl shadow-medium w-full max-w-6xl">
        <button
          onClick={() => navigate(-1)}
          className="mb-6 bg-neutral text-white px-5 py-2 rounded-lg shadow-soft hover:bg-neutral-light transition font-semibold"
        >
          Volver
        </button>

        <h2 className="text-3xl font-bold text-primary text-center mb-8">
          Gestión de Usuarios
        </h2>

        {loading ? (
          <p className="text-gray-600 text-center">Cargando usuarios...</p>
        ) : error ? (
          <p className="text-red-500 text-center">{error}</p>
        ) : (
          <div className="overflow-x-auto rounded-xl shadow-soft">
            <table className="w-full border border-gray-200 text-left rounded-lg overflow-hidden">
              <thead className="bg-primary text-white">
                <tr>
                  <th className="px-4 py-3">ID</th>
                  <th className="px-4 py-3">Username</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Form Link 1</th>
                  <th className="px-4 py-3">Form Link 2</th>
                  <th className="px-4 py-3">Form Link 3</th>
                  <th className="px-4 py-3">PowerBI Link</th>
                  <th className="px-4 py-3">Acciones</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u, i) => (
                  <tr
                    key={u.id}
                    className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}
                  >
                    <td className="px-4 py-2">{u.id}</td>
                    <td className="px-4 py-2">
                      {editingUserId === u.id ? (
                        <input
                          name="username"
                          value={formData.username}
                          onChange={handleChange}
                          className="border px-2 py-1 rounded w-full"
                        />
                      ) : (
                        u.username
                      )}
                    </td>
                    <td className="px-4 py-2">
                      {editingUserId === u.id ? (
                        <input
                          name="email"
                          value={formData.email}
                          onChange={handleChange}
                          className="border px-2 py-1 rounded w-full"
                        />
                      ) : (
                        u.email
                      )}
                    </td>

                    {/* Form Link 1 */}
                    <td className="px-4 py-2 break-words max-w-xs">
                      {editingUserId === u.id ? (
                        <input
                          name="form_link1"
                          value={formData.form_link1}
                          onChange={handleChange}
                          className="border px-2 py-1 rounded w-full"
                        />
                      ) : (
                        u.profile?.form_link1 || "-"
                      )}
                    </td>

                    {/* Form Link 2 */}
                    <td className="px-4 py-2 break-words max-w-xs">
                      {editingUserId === u.id ? (
                        <input
                          name="form_link2"
                          value={formData.form_link2}
                          onChange={handleChange}
                          className="border px-2 py-1 rounded w-full"
                        />
                      ) : (
                        u.profile?.form_link2 || "-"
                      )}
                    </td>

                    {/* Form Link 3 */}
                    <td className="px-4 py-2 break-words max-w-xs">
                      {editingUserId === u.id ? (
                        <input
                          name="form_link3"
                          value={formData.form_link3}
                          onChange={handleChange}
                          className="border px-2 py-1 rounded w-full"
                        />
                      ) : (
                        u.profile?.form_link3 || "-"
                      )}
                    </td>

                    {/* PowerBI Link */}
                    <td className="px-4 py-2 break-words max-w-xs">
                      {editingUserId === u.id ? (
                        <input
                          name="powerbi_link"
                          value={formData.powerbi_link}
                          onChange={handleChange}
                          className="border px-2 py-1 rounded w-full"
                        />
                      ) : (
                        u.profile?.powerbi_link || "-"
                      )}
                    </td>

                    <td className="px-4 py-2 flex gap-2">
                      {editingUserId === u.id ? (
                        <>
                          <button
                            onClick={handleSave}
                            className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700 transition"
                          >
                            Guardar
                          </button>
                          <button
                            onClick={handleCancel}
                            className="bg-gray-500 text-white px-3 py-1 rounded hover:bg-gray-600 transition"
                          >
                            Cancelar
                          </button>
                        </>
                      ) : (
                        <>
                          <button
                            onClick={() => handleEdit(u)}
                            className="bg-secondary text-white px-3 py-1 rounded hover:bg-secondary-dark transition"
                          >
                            Editar
                          </button>
                          <button
                            onClick={() => handleDelete(u.id)}
                            className="bg-red-600 text-white px-3 py-1 rounded hover:bg-red-700 transition"
                          >
                            Eliminar
                          </button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
