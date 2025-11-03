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
import multiprocessing

def download_pokemon(n=150, dir_name='pokemon_dataset'):
    '''
    Descarga las imágenes de los primeros n Pokemones.
    '''

    os.makedirs(dir_name, exist_ok=True)
    base_url = 'https://raw.githubusercontent.com/HybridShivam/Pokemon/master/assets/imagesHQ' 

    print(f'\nDescargando {n} pokemones...\n')
    start_time = time.time()
    
    for i in tqdm(range(1, n + 1), desc='Descargando', unit='img'):
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
    print(f'  Promedio: {total_time/n:.2f} s/img')
    
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

def run_threads(n=150, dir_name='pokemon_dataset', dir_processed='pokemon_processed'):
    
    threads = []

    tasks = [
        (download_pokemon, (n, dir_name)),
        (process_pokemon, (n, dir_name, dir_processed)),
    ]

    start = time.time()

    for func, args in tasks:
        t = threading.Thread(target=func, args=args)
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    end = time.time()
    return end - start

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

    total_time = run_threads()

    print('='*60)
    print('RESUMEN DE TIEMPOS\n')
    #print(f'  Descarga:        {download_time:.2f} seg')
    #print(f'  Procesamiento:   {processing_time:.2f} seg\n')
    print(f'  Total:           {total_time:.2f} seg')
    print('='*60)