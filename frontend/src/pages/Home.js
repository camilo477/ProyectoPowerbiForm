import { Link } from "react-router-dom";

const Home = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-neutral-light px-6">
      <div className="bg-background-card text-neutral-dark p-12 rounded-2xl shadow-medium max-w-lg text-center">
        <h1 className="text-4xl font-bold mb-4 text-primary">
          Bienvenido a la Plataforma
        </h1>
        <p className="text-lg mb-8 text-neutral">
          Accede a tu cuenta y gestiona tus recursos fácilmente.
        </p>

        <div className="flex justify-center space-x-4">
          <Link
            to="/login"
            className="px-6 py-3 bg-primary text-white rounded-xl shadow-soft hover:bg-primary-light transition font-semibold"
          >
            Iniciar Sesión
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;
