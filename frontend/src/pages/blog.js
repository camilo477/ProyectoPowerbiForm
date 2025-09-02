import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

const Blog = () => {
  const chartRef = useRef(null); 

  useEffect(() => {
    const ctx = document.getElementById('graficaRotacion')?.getContext('2d');

    if (ctx) {
      if (chartRef.current) {
        chartRef.current.destroy();
      }

      chartRef.current = new Chart(ctx, {
        type: 'bar',
        data: {
          labels: ['BPO', 'Tecnología', 'Retail', 'Salud', 'Educación'],
          datasets: [{
            label: 'Índice de Rotación en Colombia (%) - 2025',
            data: [28, 22, 18, 12, 9],
            borderWidth: 1,
            backgroundColor: 'rgba(166, 141, 74, 0.7)',
          }],
        },
        options: {
          responsive: true,
          scales: {
            y: {
              beginAtZero: true,
            },
          },
        },
      });
    }

    return () => {
      if (chartRef.current) {
        chartRef.current.destroy();
      }
    };
  }, []);

  return (
    <div className="bg-[var(--color-crema)] text-[var(--color-oscuro)] font-sans">
      <style>
        {`
          :root {
            --color-oscuro: #00070A;
            --color-verde-oscuro: #282B1B;
            --color-verde-profundo: #283B28;
            --color-verde-medio: #4E6A5B;
            --color-crema: #E0DED1;
            --color-mostaza: #A68D4A;
          }
        `}
      </style>

      <header className="bg-[var(--color-verde-oscuro)] text-[var(--color-crema)] p-6 text-center">
        <h1 className="text-4xl font-bold">Rotación de Personal en Colombia - 2025</h1>
        <p className="text-lg mt-2">
          Comprendiendo causas, consecuencias y estrategias para reducirla en el contexto colombiano actual
        </p>
      </header>

      <main className="max-w-5xl mx-auto p-6 space-y-16">
        <section>
          <h2 className="text-3xl font-bold mb-4 text-[var(--color-verde-profundo)]">
            ¿Qué es la rotación de personal?
          </h2>
          <p className="mb-4">
            En Colombia, la rotación de personal es un fenómeno creciente...
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <img
              src="https://images.unsplash.com/photo-1557804506-669a67965ba0"
              alt="Rotación de empleados"
              className="w-full rounded-lg shadow-md"
            />
            <div>
              <p className="mb-2">
                Este fenómeno tiene implicaciones en los costos de reclutamiento...
              </p>
              <p>
                En sectores como tecnología y BPO, la rotación puede superar el 30%...
              </p>
            </div>
          </div>
        </section>

        <section>
          <h2 className="text-3xl font-bold mb-4 text-[var(--color-verde-profundo)]">
            Factores que impulsan la rotación en Colombia
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <p>Algunos de los principales factores que influyen...</p>
              <ul className="list-disc ml-6 space-y-2">
                <li>Salarios no competitivos</li>
                <li>Ambiente laboral desfavorable</li>
                <li>Poca o nula retroalimentación</li>
                <li>Falta de reconocimiento</li>
                <li>Estancamiento profesional</li>
              </ul>
            </div>
            <img
              src="https://os-assets.starmeup.com/blog/wp-content/uploads/2018/10/Blog_3_ESPA%C3%91OL.jpg"
              alt="Factores de rotación"
              className="w-full rounded-lg shadow-md"
            />
          </div>
        </section>

        <section>
          <h2 className="text-3xl font-bold mb-4 text-[var(--color-verde-profundo)]">
            Estrategias efectivas para reducir la rotación
          </h2>
          <p className="mb-4">Reducir la rotación de personal en Colombia requiere...</p>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[{
              src: "https://images.unsplash.com/photo-1573496267526-08a69e46a409",
              title: "Salarios competitivos",
              desc: "Actualizar rangos salariales según estudios del mercado laboral colombiano."
            }, {
              src: "https://images.unsplash.com/photo-1521737604893-d14cc237f11d",
              title: "Programas de capacitación",
              desc: "Inversión en desarrollo profesional a través del SENA y universidades."
            }, {
              src: "https://images.unsplash.com/photo-1551836022-d5d88e9218df",
              title: "Flexibilidad y bienestar",
              desc: "Horarios flexibles, días de salud mental, y apoyo al balance vida-trabajo."
            }].map((card, idx) => (
              <div key={idx} className="bg-white p-4 rounded shadow-md">
                <img src={card.src} alt={card.title} className="w-full rounded mb-2" />
                <h3 className="text-xl font-semibold mb-1">{card.title}</h3>
                <p>{card.desc}</p>
              </div>
            ))}
          </div>
        </section>

        <section>
          <h2 className="text-3xl font-bold mb-4 text-[var(--color-verde-profundo)]">
            Impacto económico de la rotación
          </h2>
          <p className="mb-4">Según Fedesarrollo, cada reemplazo de un trabajador puede costar entre el 50% y 150% de su salario anual...</p>
          <div className="flex justify-center">
            <canvas id="graficaRotacion" className="w-full md:w-2/3 h-64 bg-white rounded-lg shadow-md"></canvas>
          </div>
          <p className="mt-4 text-sm text-gray-700 text-center">
            Fuente: Ministerio de Trabajo y Fedesarrollo, 2025.
          </p>
        </section>

        <section>
          <h2 className="text-3xl font-bold mb-4 text-[var(--color-verde-profundo)]">
            Enlaces útiles y mejores prácticas
          </h2>
          <ul className="list-decimal ml-6 space-y-2">
            {[
              ["https://www.mintrabajo.gov.co/", "Ministerio del Trabajo de Colombia"],
              ["https://observatorio.mintrabajo.gov.co", "Observatorio Laboral"],
              ["https://www.fedesarrollo.org.co/", "Fedesarrollo: Informes de rotación laboral"],
              ["https://www.elempleo.com/co/noticias", "El Empleo: Noticias sobre mercado laboral"],
              ["https://gestionsocial.org.co/", "Fundación Gestión Social"]
            ].map(([href, text], idx) => (
              <li key={idx}>
                <a href={href} className="text-[var(--color-mostaza)] underline" target="_blank" rel="noopener noreferrer">
                  {text}
                </a>
              </li>
            ))}
          </ul>
        </section>
      </main>

      <footer className="bg-[var(--color-verde-oscuro)] text-[var(--color-crema)] p-4 text-center">
        <p>© 2025 Blog de Gestión del Talento en Colombia. Todos los derechos reservados.</p>
      </footer>
    </div>
  );
};

export default Blog;
