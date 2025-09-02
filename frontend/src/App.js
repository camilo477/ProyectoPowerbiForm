import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./context/AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";

import Home from "./pages/Home";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Main from "./pages/Main";
import Resultados from "./pages/Resultados";
import Blog from "./pages/blog";
import PowerBI from "./pages/powerbi";
import Crud from "./pages/Crud";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {}
          <Route path="/" element={<Home />} />

          {}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/blog" element={<Blog />} />
          <Route path="/powerbi" element={<PowerBI />} />

          {}
          <Route
            path="/main"
            element={
              <ProtectedRoute>
                <Main />
              </ProtectedRoute>
            }
          />
          <Route
            path="/resultados"
            element={
              <ProtectedRoute>
                <Resultados />
              </ProtectedRoute>
            }
          />
          {}
          <Route
            path="/crud"
            element={
              <ProtectedRoute>
                <Crud />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
