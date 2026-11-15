# Diseño de la matriz LED

Este documento fija qué muestra la matriz LED 8x13 de la UNO Q y cómo se
calcula. Va dirigido a quien implemente la interfaz (app de App Lab,
`python/main.py` y `sketch/sketch.ino`). La parte técnica de la matriz (el
Bridge, `Frame`, el sketch) está en la skill
[`unoq-hardware-ui`](../.claude/skills/unoq-hardware-ui/SKILL.md).

La matriz tiene dos pantallas. En reposo muestra el mapa de dominio del alumno
y el porcentaje de deberes hechos. Mientras el modelo trabaja muestra una barra
que avanza con los tokens que genera.

## Restricciones

- 8 filas por 13 columnas, brillo de 0 a 7 (`setGrayscaleBits(3)`).
- Nada parpadea más de 3 veces por segundo.
- La matriz nunca muestra la respuesta de un problema ni nada que la delate.
- Python decide cada fotograma y el sketch solo lo dibuja, como en el ejemplo
  oficial `02-led-matrix-frame`.

## Pantalla de reposo

```text
columna:  0  1  2  3  4  5  6  7  8  9 10 11 12
          ar al nt co lo ge sp me pa    [deberes]
fila 0    .  .  .  .  .  .  .  .  .     #  #  #   nivel 7
fila 1    .  .  .  .  .  .  .  .  .     #  #  #   nivel 6
...                                                ...
fila 7    ▓  █  ▒  .  ▓  .  .  ░  .     #  #  #   nivel 0
```

### Mapa de dominio (columnas 0 a 8)

- Cada columna es uno de los 9 temas de `santolina_tutor/topics.py`, en este
  orden fijo: `arithmetic`, `algebra`, `number_theory`, `counting`, `logic`,
  `geometry`, `spatial`, `measurement`, `patterns`.
- Cada fila es un nivel de Canguro. El nivel 0 va en la fila de abajo (fila 7)
  y el nivel 7 en la de arriba (fila 0), de modo que el mapa se llena de abajo
  arriba.
- El brillo de una celda da el dominio del alumno en ese tema y ese nivel:
  - celda sin intentos: apagada (brillo 0), para distinguir "no lo ha probado"
    de "lo ha probado y falla";
  - celda con intentos: `brillo = 1 + round(6 * dominio)`, de 1 a 7.
- `dominio` es la fracción de aciertos sin pista en los 5 últimos intentos de
  esa celda. Un acierto con pista cuenta como medio acierto.
- El tema de cada problema sale de `data/topics/topics.jsonl` (campo `topic`),
  y el nivel, del id (`lvl-L_AAAA_P`). Ese fichero está en la placa, nunca en
  Git.

### Deberes hechos (columnas 10 a 12)

- La columna 9 queda apagada para separar el mapa de la barra.
- Las columnas 10 a 12 forman una barra de 3x8 = 24 celdas que se llena de
  abajo arriba, de izquierda a derecha en cada fila.
- `porcentaje = problemas terminados / problemas de los deberes`. Un problema
  está terminado cuando el alumno envía una respuesta final, acierte o no.
- Cada celda vale 1/24 (unos 4 %). Las celdas llenas van a brillo 7 y la
  celda a medio llenar toma un brillo proporcional a su parte llena (de 1 a 6).
- Con los deberes completos, la barra entera se queda encendida, fija y sin
  animación.

## Pantalla "pensando"

Una llamada al modelo tarda de 5 a 30 s. La barra solo avanza cuando el modelo
genera texto, así que mide el progreso real.

- Ocupa toda la matriz. Se llena en orden de lectura (fila 0 de izquierda a
  derecha, luego la fila 1, etc.), un LED por token generado, hasta 104.
- Si se esperan más de 104 tokens, cada LED vale `max_tokens / 104` tokens. Si
  la respuesta termina antes de llenar la barra, la barra se completa y se
  vuelve a la pantalla de reposo.
- Durante el prefill todavía no llega ningún token. Entonces la primera fila
  "respira": su brillo sube y baja una vez por segundo como mucho. Así el
  alumno ve que la placa no está colgada.
- Hay que pedir al servidor de llama.cpp las respuestas en streaming
  (`"stream": true` en `/v1/chat/completions`) y contar los fragmentos que
  llegan (ver las notas de implementación).
- La matriz se actualiza como mucho cada 250 ms, para no saturar el Bridge.

## Notas para la implementación

- Streaming. `copilot/` no usa streaming todavía (`copilot/llm.py` y
  `copilot/client.py` esperan la respuesta completa). La barra "pensando"
  necesita un cliente nuevo con `"stream": true` o un parámetro opcional en el
  cliente actual. `predict.py` debe seguir funcionando sin la app y sin la
  matriz.
- Temas. `data/topics/topics.jsonl` tiene una línea por problema con `id`,
  `level` y `topic`. Se generó en el portátil y no está en Git (regla de
  M3Kang), así que hay que copiarlo a la placa a mano junto al resto de datos.
  El id es el mismo en todos los idiomas, así que la búsqueda por id sirve para
  un problema en catalán o en castellano. Un problema sin tema cuenta para los
  deberes pero no para el mapa.
- Log de sesiones. Su formato aún no está definido. El mapa y las métricas
  necesitan, por cada intento: id del problema, fecha y hora, pistas usadas,
  si acertó y si la respuesta era final. Por cada llamada al modelo: tiempo
  hasta el primer token y tokens por segundo. El log guarda ids, nunca el
  texto del problema.
- Leyenda. La matriz no tiene sitio para los nombres de los temas. La
  página web debe mostrar la leyenda de las columnas y los niveles.
- Brillo. Hay que comprobar en la placa que el brillo 1 se distingue de
  apagado con luz de aula. Si no, la escala de dominio empieza en 2.

## Qué medir

- En el mapa: la evolución del dominio por tema y nivel a lo largo de una
  semana, sacada del log de sesiones que el profe descarga.
- En los deberes: el porcentaje terminado al recoger la placa.
- En la barra "pensando": el tiempo hasta el primer token y los tokens por
  segundo de cada llamada, que también van al log.

Ninguna de estas cifras necesita texto de problemas. El log guarda ids de
problema, temas, niveles, aciertos y tiempos.
