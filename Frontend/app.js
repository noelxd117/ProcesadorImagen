const form = document.getElementById("uploadForm");
const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const statusText = document.getElementById("status");

const taskTypeSelect = document.getElementById("taskType");
const convertFormat = document.getElementById("convertFormat");

const API_BASE = window.location.origin;

// Mapear valores del frontend a valores de la API
const taskTypeMapping = {
  "resize": "redimensionar",
  "grayscale": "filtro",
  "thumbnail": "miniatura",
  "convert": "convertir"
};

// Mostrar selector de formato solo en convertir
taskTypeSelect.addEventListener("change", () => {

  if (taskTypeSelect.value === "convert") {

    convertFormat.style.display = "block";

  } else {

    convertFormat.style.display = "none";
  }
});

// Preview imagen
imageInput.addEventListener("change", () => {

  const file = imageInput.files[0];

  if (file) {
    preview.src = URL.createObjectURL(file);
  }
});


// Enviar tarea
form.addEventListener("submit", async (e) => {

  e.preventDefault();

  const file = imageInput.files[0];

  if (!file) {
    statusText.textContent = "Selecciona una imagen";
    return;
  }

  const taskTypeSelected = taskTypeSelect.value;
  const apiTaskType = taskTypeMapping[taskTypeSelected];

  const formData = new FormData();

  formData.append("file", file);
  formData.append("process_type", apiTaskType);

  // Parámetros según tipo
  if (taskTypeSelected === "resize") {

    formData.append(
      "parameters",
      JSON.stringify({
        width: 800,
        height: 600
      })
    );

  } else if (taskTypeSelected === "grayscale") {

    formData.append(
      "parameters",
      JSON.stringify({
        filter_type: "grayscale"
      })
    );

  } else if (taskTypeSelected === "thumbnail") {

    formData.append(
      "parameters",
      JSON.stringify({
        size: 200
      })
    );

  } else if (taskTypeSelected === "convert") {

    formData.append(
      "parameters",
      JSON.stringify({
        format: convertFormat.value
      })
    );
  }

  statusText.textContent = "Enviando tarea...";

  try {

    const response = await fetch(`${API_BASE}/api/upload/`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Error ${response.status}: ${response.statusText}`);
    }

    const data = await response.json();

    const taskId = data.task_id;

    statusText.textContent = `Tarea creada: ${taskId}`;

    listenToTask(taskId);

  } catch (error) {

    statusText.textContent = "Error enviando tarea: " + error.message;

    console.error(error);
  }
});


// Escuchar SSE
function listenToTask(taskId) {

  const eventSource = new EventSource(
    `${API_BASE}/api/status/${taskId}/stream`
  );

  eventSource.onmessage = (event) => {

    const data = JSON.parse(event.data);

    // Mapear estados
    const statusMap = {
      "pendiente": "⏳ Pendiente",
      "en_proceso": "⚙️ Procesando...",
      "completada": "✅ Completada",
      "error": "❌ Error"
    };

    const displayStatus = statusMap[data.status] || data.status;

    statusText.textContent = displayStatus;

    if (data.error) {

      statusText.textContent = "❌ Error: " + data.error;

      eventSource.close();

      return;
    }

    if (data.status === "completada") {

      eventSource.close();

      displayResult(taskId);
    }

    if (data.status === "error") {

      eventSource.close();

      statusText.textContent =
        `❌ Error: ${data.error_message || "Error desconocido"}`;
    }
  };

  eventSource.onerror = () => {

    eventSource.close();

    statusText.textContent = "❌ Error de conexión";
  };
}


// Mostrar resultado
async function displayResult(taskId) {

  try {

    const infoResponse = await fetch(
      `${API_BASE}/api/results/${taskId}/info`
    );

    const info = await infoResponse.json();

    const resultContainer =
      document.getElementById("resultContainer");

    resultContainer.innerHTML = `
      <div class="result-info">
        <h3>✅ Procesamiento completado</h3>

        <p>
          <strong>Tipo:</strong>
          ${info.process_type}
        </p>

        <p>
          <strong>Archivo original:</strong>
          ${info.original_filename}
        </p>

        <p>
          <strong>Fecha:</strong>
          ${new Date(info.created_at).toLocaleString()}
        </p>

        <a
          href="${API_BASE}/api/results/${taskId}"
          download="processed_image"
          class="download-btn"
        >
          📥 Descargar imagen
        </a>
      </div>
    `;

  } catch (error) {

    console.error(
      "Error obteniendo información del resultado:",
      error
    );
  }
}