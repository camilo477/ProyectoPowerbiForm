import { createContext, useState } from "react";

export const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const savedUser = localStorage.getItem("user");
    return savedUser ? JSON.parse(savedUser) : null;
  });

  const loginUser = async (email, password) => {
    const res = await fetch("http://127.0.0.1:8000/api/accounts/login/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
      credentials: "include"
    });

    const data = await res.json();

    if (data.success) {
      const sessionRes = await fetch(
        `http://127.0.0.1:8000/api/accounts/powerbi-link/?email=${email}`,
        {
          method: "GET",
          credentials: "include",
        }
      );

      if (!sessionRes.ok) {
        throw new Error("No se pudo obtener la sesión del usuario");
      }

      const sessionData = await sessionRes.json();

      const fullUser = {
        ...data,
        id: sessionData.id || null,
        username: sessionData.username || "",
        form_link: sessionData.form_link || "",
        powerbi_link: sessionData.powerbi_link || ""
      };

      console.log("Usuario logueado:", fullUser);
      console.log("ID del usuario:", fullUser.id);
      console.log("Email del usuario:", fullUser.email);
      console.log("Link de Power BI del usuario:", fullUser.powerbi_link);

      setUser(fullUser);
      localStorage.setItem("user", JSON.stringify(fullUser));
    } else {
      throw new Error(data.error || "Error al iniciar sesión");
    }
  };

  const logoutUser = () => {
    setUser(null);
    localStorage.removeItem("user");
  };

  return (
    <AuthContext.Provider value={{ user, loginUser, logoutUser }}>
      {children}
    </AuthContext.Provider>
  );
}
