let nombres = [];
let nombreSeleccionado = "";

async function cargarNombres() {
  const res = await fetch('/nombres');
  nombres = await res.json();

  const select = document.getElementById('nombre');
  nombres.forEach(nombre => {
    const option = document.createElement('option');
    option.value = nombre;
    option.textContent = nombre;
    select.appendChild(option);
  });
}

function mostrarEncuesta() {
  const select = document.getElementById('nombre');
  nombreSeleccionado = select.value;

  if (!nombreSeleccionado) {
    alert("Por favor selecciona tu nombre.");
    return;
  }

  // Oculta selección, muestra encuesta
  document.getElementById('seleccion-nombre').style.display = 'none';
  document.getElementById('formulario-encuesta').style.display = 'block';

  // Generar preguntas
  const preguntasDiv = document.getElementById('preguntas');
  preguntasDiv.innerHTML = '';

  const otros = nombres.filter(nombre => nombre !== nombreSeleccionado);

  otros.forEach(nombre => {
    const contenedor = document.createElement('div');
    contenedor.innerHTML = `
      <label>¿Qué tan satisfecho estás con el rendimiento de <strong>${nombre}</strong>?</label><br>
      <select name="${nombre}" required>
        <option value="">-- Selecciona una puntuación --</option>
        <option value="1">1 (bajo)</option>
        <option value="2">2 (medio)</option>
        <option value="3">3 (alto)</option>
      </select><br><br>
    `;
    preguntasDiv.appendChild(contenedor);
  });
}

// Manejar envío del formulario
document.addEventListener('DOMContentLoaded', () => {
  cargarNombres();

  document.getElementById('encuesta').addEventListener('submit', async (e) => {
    e.preventDefault();

    const formData = new FormData(e.target);
    const respuestas = {};

    for (let [clave, valor] of formData.entries()) {
      respuestas[clave] = parseInt(valor);
    }

    const payload = {
      evaluador: nombreSeleccionado,
      respuestas: respuestas
    };

    const res = await fetch('/guardar', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });

    if (res.ok) {
      alert("¡Gracias por enviar tu evaluación!");
      location.reload();
    } else {
      alert("Ocurrió un error al guardar tus respuestas.");
    }
  });
});