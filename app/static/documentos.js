// Asistente interno Ponqué Ponqué Calarcá — panel de documentos (vanilla JS).
(function () {
  "use strict";

  const areasContenedor = document.getElementById("areas");
  const modal = document.getElementById("modal-vista-previa");
  const tituloModal = document.getElementById("titulo-vista-previa");
  const cuerpoModal = document.getElementById("cuerpo-vista-previa");
  const botonCerrar = document.getElementById("cerrar-vista-previa");
  const botonPreguntar = document.getElementById("preguntar-sobre-documento");
  const inputPregunta = document.getElementById("pregunta");

  let documentoActual = null;

  function crearAreaAcordeon(area, archivos) {
    const contenedor = document.createElement("div");
    contenedor.className = "area";

    const boton = document.createElement("button");
    boton.type = "button";
    boton.className = "area__boton";
    boton.textContent = area;

    const lista = document.createElement("ul");
    lista.className = "area__lista";
    lista.hidden = true;

    archivos.forEach(function (doc) {
      const item = document.createElement("li");
      item.className = "area__archivo";

      const botonArchivo = document.createElement("button");
      botonArchivo.type = "button";
      botonArchivo.className = "area__archivo-boton";
      botonArchivo.textContent = doc.archivo;
      botonArchivo.addEventListener("click", function () {
        abrirVistaPrevia(area, doc.archivo);
      });

      item.appendChild(botonArchivo);
      lista.appendChild(item);
    });

    boton.addEventListener("click", function () {
      lista.hidden = !lista.hidden;
    });

    contenedor.appendChild(boton);
    contenedor.appendChild(lista);
    return contenedor;
  }

  async function cargarAreas() {
    try {
      const respuesta = await fetch("/documentos");
      if (!respuesta.ok) {
        throw new Error("No se pudo cargar la lista de documentos");
      }
      const datos = await respuesta.json();
      const areas = Object.keys(datos);
      if (areas.length === 0) {
        areasContenedor.textContent = "No hay documentos disponibles.";
        return;
      }
      areas.forEach(function (area) {
        areasContenedor.appendChild(crearAreaAcordeon(area, datos[area]));
      });
    } catch (error) {
      areasContenedor.textContent = "No se pudo cargar la lista de documentos.";
      console.error("Error al consultar /documentos:", error);
    }
  }

  function limpiarCuerpoModal() {
    cuerpoModal.innerHTML = "";
  }

  function renderizarTabla(hojas) {
    hojas.forEach(function (hoja) {
      if (hoja.hoja) {
        const subtitulo = document.createElement("h3");
        subtitulo.textContent = hoja.hoja;
        cuerpoModal.appendChild(subtitulo);
      }
      const tabla = document.createElement("table");
      if (hoja.encabezados && hoja.encabezados.length > 0) {
        const cabecera = document.createElement("tr");
        hoja.encabezados.forEach(function (texto) {
          const celda = document.createElement("th");
          celda.textContent = texto;
          cabecera.appendChild(celda);
        });
        tabla.appendChild(cabecera);
      }
      hoja.filas.forEach(function (fila) {
        const tr = document.createElement("tr");
        fila.forEach(function (valor) {
          const td = document.createElement("td");
          td.textContent = valor;
          tr.appendChild(td);
        });
        tabla.appendChild(tr);
      });
      cuerpoModal.appendChild(tabla);
    });
  }

  function renderizarTexto(parrafos) {
    parrafos.forEach(function (parrafo) {
      const p = document.createElement("p");
      p.textContent = parrafo;
      cuerpoModal.appendChild(p);
    });
  }

  function renderizarHtml(html) {
    // Contenido de confianza (generado por nosotros mismos en documentos/,
    // no proviene del modelo ni de entrada del usuario) — ver el spec.
    cuerpoModal.innerHTML = html;
  }

  async function abrirVistaPrevia(area, archivo) {
    documentoActual = archivo;
    tituloModal.textContent = archivo;
    limpiarCuerpoModal();
    cuerpoModal.textContent = "Cargando...";
    modal.hidden = false;

    try {
      const respuesta = await fetch(
        "/documentos/" + encodeURIComponent(area) + "/" + encodeURIComponent(archivo)
      );
      if (!respuesta.ok) {
        const datos = await respuesta.json().catch(function () {
          return {};
        });
        limpiarCuerpoModal();
        cuerpoModal.textContent = datos.detail || "No se pudo generar la vista previa de este archivo.";
        return;
      }
      const datos = await respuesta.json();
      limpiarCuerpoModal();
      if (datos.tipo === "tabla") {
        renderizarTabla(datos.contenido);
      } else if (datos.tipo === "html") {
        renderizarHtml(datos.contenido);
      } else {
        renderizarTexto(datos.contenido);
      }
    } catch (error) {
      limpiarCuerpoModal();
      cuerpoModal.textContent = "No se pudo generar la vista previa de este archivo.";
      console.error("Error al consultar la vista previa:", error);
    }
  }

  function cerrarVistaPrevia() {
    modal.hidden = true;
    documentoActual = null;
  }

  botonCerrar.addEventListener("click", cerrarVistaPrevia);

  modal.addEventListener("click", function (evento) {
    if (evento.target === modal) {
      cerrarVistaPrevia();
    }
  });

  document.addEventListener("keydown", function (evento) {
    if (evento.key === "Escape" && !modal.hidden) {
      cerrarVistaPrevia();
    }
  });

  botonPreguntar.addEventListener("click", function () {
    if (documentoActual) {
      inputPregunta.value = "Cuéntame sobre el documento " + documentoActual;
    }
    cerrarVistaPrevia();
    inputPregunta.focus();
  });

  cargarAreas();
})();
