import React from "react";

function Streamlit() {
  return (
    <div style={{ width: "100%", height: "100vh" }}>
      <iframe
        src="http://localhost:8501" // 🔹 cambia esta URL por la de tu app Streamlit en producción
        title="IA Streamlit"
        style={{ width: "100%", height: "100%", border: "none" }}
      />
    </div>
  );
}

export default Streamlit;
