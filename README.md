# Ejercicio: Paralelismo y Concurrencia

Este proyecto implementa una **pipeline** de procesamiento de imágenes de Pokémon, aplicando **multithreading** y **multiprocessing** para optimizar el rendimiento en la descarga y transformación de imágenes.

## Estrategias de Optimización

### 1. Multithreading
La función `download_pokemon` descarga imágenes desde una API. Estas operaciones generan tiempos muertos por latencia de red, por lo que se utiliza **multithreading** para ejecutar la descarga y el procesamiento en paralelo dentro de un mismo núcleo.  

**Resultado:** reducción del tiempo de ejecución en un **47.81%** respecto al código original.

### 2. Multiprocessing y Multithreading
Para aprovechar varios núcleos, se implementa **multiprocessing**, aplicando la misma lógica del multithreading pero de forma independiente en cada núcleo. Cada proceso crea sus propias carpetas de descarga y procesamiento, lo que **evita bloqueos (locks)** y el **error 032** por acceso simultáneo a los mismos archivos. Al finalizar, los resultados se combinan en una sola carpeta y se eliminan las temporales.  

**Resultado:** aprovechamiento total de los recursos del sistema y una reducción del tiempo de ejecución en un **89.28%** respecto al código original.

## Adaptación de las Funciones Base

Las funciones originales **`download_pokemon`** y **`process_pokemon`** fueron modificadas para ser compatibles con entornos **multithreaded** y **multiprocess**. Estas adaptaciones permiten su ejecución concurrente e independiente en distintos núcleos, garantizando que cada proceso trabaje con sus propios directorios sin interferir con los demás.

## Comparativa de Rendimiento

| Estrategia                        | Tiempo Total (s) |
|----------------------------------|-----------------:|
| Código Base                      | 276.20           |
| Multithreading                   | 144.16           |
| Multithreading + Multiprocessing | 29.61            |

## Requisitos

```bash
pip install pillow tqdm requests
