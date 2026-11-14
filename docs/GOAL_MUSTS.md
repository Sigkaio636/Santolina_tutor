# GOAL_MUSTS: qué hay que cumplir

Lista única de lo que el reto pide al equipo. Cada ítem cita su fuente para poder comprobarlo.
Lo que no sale de las fuentes se marca con ⚠️ y está en [Pendientes](#4-pendientes-de-confirmar-con-los-organizadores).

Fuentes:

- [`BOARD_SETUP.md`](BOARD_SETUP.md): README de los organizadores (Deliverables, pasos 14 y 15).
- [`.claude/skills/publish-project/SKILL.md`](../.claude/skills/publish-project/SKILL.md): estructura del README y del Project Hub.
- [`CHALLENGE_CONTEXT.md`](CHALLENGE_CONTEXT.md) y [`RESUMEN_QUALCOMM_UNO_Q.md`](RESUMEN_QUALCOMM_UNO_Q.md): contexto del equipo.

> **No hay rúbrica oficial.** Ni pesos, ni jurado, ni métricas obligatorias (`RESUMEN_QUALCOMM_UNO_Q.md` §3). Esta lista recoge lo que se pide; no dice cuánto puntúa cada cosa.

---

## 1. Checklist de obligatorios

### 1.1 El reto

- [ ] El copiloto **corre entero en la Arduino UNO Q**, sin salir del dispositivo. (`BOARD_SETUP.md`, The challenge)
- [ ] **Usa M3Kang** de una forma propia. (`BOARD_SETUP.md`, The challenge)
- [ ] Cubre **al menos una** de las dos funciones:
    - [ ] **Teach**: guía al estudiante sin dar la respuesta (pistas, práctica adaptativa, análisis de errores, interacción física, colaboración).
    - [ ] **Reason**: dado un problema tipo Kangaroo, elige la respuesta correcta. Los organizadores lo miden en un conjunto de test oculto.
- [ ] Si se elige **Reason**: el `predict.py` de la raíz respeta el contrato de los organizadores. (`CLAUDE.md`)
- [ ] ⚠️ Si se elige **Reason**: hipótesis de trabajo, **no confirmada**: el test oculto trae solo preguntas de texto, en varios idiomas. Ver la evidencia en [4.1](#41-test-oculto-formato-esperado).

### 1.2 Repositorio de GitHub público

- [ ] El repositorio es **público** y de código abierto. (`BOARD_SETUP.md`, Step 15.1)
- [ ] Contiene **todo lo necesario para correr el copiloto en una UNO Q nueva**:
    - [ ] `config.env` con repositorio, revisión, fichero y SHA256 de cada modelo, y el commit de llama.cpp.
    - [ ] Los ficheros de servicio.
    - [ ] La app de App Lab, si existe.
- [ ] Tiene una **licencia** para el código propio (por ejemplo MIT) y los créditos de lo reutilizado.
- [ ] **No contiene datos de M3Kang**: ni `train.jsonl`, `val.jsonl`, imágenes, `index.db`, ni modelos `*.gguf`. Se enlaza la [dataset card](https://huggingface.co/datasets/qualcomm/M3Kang) en su lugar. (Red line 1 de `CLAUDE.md`)
- [ ] `git status` revisado antes de cada push.

### 1.3 README (en este orden)

- [ ] **Qué hace**, en dos o tres frases, con foto o vídeo corto funcionando en la placa.
- [ ] **Arquitectura**: qué corre en Linux, qué corre en el microcontrolador, cómo los conecta el Bridge, qué servidores de modelo usa y cómo usa M3Kang.
- [ ] **Cómo replicarlo**, paso a paso, desde una placa preparada con los pasos 0 a 12, con los comandos y lo que se debe ver.
- [ ] **Resultados**: tabla de `results/ablations.csv`, cada experimento frente al baseline, con exactitud, latencia media y peor, y número de problemas.
- [ ] **Análisis de errores** por **tema**, **idioma** y **dificultad (nivel)**, con el número de problemas junto a cada exactitud y algunas respuestas erróneas explicadas.
- [ ] **Qué no funcionó** y qué se probaría después.
- [ ] **El equipo**.

### 1.4 Paso a paso en Arduino Project Hub

- [ ] Proyecto creado en [Arduino Project Hub](https://projecthub.arduino.cc/) con cuenta de Arduino. (`BOARD_SETUP.md`, Step 15.2)
- [ ] Secciones:
    - [ ] **Introducción**: a quién ayuda, por qué corre offline, foto o vídeo.
    - [ ] **Componentes y apps**: UNO Q 4 GB, App Lab, llama.cpp y los modelos.
    - [ ] **Arquitectura**: diagrama de las dos mitades de la placa, el Bridge, los servidores de modelo y dónde entra M3Kang.
    - [ ] **Paso a paso**: de una placa nueva a la demo, con comandos y resultado esperado. Enlaza al repo en vez de pegar todo el código.
    - [ ] **Resultados y análisis de errores**.
    - [ ] **Qué hemos aprendido** y qué sigue.
- [ ] Fotos y capturas **hechas por el equipo**.
- [ ] **Cita de M3Kang** (Torres-Camps et al., 2026, [arXiv:2601.16218](https://arxiv.org/abs/2601.16218)).
- [ ] No se suben datos de M3Kang. Para mostrar un ejemplo de problema, se mira antes la licencia de la dataset card.

### 1.5 Demo en vivo y pitch

- [ ] **Demo en vivo en la placa.** (`BOARD_SETUP.md`, Deliverables)
- [ ] **Pitch de 3 minutos**, con esta estructura sugerida:
    - [ ] Problema (20 s)
    - [ ] Demo (90 s)
    - [ ] Números: exactitud frente al 22,5 % del baseline, latencia, análisis de errores (40 s)
    - [ ] Qué aprendimos (30 s)
- [ ] La demo corre como la verá el jurado: **Wi-Fi apagado**, servicios arrancados al inicio, nada en el portátil haciendo el trabajo. Si hay una página web en el portátil, conexión por USB con `adb forward`.
- [ ] Problemas de la demo **elegidos de antemano** y probados en la placa el mismo día.
- [ ] **Al menos dos ensayos con cronómetro.**
- [ ] **Vídeo corto de la demo funcionando**, por si falla en el escenario.

### 1.6 Verificación antes de compartir

- [ ] Cada número del README sale de una ejecución registrada en `ablations.csv`, con los problemas indicados. Si son 50 o menos, se dice.
- [ ] Referencia de baseline: **22,5 % sobre 40 problemas en inglés con opciones por OCR**.
- [ ] Se clona el repositorio en una carpeta nueva y se sigue el README. Se arregla cada paso que falle.
- [ ] Todos los enlaces funcionan.
- [ ] **Se envían a los organizadores los dos enlaces**: repositorio y Project Hub.

---

## 2. Campos abiertos, subjetivos y creativos

Aquí las fuentes no fijan un resultado ni un criterio. El equipo decide, y nadie ha dicho cómo se puntúa. La columna de la derecha es una propuesta de cómo reducir el riesgo, no una regla del reto.

| Campo | Por qué es abierto | Qué decide el equipo | Cómo reducir el riesgo |
|---|---|---|---|
| **Uso de M3Kang** | "Depende de ti": base de conocimiento para recuperación, entrenamiento, embeddings, mapa de dificultad, puente multilingüe "o algo que nadie ha pensado". "Los usos más originales puntuarán más." | Qué papel tiene M3Kang y por qué. | Explicarlo en la arquitectura del README y en el pitch, y medir su efecto con un experimento en `ablations.csv`. |
| **Teach o Reason** | Basta una de las dos. Reason se mide con un test oculto; Teach no tiene métrica definida. | Cuál se cubre, o si se cubren ambas. | Si es Teach, definir antes cómo se comprueba que "guía sin dar la respuesta". |
| **La idea y la experiencia** | La charla propone ideas (problema parecido más fácil, caja de debate en clase, simplificación de enunciados, voz A–E con matriz LED, problemas con imagen). Son inspiración, no una lista cerrada. | Qué experiencia vive el estudiante. | Elegir una y llevarla hasta la demo antes que tocar varias a medias. |
| **Enfoque técnico** | El vídeo demuestra RAG con embeddings sobre Qwen 3.5 0.8B; `CHALLENGE_CONTEXT.md` plantea afinar, podar y cuantizar un Gemma. No son excluyentes. | Qué camino y en qué orden. | Decidirlo de forma consciente y dejar el motivo escrito. |
| **Calidad pedagógica** | No hay benchmark oficial. `CHALLENGE_CONTEXT.md` §7 sugiere MathTutorBench o MRBench, sin verificar. Es un arnés del equipo, no una exigencia. | Qué es "buena explicación" y cómo se mide. | Evaluar generación abierta, no solo acierto A–E: la poda y la cuantización pueden romper la generación sin bajar la exactitud tipo test. |
| **Hardware e interfaz** | La matriz LED 8×13 es la única salida de hardware. App Lab, página web y voz son opcionales. | Si hay interfaz y de qué tipo. | Priorizar lo que funcione en la placa sin portátil. |
| **Idioma** | El idioma de respuesta no está confirmado. | En qué idiomas habla el copiloto. | Confirmar con los organizadores y medir el error por idioma. |
| **Narrativa y redacción** | El ponente valora la documentación casi tanto como el resultado y repite que "todo debe poder replicarse". | Cómo se cuenta el proyecto, incluido lo que falló. | Escribir para un estudiante que no estuvo en el datathon, con frases cortas, y contar lo que no funcionó igual de claro. |
| **Demo y pitch** | Se juzga en directo, con criterio humano. | Qué problemas, qué orden y qué se destaca. | Ensayar con cronómetro y llevar el vídeo de respaldo. |

---

## 3. Fuera de alcance de esta lista

No se han inventado pesos, puntuaciones ni plazos. Si el jurado publica una rúbrica, sustituye a la sección 2.

---

## 4. Pendientes de confirmar con los organizadores

- [ ] ⚠️ **Rúbrica y jurado**: no existen en el vídeo ni en el README. (`RESUMEN_QUALCOMM_UNO_Q.md` §3)
- [ ] ⚠️ **Fecha de la presentación**: el vídeo dice "domingo" y "te veo el lunes".
- [ ] ⚠️ **Idioma(s) de respuesta** del copiloto. (`CHALLENGE_CONTEXT.md` §7)
- [ ] ⚠️ **Benchmark pedagógico** concreto y si hay script oficial de evaluación. (`CHALLENGE_CONTEXT.md` §7)
- [ ] ⚠️ **URL del repositorio de Qualcomm**: no sale en el vídeo. (`RESUMEN_QUALCOMM_UNO_Q.md`)
- [ ] ⚠️ **Formato del test oculto**: ver [4.1](#41-test-oculto-formato-esperado).

### 4.1 Test oculto: formato esperado

**Hipótesis de trabajo:** el test oculto de **Reason** trae solo preguntas de texto, en varios idiomas.

**Ninguna fuente lo dice.** Es una lectura de pistas indirectas. Revisión hecha el 2026-11-14 sobre los documentos del repositorio y sobre el README de los organizadores en GitHub. Su último commit es `d6e3f1b`, el mismo que copia [`BOARD_SETUP.md`](BOARD_SETUP.md).

| Qué se espera | Evidencia | Fuente |
|---|---|---|
| **El test existe y es oculto** | "Organizers will measure this objectively on a hidden test set." Se puntúa el `predict.py` de cada equipo. | `BOARD_SETUP.md`, The challenge (línea 38) y 13.3 (línea 1093). `OCR_FAILURE_MODES.md` línea 151. |
| **Solo texto** | La entrada de `predict.py` es un JSONL con `id`, `text`, y `options` y `language` "cuando estén disponibles". No hay campo ni argumento para imagen. `solve()` acepta `image_b64`, pero `predict.py` nunca se lo pasa. | `predict.py`, docstring (líneas 7 a 9) y `copilot/pipeline.py` |
| **Solo texto** | La imagen es un experimento del explorer: con la imagen reducida cuesta 28 a 38 s por problema, y con la completa no cabe en los 60 s. | `BOARD_SETUP.md`, "Let the model see the image" (líneas 975 a 1009) |
| **Varios idiomas** | El CSV de salida lleva la columna `language`. M3Kang tiene 108 idiomas con el mismo `id`. | `predict.py`; `BOARD_SETUP.md` líneas 715 a 754 |
| **Varios idiomas** | `eval.py` mide por idioma. El entregable pide error por tema, idioma y dificultad. | `BOARD_SETUP.md` líneas 46 y 855 |

**Lo que no cubre la evidencia:**

- Ningún texto dice "solo texto". La descripción del reto dice "Kangaroo-style problem", no "problemas de M3Kang". (`BOARD_SETUP.md`, línea 38)
- En M3Kang, las opciones A a E están solo en la imagen. Si el test trae solo `text`, las `options` pueden venir vacías. Entonces "solo texto" no significa "con opciones". (`BOARD_SETUP.md`, línea 717)
- Si el test fuera una muestra aleatoria de M3Kang, más de la mitad de las filas necesitaría una figura: 440 de 789 en nuestra validación. (`docs/experiments/2026-11-decider-0.8b.md`, líneas 119 y 120)
- No hay lista de idiomas del test. Los datos locales solo tienen `eng`, `cat` y `esp`.

**Qué hacer:**

- Preguntar a los organizadores: ¿el test trae `options` rellenas o vacías? ¿Hay campo de imagen? ¿Qué idiomas incluye?
- Mientras llega la respuesta, no apoyar el sistema en la imagen. Probar el caso sin `options` y varios idiomas, con `eval.py`.
