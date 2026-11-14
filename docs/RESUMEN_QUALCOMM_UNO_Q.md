# Resumen interpretativo: UPC Datathon – Qualcomm Challenge (Arduino UNO Q)

> **Fuente:** transcript del vídeo "UPC Datathon - Qualcomm Challenge step by step Arduino UNO Q setup"
> (ponente de Qualcomm; el nombre sale como "Maros" en el transcript). El `.txt` está en `origin/main`
> (commit `e44dad9`), **no en la rama `docs-skills-orchestrator`**. Para contrastar se usa
> [`CHALLENGE_CONTEXT.md`](../CHALLENGE_CONTEXT.md) (en `origin/main` está en `docs/`).
>
> **Cómo leer este documento:** el transcript es automático y tiene nombres deformados. Lo que **dice el vídeo**
> va tal cual; lo que es **interpretación mía** va marcado como *(inferido)*. Lo dudoso va marcado *(dudoso)*.

---

## TL;DR

- **Qué se pide:** un *math copilot* que corra **íntegramente en la Arduino UNO Q**, apoyado en el dataset **M3Kang** (problemas del Cangur).
- **Debe hacer una de dos cosas:** (a) enseñar matemáticas / mejorar la experiencia del estudiante, o (b) ayudar a razonar problemas nuevos o a entender por qué se fallan problemas concretos del Cangur.
- **Qué entregar:** repo de GitHub open source bien documentado, paso a paso en Arduino Project Hub y presentación.
- **Límite duro:** la placa lee a ~11 tok/s y escribe a ~5 tok/s, así que cada respuesta tarda 20–40 s. El modelo base acierta poco (el ponente dice que ~80 % de las veces falla).
- **Evaluación:** **el vídeo no da criterios explícitos.** Hay que preguntarlos a los organizadores (ver §4).

---

## 1. El reto

| Punto | Lo que dice el vídeo |
|---|---|
| Problema | La competencia matemática en Cataluña está bajando. Se quiere usar IA para ayudar a estudiantes, profesores o cualquiera. |
| Datos | **M3Kang**, modelo/dataset del equipo de Qualcomm Barcelona: casi **2.000 problemas** matemáticos de **2007 a 2024** del Cangur, traducidos a **108 idiomas** (el ponente dice 106 una vez). Alojado en Hugging Face. |
| Entregable técnico | Diseñar y construir un *math copilot* que **corra enteramente en la UNO Q**. |
| Restricción de propósito | Debe **o bien enseñar** a estudiantes, **o bien ayudar a razonar** problemas nuevos o por qué se fallan ciertos problemas del Cangur (p. ej. preparar las Proves Cangur). |

*(inferido)* El vídeo insiste en que lo más importante es **elegir un tema que dispare tu curiosidad** y después la tecnología. El reto es abierto: la
placa y el baseline son el punto de partida, no la solución.

---

## 2. Pasos del proyecto

El ponente habla de **12 pasos de setup + un paso 13 de ideas** ("en un par de horas lo tienes todo montado").
El transcript **no numera todos los pasos**; la numeración exacta está en el README de Qualcomm, que no tenemos.
Por eso describo la **acción** y solo cito sintaxis literal cuando es una herramienta estándar.
La numeración de la tabla es **mía** (orden en que aparece en el vídeo) y no coincide necesariamente con la del README.

| # | Acción | Por qué importa |
|---|---|---|
| 1 | Instalar **Arduino App Lab**, conectar la UNO Q por **USB-C**, ponerle nombre y **contraseña**, e introducir el WiFi de la UPC (**eduroam no funciona**). Actualizar SO y librerías. | La placa se fabricó hace meses: SO y librerías están desactualizados. **Si pierdes la contraseña no entras al dispositivo.** |
| 2 | Conectarse por **ADB** (`adb devices`, luego `adb shell`; con varias placas, `adb -s <id> shell`). SSH es la alternativa. | Es el canal de trabajo en el resto del vídeo. |
| 3 | `sudo apt-get update` e instalar paquetes de compilación. | Hacen falta compiladores para el siguiente paso. |
| 4 | Descargar un **commit concreto** de **llama.cpp**, compilarlo en la placa y comprobar versiones (`llama-server`, `llama-cli`). | Motor que ejecuta el modelo en CPU. |
| 5 | Descargar con `wget` desde Hugging Face **Qwen 3.5 0.8B** (~1 GB) y un **modelo de embeddings** (384 dimensiones). Nombre del modelo en el transcript: "VGA small" *(dudoso; 384 dim sugiere un modelo tipo bge-small, verificar en el README)*. | SLM para generar + embeddings para recuperar. |
| 6 | Arrancar `llama-server` en el puerto **8081** y probar la API de chat completions con "¿cuánto es 7×8?". Medir tiempos (en el vídeo: ~6 s de predicción y ~9 s de prompt). | Fija el baseline de velocidad. |
| 7 | Probar un problema real del Cangur con opciones A–E (enunciado omitido: los datos de M3Kang no se publican, ver la [dataset card](https://huggingface.co/datasets/qualcomm/M3Kang)). | Demuestra que el modelo base falla: elige una opción incorrecta. |
| 8 | Parar el servidor y arrancar el de **embeddings** en el puerto **8082**; comprobar que devuelve vectores de 384 números. | Base del RAG. |
| 9 | Dejar ambos modelos como **servicios systemd** para que arranquen solos. Nombres de servicio en el transcript: "mac lm" y "mac embed" *(dudoso, dejados como se oyen)*. | Evita lanzar `llama-server` a mano cada vez. |
| 10 | Clonar el **repo del datathon** en la placa y ejecutar el script de predicción (llamado `predict`) sobre problemas de ejemplo con salida a CSV. | Mide el baseline: se ve que el SLM tiende a contestar **A o D**. |
| 11 | **En el portátil:** crear un entorno virtual de Python, instalar requisitos, **descargar M3Kang** (~400 MB; el ponente limita a ~20 problemas para probar) y copiar los ficheros a la placa (`adb push` o `scp`). | Datos para construir embeddings y RAG. |
| 12 | Construir el **índice RAG** (demo con **13 problemas**) y probar el modo de recuperación (`rag1`): añade los problemas parecidos con su respuesta al prompt. | Si hay un problema similar la respuesta sale en **menos de 1 s**; si no, ~20 s. |
| 13 | **Interfaz web**: servidor Python en la placa (host `0.0.0.0`, puerto **8000**) para explorar problemas y consultar al modelo desde el portátil. | Hace el proyecto visual y demostrable. La hizo con IA agéntica. |
| 14 | *(Opcional)* **Problemas con imagen:** otro `llama-server` en el puerto **8083** con un *projector file*. | Muchos problemas del Cangur llevan imagen. |
| — | **Tu propio proyecto** (el "paso 13" del vídeo): implementar la idea elegida. | Es donde está el valor. |

**Cuidados operativos (dichos en el vídeo):**
- Al terminar, **`sudo poweroff`**. Si no, el `llama-server` puede quedar en estado zombi al reencender (hay que localizarlo con `ps` y matarlo).
- Vigilar la **memoria** disponible.
- Tener **dos terminales** abiertas (servidor + pruebas) ayuda.

---

## 3. Criterios de evaluación

### Lo que el vídeo NO dice
**No hay una rúbrica explícita**: ni pesos, ni jurado, ni métricas obligatorias. Cualquier lista de "criterios oficiales" sería inventada.

### Lo que el ponente enfatiza *(inferido: son señales, no reglas)*
1. **Curiosidad e idea propia:** "lo más importante es que elijas un tema que despierte tu curiosidad".
2. **Documentación y replicabilidad:** pide explicar todo en el repo (qué problemas descargaste, cómo entrenaste, por qué haces el proyecto). "Cualquiera en el mundo debería poder replicarlo."
3. **Innovación sobre el baseline:** el sistema base falla mucho; ahí es donde "aplicar innovación y creatividad".
4. **Que funcione dentro de la placa:** el copilot debe correr en la UNO Q.

### Métricas propuestas por el equipo (**NO oficiales**)
De `CHALLENGE_CONTEXT.md` (§7): exactitud en un conjunto Kangaroo reservado, score pedagógico (MathTutorBench / MRBench, **sin verificar cuál**), comprobaciones de generación (idioma, longitud, alucinaciones) y métricas en placa (tok/s, tiempo al primer token, RAM). Es un arnés de trabajo del equipo, no una exigencia del reto.

### Pregunta pendiente para los organizadores
¿Hay rúbrica oficial? ¿Qué peso tiene la demo frente al repo? ¿Hay límites de tamaño de modelo, de datos externos o de datos sintéticos?

---

## 4. Recursos disponibles

| Tipo | Recurso |
|---|---|
| **Hardware** | Arduino UNO Q conectada por USB-C (Mac/Windows/Linux). **No** hay Arduino Ventuno Q (40 TOPS): "quizá en el próximo datathon". Matriz LED de la UNO Q. Micrófono/webcam/hub USB: **hay que pedirlos a los organizadores**. |
| **Software** | Arduino App Lab, ADB, llama.cpp, Qwen 3.5 0.8B, modelo de embeddings. |
| **Datos** | M3Kang en Hugging Face (dataset y paper), ~400 MB. |
| **Repo de Qualcomm** | Contiene el README paso a paso, el script de predicción, el indexador RAG, la interfaz web, herramientas de medición y análisis de errores y ejemplos de matriz LED. La URL **no sale en el vídeo**: pedirla a organizadores o a Qualcomm. |
| **Skills para agentes** | Carpeta de *skills* en el repo para que tu agente de IA sepa: usar la UNO Q, construir apps para ella, usar el modelo de embeddings, el hardware, y redactar el proyecto para Project Hub. Recomendación: **copiarlas a tu propio repo**. |
| **Referencias** | Tutorial de un profesor chileno (Qualcomm ambassador, da clases también en Brasil/LatAm) sobre RAG con SLM en Arduino. Nombre del transcript: "Marel Rob" *(dudoso; probable Marcelo Rovai, verificar)*. Artículo del propio ponente sobre LLM/VLM en la UNO Q con Go. Proyecto "Island Sword Fight" en su GitHub (keyword spotting). |
| **Contacto** | El ponente ofrece contacto por LinkedIn y por correo (el correo en el transcript es ambiguo, no lo copio). |

---

## 5. Trabajo a realizar

**Checklist en orden** *(inferido a partir de los pasos y entregables)*:

- [ ] Completar el setup (pasos 1–10) y **medir el baseline** (tiempos y acierto).
- [ ] Descargar M3Kang y construir el RAG con **más de 13 problemas** (inglés y catalán).
- [ ] **Elegir la idea** y decidir cuál de las dos funciones cubre (enseñar o razonar/diagnosticar fallos).
- [ ] Implementar la idea sobre la base (RAG + interfaz web).
- [ ] **Documentar mientras se construye.**
- [ ] Publicar el **repo de GitHub open source** (qué problemas, cómo se entrenó/indexó, por qué).
- [ ] Publicar el **paso a paso en Arduino Project Hub** (hay una skill para redactarlo).
- [ ] **Presentación.** El vídeo dice "la presentación del domingo" y "te veo el lunes": **fecha ambigua, confirmar**.

**Ideas que propone el ponente (paso 13):**
1. **Problema parecido más fácil:** si el estudiante se atasca, el copilot busca (por embeddings) un problema similar pero más sencillo.
2. **Caja de debate en clase:** se proyecta un problema, los alumnos votan A–E desde el móvil, botón o voz, y la UNO Q valida la respuesta. Interfaz web en Python.
3. **Puente multilingüe / simplificación de enunciados:** reescribir el texto de forma más simple (p. ej. ayuda para personas con dislexia).
4. **Keyword spotting A–E por voz:** reconocer "a, b, c, d, e" con un modelo local y mostrar acierto/fallo en la matriz LED (rojo/verde). Requiere micrófono.
5. **Problemas con imagen:** leer imágenes con el projector file (puerto 8083).

---

## 6. Lectura interpretativa

1. **El cuello de botella es la velocidad, no solo el acierto.** ~5 tok/s implica 20–40 s por respuesta. Todo lo que evite generar o acorte la generación gana mucho.
2. **El RAG es el camino que Qualcomm demuestra y la palanca más barata.** Con solo 13 problemas indexados, una pregunta parecida se respondió en menos de 1 s. Con el dataset completo la ganancia debería crecer *(inferido)*.
3. **El diferencial está en la idea y la experiencia, no en un modelo mayor.** La placa no da para más: el valor está en cómo se usa el copilot (debate en clase, accesibilidad, diagnóstico de fallos).
4. **El ponente valora la documentación casi tanto como el resultado.** Repo, Project Hub y presentación aparecen como entregables, y repite que "todo debe poder replicarse".
5. **Divergencia con el plan del equipo.** `CHALLENGE_CONTEXT.md` parte de afinar/podar/cuantizar un modelo Gemma; el vídeo demuestra un camino distinto (Qwen 3.5 0.8B + embeddings + RAG sin reentrenar). No son excluyentes, pero conviene **decidirlo conscientemente**:

   | Punto | Vídeo | `CHALLENGE_CONTEXT.md` |
   |---|---|---|
   | Nº de problemas | ~2.000 (M3Kang, 108 idiomas) | ~1.000 |
   | Enfoque | RAG + embeddings sobre Qwen 3.5 0.8B | Fine-tune, poda, cuantización de Gemma |
   | Servidor | `llama-server` en 8081 / 8082 / 8083 | LLM Brick de App Lab (puerto 9999) |

---

## 7. Incertidumbres a verificar

- **Criterios de evaluación:** no existen en el vídeo; preguntar a los organizadores.
- **Fecha de la presentación:** "domingo" y "lunes" son ambiguos.
- **URL y README del repo de Qualcomm:** no salen en el transcript; ahí están los comandos exactos y la numeración real de los pasos.
- **Nombres deformados por el transcript automático:** modelo de embeddings ("VGA small"), servicios systemd ("mac lm" / "mac embed"), profesor chileno ("Marel Rob"), "Dathlon", "provis kangur".
- **Cifras:** 108 vs 106 idiomas; "casi 2.000" problemas (≈) frente a ~1.000 en el contexto del equipo.
- **Variante de la placa (2 GB o 4 GB):** el vídeo dice que "necesitarás mucha memoria", pero no indica la variante.
