'''
@tortolala
Pokemon image processing pipeline.
'''

from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from pika_banner import print_pikachu
from tqdm import tqdm
import requests
import time
import os
import shutil

# Multithreading (concurrencia)
import threading

# Multiprocessing (paralelismo)
import multiprocessing as mp

def download_pokemon(start=1, end=151, dir_name='pokemon_dataset'):
    '''
    Descarga las imágenes de los primeros n Pokemones.
    '''

    os.makedirs(dir_name, exist_ok=True)
    base_url = 'https://raw.githubusercontent.com/HybridShivam/Pokemon/master/assets/imagesHQ' 

    print(f'\nDescargando {end - start} pokemones...\n')
    start_time = time.time()
    
    for i in tqdm(range(start, end), desc='Descargando', unit='img'):
        file_name = f'{i:03d}.png'
        url = f'{base_url}/{file_name}'
        
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            img_path = os.path.join(dir_name, file_name)
            with open(img_path, 'wb') as f:
                f.write(response.content)
                
        except requests.exceptions.RequestException as e:
            tqdm.write(f'  Error descargando {file_name}: {e}')
    
    total_time = time.time() - start_time
    print(f'  Descarga completada en {total_time:.2f} segundos')
    print(f'  Promedio: {total_time / (end - start):.2f} s/img')
    
    return total_time


def process_pokemon(n=150, dir_origin='pokemon_dataset', dir_name='pokemon_processed'):
    '''
    Procesa imágenes hasta completar n, evitando reprocesar las ya tratadas.
    La barra de progreso muestra el avance total hacia n imágenes procesadas.
    '''
    os.makedirs(dir_name, exist_ok=True)
    processed = []  # lista de nombres ya procesados

    print(f'\nEsperando procesar {n} imágenes en total...\n')
    start_time = time.time()

    # Barra de progreso global
    pbar = tqdm(total=n, desc='Procesando', unit='img')

    while len(processed) < n:
        images = [f for f in os.listdir(dir_origin) if f.endswith('.png')]
        pending = [img for img in images if img not in processed]

        if not pending:
            time.sleep(5)
            continue

        for image in pending:
            if len(processed) >= n:
                break

            try:
                path_origin = os.path.join(dir_origin, image)
                img = Image.open(path_origin).convert('RGB')

                # Transformaciones
                img = img.filter(ImageFilter.GaussianBlur(radius=10))
                enhancer = ImageEnhance.Contrast(img)
                img = enhancer.enhance(1.5)
                img = img.filter(ImageFilter.EDGE_ENHANCE_MORE)
                img_inv = ImageOps.invert(img)
                img_inv = img_inv.filter(ImageFilter.GaussianBlur(radius=5))
                width, height = img_inv.size
                img_inv = img_inv.resize((width * 2, height * 2), Image.LANCZOS)
                img_inv = img_inv.resize((width, height), Image.LANCZOS)

                saving_path = os.path.join(dir_name, image)

                # evitar error de permisos
                if os.path.exists(saving_path):
                    os.remove(saving_path)

                img_inv.save(saving_path, quality=95)

                processed.append(image)
                pbar.update(1)

            except Exception as e:
                pbar.write(f'  Error procesando {image}: {e}')

        if len(processed) < n:
            time.sleep(5)

    pbar.close()
    total_time = time.time() - start_time
    print(f'\nProcesamiento completado. {len(processed)} imágenes procesadas.')
    print(f'Tiempo total: {total_time:.2f} segundos')
    print(f'Promedio: {total_time / len(processed):.2f} s/img\n')

    return processed, total_time


def run_threads(start=1, end=151, dir_name='pokemon_dataset', dir_processed='pokemon_processed', chunk_id=0):
    
    threads = []

    tasks = [
        (download_pokemon, (start, end, dir_name)),
        (process_pokemon, (end - start, dir_name, dir_processed)),
    ]

    start_time = time.time()

    for func, args in tasks:
        t = threading.Thread(target=func, args=args)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end_time = time.time()
    return end_time - start_time


def worker(chunk_tuple, resultado_queue):
    start_chunk, end_chunk, dir_name, dir_processed, chunk_id = chunk_tuple
    resultado = run_threads(start_chunk, end_chunk, dir_name, dir_processed, chunk_id)
    resultado_queue.put(resultado)


def parallel_processing(data=150, dir_name='pokemon_dataset', dir_processed='pokemon_processed', n_cores=1):
   
    # Dividir datos en chunks
    chunk_size = data // n_cores
    chunks = []
    
    for i in range(n_cores):
        start = 1 + i * chunk_size
        end = start + chunk_size if i < n_cores - 1 else data + 1
        # each chunk is (chunk_data, dir_name, dir_processed, chunk_id)
        chunks.append((start, end, dir_name, dir_processed, i))

    # Crear procesos manualmente
    processes = []
    queue = mp.Queue()

    start_time = time.time()
    
    # Iniciar procesos
    for chunk_data in chunks:
        p = mp.Process(target=worker, args=(chunk_data, queue))
        p.start()
        processes.append(p)
    
    # Esperar a que terminen
    for p in processes:
        p.join()
    
    # Recolectar resultados
    results = []
    while not queue.empty():
        results.append(queue.get())
    
    total_time = time.time() - start_time
    
    print(f'Tiempo: {total_time:.4f}s')
    print(f'Cores utilizados: {n_cores}')
    return total_time


if __name__ == '__main__':

    shutil.rmtree('pokemon_dataset', ignore_errors=True)
    shutil.rmtree('pokemon_processed', ignore_errors=True)
    
    print('='*60)
    print_pikachu()
    print('   POKEMON IMAGE PROCESSING PIPELINE')
    print('='*60)
    
    # Fase 1: Descarga (I/O Bound)
    #download_time = download_pokemon()
    # Fase 2: Procesamiento (CPU Bound)
    #processing_time = process_pokemon()
    
    # Resumen final
    #total_time = download_time + processing_time

    #total_time = run_threads()
    total_time = parallel_processing(data=150, dir_name='pokemon_dataset', dir_processed='pokemon_processed', n_cores=8)

    print('='*60)
    print('RESUMEN DE TIEMPOS\n')
    #print(f'  Descarga:        {download_time:.2f} seg')
    #print(f'  Procesamiento:   {processing_time:.2f} seg\n')
    print(f'  Total:           {total_time:.2f} seg')
    print('='*60)
