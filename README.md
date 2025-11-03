Pokemon Image Processing Pipeline

Este proyecto implementa un pipeline para descargar y procesar imágenes de Pokémon de manera eficiente, combinando técnicas de concurrencia y paralelismo según la naturaleza de cada tarea.

---

Lógica General

La idea central del proyecto fue abstraer cada proceso iterativo a una función separada (worker). Esto permitió asignar los recursos disponibles de manera eficiente y flexible:

1. Descarga de imágenes (Multithreading)
La descarga de imágenes es una tarea I/O-bound (espera de respuesta de red). Por ello, se utilizó multithreading, donde cada imagen se descarga en un thread independiente.
La barra de progreso se actualiza conforme los threads completan sus descargas, y se asegura que todas las descargas terminen antes de continuar. Esto permite aprovechar la latencia de la red y mantener varios requests activos al mismo tiempo.

2. Procesamiento de imágenes (Multiprocessing)
El procesamiento de imágenes es CPU-bound, ya que cada imagen recibe múltiples transformaciones y filtros pesados.
Para aprovechar todos los cores disponibles, se utilizó multiprocessing, dividiendo la carga de imágenes entre varios procesos. Cada proceso trabaja en paralelo sobre diferentes imágenes, reduciendo significativamente el tiempo total de procesamiento.

3. Paralelismo + Concurrencia para descarga optimizada
Para intentar mejorar aún más el tiempo de descarga, se combinó paralelismo y concurrencia:
- Se dividió el rango total de imágenes entre varios processes (cores) usando multiprocessing. Esto permite que diferentes núcleos de la CPU gestionen descargas distintas simultáneamente.
- Cada proceso ejecuta múltiples threads internos que descargan imágenes de manera concurrente, aprovechando la latencia de la red.

De esta manera, se busca maximizar el uso de la máquina: los cores trabajan en paralelo (paralelismo) y dentro de cada core varias descargas se gestionan simultáneamente (concurrencia). Esto no es simplemente juntar las funciones de descarga y procesamiento, sino una estrategia específica para optimizar la fase de I/O.

---

Resultados de rendimiento

Se probaron cinco escenarios distintos y se midieron los tiempos de descarga, procesamiento y total (en segundos):

Caso                              | Descarga | Procesamiento | Total
---------------------------------|----------|---------------|------
Baseline                          | 86.96    | 23.64         | 110.60
Solo concurrencia (Conkeldurr)    | 13.88    | 23.25         | 37.13
Solo paralelismo (Paras)          | 86.22    | 5.50          | 91.72
Ambos (Concurrencia + Paralelismo)| 16.90    | 5.04          | 21.94
Download paralelizado              | 11.96    | 4.90          | 16.85

---

Observaciones finales

El mayor cuello de botella y variable impredecible fue la velocidad de internet, ya que esta hacía que la velocidad de descarga variara significativamente entre ejecuciones. Por esta razón, no es posible asegurar que la solución de download paralelizado haya sido una mejora real sobre la combinación de multithreading para descarga y multiprocessing para procesamiento, aunque los tiempos reportados sugieren un beneficio en algunos casos.

---

Generación de este README

Este README fue generado con la ayuda de ChatGPT. Se usaron los siguientes prompts:

1. Prompt inicial para la lógica y resultados del proyecto:
"Primero: ¿Podrías ayudarme a explicar la lógica de cómo hicimos estas tres partes del proyecto en un README.txt para mi repo? Mi lógica general fue abstraer el proceso iterable a una función distinta (worker) para luego asignar los recursos dependiendo de los llamados a la función. Explica primero el multithreading para el download, segundo el multiprocessing para el procesamiento de las imágenes y, tercero y último, la lógica de usar varios threads por cada core para, verdaderamente, aprovechar los recursos a su máximo. Quiero que muestres los resultados de los cinco casos en una tabla. Baseline: Descarga = 86.96, Procesamiento = 23.64, Total = 110.60. Solo concurrencia (Conkeldurr): 13.88, 23.25, 37.13. Solo paralelismo (Paras): 86.22, 5.5, 91.72. Ambos: 16.9, 5.04, 21.94. (Download paralelizado): 11.96, 4.9, 16.85. Por último, quiero que agregues un parrafo final que diga que el mayor cuello de botella y variable impredecible fue la velocidad de internet ya que esta hacía que variara la velocidad bastante. Por lo mismo, no se sabe si el download paralelizado fue verdaderamente una mejora a la solución de que usaba multithreading para download y paralelismo para procesamiento."

2. Prompt de mejora para aclarar el punto 3 (paralelismo + concurrencia):
"Podrías hacer más explicito en el punto 3 que se utiliza el paralelismo para intentar mejorar el tiempo de descarga al repartir las tareas en diferentes cores y luego usar la concurrencia? Siento que se puede confundir con simplemente unir ambas funciones del punto 1 y 2 en un solo archivo."
