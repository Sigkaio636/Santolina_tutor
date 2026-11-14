# Crítica: dispersión esperanza de vida × fertilidad, seis países pequeños, 1955–2005

**Entrada**: `bad_gapminder.json` (spec Vega-Lite v5 exportada desde Altair), idioma: *bubble chart* (dispersión con tamaño), marca `square` con `clip: true`.
**Datos**: 32 filas. Claves: `country` (nominal, 6: Aruba, Granada, Islandia, Israel, Jamaica, Líbano) y `year` (ordinal/temporal, 6 niveles: 1955, 1965, …, 2005). Valores: `life_expect` (cuantitativo, años; 58,0–81,2), `fertility` (cuantitativo, hijos por mujer; 1,8–6,7), `pop` (cuantitativo, personas; 53 865–6 720 000, razón 125×). Aruba y Granada no tienen 1965 ni 1985 (4 puntos en vez de 6).
**Propósito asumido**: el usuario no lo dice. Por el contexto (informe interno, datos tipo Gapminder) asumo modo **explicativo/análisis** para los lectores del informe: (1) seguir la trayectoria demográfica de cada país en 50 años, (2) compararlas entre países (quién parte de más atrás, quién converge), (3) ver la relación esperanza de vida ↔ fertilidad. La población no forma parte de la pregunta enunciada.

## Veredicto

Hoy el gráfico tiene valor negativo: no se puede saber qué punto es de qué país (el canal `shape` se descarta en silencio con la marca `square`, no hay leyenda de país ni tooltip), el dominio forzado `[0, 80]` con `clip` elimina el mejor dato de la serie (Islandia 2005, 81,2 años) y deja el 71 % del eje x vacío, el tiempo va en una paleta categórica que pierde el orden, y la población, que no forma parte de la pregunta, decide qué puntos se ven: los tres países más pequeños (justamente "los países pequeños" del proyecto) son puntos de 1–3 px. Con estos datos un lector aprende menos que con una tabla de 6 × 6 pares. Sin embargo, la visualización sí está justificada: seis trayectorias de 50 años son exactamente lo que una dispersión conectada (o seis miniaturas) muestra y una tabla esconde. El cambio que más valor recupera: codificar el país (color + trazo que una sus puntos en orden de año + etiqueta directa) y quitar el dominio forzado.

## Scorecard de valor (V = T + I + E + C)

| Componente | Nota | Por qué |
|---|---|---|
| T · Tiempo | 0/3 | Recuperar un valor ("¿cuánta fertilidad tenía Jamaica en 1965?"): imposible, el país no está codificado. Tendencia por país: imposible. Extremo ("¿quién alcanza más esperanza de vida?"): respuesta **incorrecta**, el máximo real (81,2) está recortado y el lector contesta "80". Rango: trabajo, y en x falso. Correlación: inmediata pero exagerada (nube comprimida en el 30 % del eje). Filtrar por año: trabajo de leyenda con 6 tonos. Anomalías (el pico de fertilidad 4,2 → 5,8 → 4,0 de Jamaica en 1965): visible como punto suelto, inatribuible. |
| I · Insight | 0/3 | Lo único que se ve (correlación negativa esperanza de vida–fertilidad) es un hecho de manual que no necesita estos datos. Lo que estos datos sí aportan (la transición demográfica de cada país, la convergencia hacia ~2 hijos y 70–80 años, Israel manteniendo 2,8 hijos con 80 años de esperanza, el pico de Jamaica) está oculto. Los hallazgos críticos limitan I ≤ 1. |
| E · Esencia | 1/3 | Impresión a cinco segundos: "una nube de cuadrados de colores en la esquina derecha, bajando". Sin título que la ancle; el mensaje pretendido (seis países convergen en 50 años) no llega. |
| C · Confianza | 0/3 | Dato recortado, eje que afirma que 80 es el techo, sin fuente, sin unidades, nombres de variable crudos, años ausentes de Aruba y Granada sin declarar (el lector no sabe si son 4 puntos por falta de datos o por decisión). Un lector escéptico no se fía, y con razón. |

Expresivo: **no** (pierde la clave país, pierde el orden del año, recorta datos). Efectivo: **no** (atributo principal sin canal; tiempo en tono; tres leyendas; población domina el peso visual; rojo–verde). Apropiado: **no** en su estado actual (una tabla 6 × 6 gana); **sí** con el rediseño (trayectorias que la tabla no muestra).

## Hallazgos

### Críticos (engañan o bloquean la tarea principal)

- **[PUR-01 / EXP-01]** El país, la clave principal, no está codificado. Evidencia: `mark: square` + `encoding.shape = country`; Vega-Lite avisa en consola `shape dropped as it is incompatible with "square"` y el render no tiene leyenda de país (solo `year` y `pop`). No hay `tooltip`. Consecuencia: las tareas (1) y (2) son imposibles; el gráfico muestra 32 puntos anónimos. Es un hecho determinista. Arreglo: país → color (6 tonos cualitativos, seguros para daltonismo) + trazo `line`/`trail` con `order: year` que una los puntos de cada país + etiqueta directa en el extremo 2005. Si se quería la forma, la marca tiene que ser `point`, pero con 6 países la forma es un canal débil (EFF-08: > 4 formas); mejor color y etiquetas.
- **[EXP-09 / SCL-05 / TRUNC-11]** Dominio forzado `x: [0, 80]` con `clip: true`. Evidencia determinista: datos 58,0–81,2; Islandia 2005 (81,2) desaparece; Israel 2005 (80,0) queda partido en el borde; razón datos/eje = 23,2/80 = 29 % (< 50 %), es decir, el 71 % del eje está vacío. Consecuencia: el lector lee un máximo falso (80), pierde el punto más destacable de la serie, y la nube comprimida horizontalmente exagera la pendiente y la fuerza de la correlación. Arreglo: eliminar `scale.domain` y `clip`; dejar x en ~[55, 85] (una dispersión no necesita el cero, SCL-02: hacerlo visible con los ticks) o `domain: [55, 85]` explícito; y en todo caso nunca recortar datos: si se fuerza un dominio, que contenga los datos.
- **[EXP-02 / COL-02]** El año (ordenado, 6 niveles equiespaciados) va en tono categórico `category10`. Evidencia: `color: year:nominal, scheme category10`. Consecuencia: el orden temporal no existe en el gráfico; para saber si un punto es anterior a otro hay que consultar la leyenda y recordar la secuencia azul → naranja → verde → rojo → morado → marrón (6 chunks, por encima de la memoria de trabajo). La dirección del cambio, que es el mensaje de todo gráfico tipo Gapminder, es invisible. Excepción de la regla (≤ 3 niveles o el orden lo lleva x): no aplica, x es esperanza de vida. Arreglo: el tiempo se lleva con la conexión ordenada de los puntos (Gestalt de conectividad) y un marcador de inicio/fin; si se quiere color para el año, paleta secuencial de luminancia (`viridis`, `blues`) y `year:ordinal`.

### Mayores (frenan la tarea, esconden insight, pierden lectores)

- **[EFF-02 / EFF-16 / IDM-SCATTER]** La población en área manda sobre todo lo demás sin ser parte de la pregunta. Evidencia: `size: pop:quantitative`, razón 125× entre Aruba 1955 y Israel 2005; Vega-Lite escala el área desde cero, así que Aruba, Granada e Islandia (10 de 32 puntos) se dibujan como puntos de 1–3 px (ver render), mientras que 11 puntos de Israel, Líbano y Jamaica se amontonan y ocluyen en la caja 70–77 × 1,8–3,2. Consecuencia: los "países pequeños" del proyecto son los que desaparecen; el área se lee con exponente ≈ 0,7 (Stevens) y nadie va a comparar poblaciones aquí. Arreglo: quitar `size` (dejar `pop` en el tooltip) o, si la población es parte del mensaje, `scale.range: [40, 400]` con opacidad 0,7 y borde, aceptando que las áreas solo dan una impresión.
- **[EFF-11 / EFF-08]** Carga de memoria y búsqueda conjuntiva. Evidencia: dos leyendas renderizadas (6 entradas de año + 7 de población, con una entrada "0" absurda) y una tercera prevista (6 formas de país). Localizar "Israel en 1985" exigiría rojo AND forma-Israel: búsqueda serial, no preatentiva; y la forma ni siquiera existe. Arreglo: una sola leyenda (país) o ninguna (etiquetas directas al final de cada trazo).
- **[COL-05 / ACC-01]** Paleta rojo–verde sin segunda pista. Evidencia determinista: `category10` contiene `#2ca02c` (1975) y `#d62728` (1985); simulación de deuteranopia: 1965/1975/1985/2005 colapsan en amarillos-marrones y 1955/1995 en azules (ΔE simulado 7–8 para los pares #2ca02c/#d62728 y #1f77b4/#9467bd); la forma que haría de segunda pista está descartada. Consecuencia: un 8 % de lectores varones no distingue la mitad de los años. Arreglo: la paleta secuencial o la conexión ordenada del hallazgo anterior lo resuelve de paso.
- **[COL-08 / ACC-04]** No funciona en blanco y negro. Evidencia: en la versión en escala de grises los seis años son el mismo gris medio. Consecuencia: impreso o fotocopiado, el gráfico pierde su única codificación del tiempo. Arreglo: luminancia secuencial para el año, o el tiempo en la geometría (trazo).
- **[EFF-12 / CMP-03]** Los puntos de un mismo país no están conectados ni adyacentes; la trayectoria hay que reconstruirla mentalmente emparejando colores con la leyenda en orden. Consecuencia: "ojos antes que memoria": lo que una línea daría en 200 ms exige seis consultas de leyenda por país. Arreglo: `mark_line(point=True)` con `order=year` (dispersión conectada) o `mark_trail`.
- **[TXT-01 / TEXT-1 / PUR-04]** Sin título. Evidencia: ninguna propiedad `title` en la spec. Consecuencia: el lector no sabe qué, dónde, cuándo; para un gráfico explicativo es una violación de esquema y el elemento más recordado desaparece. Arreglo: título con el mensaje, subtítulo con población/periodo/unidades.
- **[SCL-06 / TXT-03]** Títulos de ejes y leyendas son nombres de campo crudos sin unidades. Evidencia: `life_expect`, `fertility`, `pop`, `year`. Arreglo: "Esperanza de vida al nacer (años)", "Fertilidad (hijos por mujer)", "Población (habitantes)".
- **[TXT-08 / PUR-09 / DAT-03]** Sin fuente, sin n, sin declarar los datos faltantes. Evidencia: Aruba y Granada tienen 4 filas (faltan 1965 y 1985) y nada lo dice; sin nota de fuente (Gapminder/ONU). Consecuencia: C = 0; un lector atento ve 4 puntos frente a 6 y no sabe si es dato o descuido. Arreglo: pie "Fuente: Gapminder. Aruba y Granada sin datos en 1965 y 1985" y, en el trazo, tramo discontinuo o hueco donde falta el año.
- **[INT-01 / INT-03]** Ninguna interacción, ni siquiera tooltip. Evidencia: sin `tooltip` ni `params`. Con el país sin codificar, ni pasando el ratón se puede recuperar. Arreglo: tooltip `[country, year, life_expect, fertility, pop]` como mínimo; opcional, selección en leyenda que atenúe el resto a gris.
- **[CLT-03 / PUR-11]** Densidad de datos ínfima. Evidencia (inspector de imagen): el 3,8 % de los píxeles lleva algo; 400 × 300 px con el 71 % del eje x vacío. Consecuencia: el espacio se gasta en nada y los puntos que importan caben en un sello de correos. Se corrige con el dominio.

### Menores

- **[TXT-05 / TEXT-3]** Los rasgos notables (pico de fertilidad de Jamaica en 1965: 5,8; Israel llega a 80 años con 2,8 hijos, muy por encima del resto) no tienen anotación. En un gráfico explicativo son las dos frases que el lector recordaría.
- **[ACC-05]** Texto de ticks y leyenda a ~10 px (11 de 12 palabras detectadas por OCR por debajo de 11 px). Es el valor por defecto de Vega a 400 × 300; con más tamaño o `labelFontSize: 12` basta.
- **[TXT-13]** La leyenda de tamaño tiene una entrada "0" (un cuadrado de población cero) por escalar el área desde cero; desaparece al quitar `size`.

## Registro de comprobaciones deterministas

- `scripts/inspect_vegalite.py bad_gapminder.json`: EXP-02 (color = year:nominal, 6 valores); EXP-09 (x domain [0, 80], datos 58,0–81,2, clip); COL-05 (rojo+verde; deuteranopia #1f77b4/#9467bd ΔE 38,2 → 8,0; #2ca02c/#d62728 119,8 → 7,3; protanopia #ff7f0e/#2ca02c 100,6 → 4,6); EFF-08 (shape = country, 6 formas; color y forma en atributos distintos → búsqueda conjuntiva); EFF-11 (3 leyendas); SCL-06 ×2 (+2 sin unidades); TXT-01; TXT-03 (leyenda `year`); EFF-02 (size = pop). Aviso: `vl_convert` no disponible, se generó HTML.
- Render en navegador (Vega-Lite 5 vía vega-embed): consola `WARN shape dropped as it is incompatible with "square"`; leyendas presentes: `year` (6) y `pop` (7 entradas, incluida "0"); eje x 0–80; Islandia 2005 ausente, Israel 2005 cortado en el borde; puntos de Aruba/Granada/Islandia de 1–3 px.
- `scripts/inspect_image.py` sobre la captura: ACC-05 (texto < 11 px), CLT-03 (3,8 % de píxeles no fondo), SCL-06 (sin unidades), TXT-08 (sin fuente/n). Simulaciones: en escala de grises los seis años son indistinguibles; en deuteranopia quedan dos familias (azules / amarillo-marrones).
- Cálculo sobre la spec: 32 filas, 6 países, 6 años; Aruba y Granada sin 1965 ni 1985; span datos/eje en x = 29 %; razón de población 125×; 11 puntos en la caja 70–77 × 1,8–3,2; Islandia 2005 = 81,2 > 80 (recortado), Israel 2005 = 80,0 (en el borde).
- Matices sobre hallazgos deterministas: EFF-08 "6 formas" y "conjunción color × forma" se reportan tal cual por el inspector, pero el problema real es peor: la forma no se renderiza, así que no hay "demasiadas formas" sino ningún canal para el país (recogido como crítico en PUR-01). EFF-11 "3 leyendas": en el render son 2, y sigue sobrando una. El campo `description` de la spec habla de "11 valores" de año; los datos tienen 6; el inspector cuenta bien. `lie_factor.py` no aplica (no hay marcas de longitud).

## Qué conservar

- La elección de la dispersión esperanza de vida (x) × fertilidad (y): dos cuantitativos en posición, el canal más preciso; correcta y es la base del rediseño.
- El eje y desde 0: la fertilidad tiene cero real y el rango 0–7 no aplasta la variación (span 4,9/7 = 70 %).
- La selección de seis países pequeños con 50 años de historia: es un subconjunto con una historia que contar (convergencia desde orígenes muy distintos), no hace falta añadir más países.
- La intención de mostrar el tiempo: debe seguir ahí, pero en la geometría, no en el tono.

## Rediseño

- **Idioma**: dispersión conectada (un trazo por país, puntos unidos en orden de año), un solo panel de ~600 × 400 px. Alternativa si los trazos se cruzan demasiado: seis miniaturas 3 × 2 con escalas compartidas, cada país en color sobre los otros cinco en gris claro (CMP-05, SCL-08).
- **Codificaciones**: `life_expect` → x, cuantitativo, dominio [55, 85] con ticks visibles (SCL-02: truncamiento explícito; no es un gráfico de longitudes); `fertility` → y, cuantitativo, [0, 7], línea de referencia a 2,1 hijos (nivel de reemplazo, TRUNC-9: referencia con sentido); `country` → color (tono cualitativo, 6) + `line` con `order: year` + `point` + etiqueta `text` en el punto 2005; `year` → posición a lo largo del trazo, punto inicial 1955 hueco y final 2005 relleno, etiqueta "1955"/"2005" en un solo trazo para enseñar a leerlo; `pop` → fuera del gráfico, solo en tooltip (o `size` con `range [40, 400]` si el profesor exige mostrarla). Años ausentes (Aruba, Granada 1965/1985): tramo discontinuo (`strokeDash` condicional) o nota al pie.
- **Orden**: `order: year` en el trazo; leyenda, si la hay, en el mismo orden vertical en que terminan los trazos en 2005 (Islandia, Israel, Aruba, Jamaica, Líbano, Granada) para que leyenda y datos coincidan; mejor sin leyenda y con etiquetas directas.
- **Plan de color**: color solo para distinguir país; paleta Okabe-Ito (azul #0072B2, naranja #E69F00, verde azulado #009E73, bermellón #D55E00, púrpura #CC79A7, celeste #56B4E9) o `tableau10` evitando el par rojo–verde; segunda pista = etiqueta directa en cada trazo; ejes y cuadrícula gris claro; comprobar en simulador de deuteranopia antes de entregar.
- **Plan de texto**: título con mensaje: "Seis países pequeños convergen en 50 años hacia 70–80 años de esperanza de vida y ~2 hijos por mujer"; subtítulo: "Esperanza de vida al nacer frente a fertilidad, 1955–2005, un punto por década"; ejes con unidades; dos anotaciones con contexto (Jamaica 1965: pico de 5,8 hijos; Israel: fertilidad estable en ~2,8 con 80 años de esperanza de vida en 2005); pie: "Fuente: Gapminder. Aruba y Granada: sin datos en 1965 y 1985".
- **Interacción** (opcional, Altair `selection_point` en `country`): estado por defecto con todos los trazos visibles y etiquetados (ya responde a las tres tareas sin tocar nada); clic en un país o en la leyenda atenúa el resto a gris; tooltip con país, año, esperanza de vida, fertilidad y población.
- **Esbozo en Altair** (misma biblioteca; completarlo con las anotaciones):

```python
import altair as alt
base = alt.Chart(df).encode(
    x=alt.X('life_expect:Q', title='Esperanza de vida al nacer (años)',
            scale=alt.Scale(domain=[55, 85])),
    y=alt.Y('fertility:Q', title='Fertilidad (hijos por mujer)',
            scale=alt.Scale(domain=[0, 7])),
    color=alt.Color('country:N', title=None, legend=None,
                    scale=alt.Scale(range=['#0072B2','#E69F00','#009E73',
                                           '#D55E00','#CC79A7','#56B4E9'])),
    tooltip=['country','year','life_expect','fertility','pop'])
trail = base.mark_line(point=True).encode(order='year:O')
labels = (base.transform_filter(alt.datum.year == 2005)
              .mark_text(align='left', dx=7).encode(text='country:N'))
ref = alt.Chart(pd.DataFrame({'y':[2.1]})).mark_rule(strokeDash=[4,4], color='grey').encode(y='y:Q')
chart = (trail + labels + ref).properties(
    width=600, height=400,
    title={'text': 'Seis países pequeños convergen en 50 años hacia 70–80 años de esperanza de vida y ~2 hijos por mujer',
           'subtitle': 'Esperanza de vida frente a fertilidad, 1955–2005, un punto por década. Fuente: Gapminder. Aruba y Granada sin datos en 1965 y 1985'})
```
