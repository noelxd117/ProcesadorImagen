const form = document.getElementById("uploadForm");
const imageInput = document.getElementById("imageInput");
const preview = document.getElementById("preview");
const statusText = document.getElementById("status");


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
  const taskType = document.getElementById("taskType").value;

  const formData = new FormData();

  formData.append("image", file);
  formData.append("task_type", taskType);

  statusText.textContent = "Enviando tarea...";

  try {

    const response = await fetch("http://localhost:5500/tasks", {
      method: "POST",
      body: formData
    });

    const data = await response.json();

    const taskId = data.task_id;

    statusText.textContent = `Tarea creada: ${taskId}`;

    listenToTask(taskId);

  } catch (error) {

    statusText.textContent = "Error enviando tarea";

    console.error(error);
  }

});


// Escuchar SSE
function listenToTask(taskId) {

  const eventSource = new EventSource(
    `http://localhost:5500/events/${taskId}`
  );

  eventSource.onmessage = (event) => {

    const data = JSON.parse(event.data);

    statusText.textContent = data.status;

    if (data.status === "completed") {

      eventSource.close();

      console.log("Procesamiento terminado");
    }

    if (data.status === "error") {

      eventSource.close();
    }
  };
}