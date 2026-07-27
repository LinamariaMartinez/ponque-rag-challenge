// Asistente interno Ponqué Ponqué Calarcá — chat vanilla JS (sin framework).
(function () {
  "use strict";

  const chat = document.getElementById("chat");
  const formulario = document.getElementById("formulario");
  const input = document.getElementById("pregunta");
  const botonEnviar = document.getElementById("boton-enviar");
  const chips = document.getElementById("chips");

  function crearBurbujaUsuario(texto) {
    const burbuja = document.createElement("div");
    burbuja.className = "burbuja burbuja--usuario";

    const parrafo = document.createElement("p");
    parrafo.className = "burbuja__texto";
    parrafo.textContent = texto;

    burbuja.appendChild(parrafo);
    return burbuja;
  }

  function crearBurbujaCargando() {
    const burbuja = document.createElement("div");
    burbuja.className = "burbuja burbuja--agente burbuja--cargando";

    const parrafo = document.createElement("p");
    parrafo.className = "burbuja__texto";
    parrafo.textContent = "Pensando...";

    burbuja.appendChild(parrafo);
    return burbuja;
  }

  function crearBurbujaAgente(respuesta, fuentes) {
    const burbuja = document.createElement("div");
    burbuja.className = "burbuja burbuja--agente";

    const parrafo = document.createElement("p");
    parrafo.className = "burbuja__texto";
    parrafo.textContent = respuesta;
    burbuja.appendChild(parrafo);

    if (Array.isArray(fuentes) && fuentes.length > 0) {
      const lista = document.createElement("ul");
      lista.className = "fuentes";
      fuentes.forEach(function (fuente) {
        const item = document.createElement("li");
        item.className = "fuentes__item";
        item.textContent = fuente;
        lista.appendChild(item);
      });
      burbuja.appendChild(lista);
    }

    return burbuja;
  }

  function crearBurbujaError(texto) {
    const burbuja = document.createElement("div");
    burbuja.className = "burbuja burbuja--agente burbuja--error";

    const parrafo = document.createElement("p");
    parrafo.className = "burbuja__texto";
    parrafo.textContent = texto;

    burbuja.appendChild(parrafo);
    return burbuja;
  }

  function desplazarAlFinal() {
    chat.scrollTop = chat.scrollHeight;
  }

  async function enviarPregunta(pregunta) {
    chat.appendChild(crearBurbujaUsuario(pregunta));
    desplazarAlFinal();

    const burbujaCargando = crearBurbujaCargando();
    chat.appendChild(burbujaCargando);
    desplazarAlFinal();

    input.disabled = true;
    botonEnviar.disabled = true;

    try {
      const respuestaHttp = await fetch("/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ pregunta: pregunta }),
      });

      if (!respuestaHttp.ok) {
        throw new Error("Respuesta no exitosa del servidor: " + respuestaHttp.status);
      }

      const datos = await respuestaHttp.json();
      burbujaCargando.remove();
      chat.appendChild(crearBurbujaAgente(datos.respuesta, datos.fuentes));
    } catch (error) {
      burbujaCargando.remove();
      chat.appendChild(
        crearBurbujaError("No se pudo conectar con el asistente. Intenta de nuevo en un momento.")
      );
      console.error("Error al consultar /chat:", error);
    } finally {
      input.disabled = false;
      botonEnviar.disabled = false;
      desplazarAlFinal();
      input.focus();
    }
  }

  formulario.addEventListener("submit", function (evento) {
    evento.preventDefault();
    const pregunta = input.value.trim();
    if (!pregunta) {
      return;
    }
    input.value = "";
    enviarPregunta(pregunta);
  });

  chips.addEventListener("click", function (evento) {
    const chip = evento.target.closest(".chip");
    if (!chip) {
      return;
    }
    input.value = chip.dataset.pregunta || chip.textContent;
    input.focus();
  });
})();
