from PIL import Image, ImageOps, ImageFilter, ImageEnhance
from banners import print_intro
from tqdm import tqdm
import requests
import time
import os
import threading
import multiprocessing as mp

# -------------------------
# Worker para descarga (I/O)
# -------------------------
def download_worker(start_idx, end_idx, dir_name, base_url, progress_counter, lock):
    def image_thread(i):
        file_name = f'{i:03d}.png'
        url = f'{base_url}/{file_name}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            img_path = os.path.join(dir_name, file_name)
            with open(img_path, 'wb') as f:
                f.write(response.content)
        except requests.exceptions.RequestException as e:
            print(f'  Error descargando {file_name}: {e}')

        # Actualizar contador de progreso de manera segura
        with lock:
            progress_counter.value += 1

    threads = []
    for i in range(start_idx, end_idx + 1):
        t = threading.Thread(target=image_thread, args=(i,))
        threads.append(t)
        t.start()
    
    for t in threads:
        t.join()

# -------------------------
# Función principal de descarga
# -------------------------
def download_pokemon(n=150, dir_name='pokemon_dataset', max_workers=8):
    os.makedirs(dir_name, exist_ok=True)
    base_url = 'https://raw.githubusercontent.com/HybridShivam/Pokemon/master/assets/imagesHQ' 
    print(f'\nDescargando {n} pokemones con {max_workers} workers...\n')

    # Multiprocessing-safe counter para actualizar tqdm desde el main process
    progress_counter = mp.Value('i', 0)
    lock = mp.Lock()

    # Dividir el rango de imágenes por worker
    chunk_size = n // max_workers
    ranges = []
    for w in range(max_workers):
        start = w * chunk_size + 1
        end = (w + 1) * chunk_size
        ranges.append((start, end))
    if ranges[-1][1] < n:
        ranges[-1] = (ranges[-1][0], n)

    start_time = time.time()

    # Multiprocessing
    processes = []
    for r in ranges:
        p = mp.Process(target=download_worker, args=(r[0], r[1], dir_name, base_url, progress_counter, lock))
        processes.append(p)
        p.start()

    # Barra de progreso en main process
    with tqdm(total=n, desc="Descargando", unit="img") as pbar:
        while any(p.is_alive() for p in processes):
            with lock:
                pbar.n = progress_counter.value
            pbar.refresh()
            time.sleep(0.1)
        # Actualizar al final
        with lock:
            pbar.n = progress_counter.value
        pbar.refresh()

    for p in processes:
        p.join()

    total_time = time.time() - start_time
    print(f'\nDescarga completada en {total_time:.2f} segundos')
    print(f'Promedio: {total_time/n:.2f} s/img')
    return total_time

# -------------------------
# Worker para procesamiento (CPU)
# -------------------------
def process_worker_wrapper(args):
    image, dir_origin, dir_name = args
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
        img_inv = img_inv.resize((width*2, height*2), Image.LANCZOS)
        img_inv = img_inv.resize((width, height), Image.LANCZOS)

        saving_path = os.path.join(dir_name, image)
        img_inv.save(saving_path, quality=95)

    except Exception as e:
        print(f'  Error procesando {image}: {e}')

# -------------------------
# Función principal de procesamiento
# -------------------------
def process_pokemon(dir_origin='pokemon_dataset', dir_name='pokemon_processed', max_workers=8):
    os.makedirs(dir_name, exist_ok=True)
    images = sorted([f for f in os.listdir(dir_origin) if f.endswith('.png')])
    total = len(images)

    print(f'\nProcesando {total} imágenes con {max_workers} cores...\n')
    start_time = time.time()

    args_list = [(image, dir_origin, dir_name) for image in images]

    with mp.Pool(processes=max_workers) as pool:
        for _ in tqdm(pool.imap_unordered(process_worker_wrapper, args_list),
                      total=total, desc='Procesando', unit='img'):
            pass

    total_time = time.time() - start_time
    print(f'\nProcesamiento completado en {total_time:.2f} segundos')
    print(f'Promedio: {total_time/total:.2f} s/img\n')
    return total_time

# -------------------------
# MAIN
# -------------------------
if __name__ == '__main__':
    n = 151
    print('='*60)
    print_intro()
    print('   POKEMON IMAGE PROCESSING PIPELINE')
    print('='*60)

    # Fase 1: Descarga (I/O Bound)
    download_time = download_pokemon(n)

    # Fase 2: Procesamiento (CPU Bound)
    processing_time = process_pokemon()

    # Resumen final
    total_time = download_time + processing_time
    print('='*60)
    print('RESUMEN DE TIEMPOS\n')
    print(f'  Descarga:        {download_time:.2f} seg')
    print(f'  Procesamiento:   {processing_time:.2f} seg\n')
    print(f'  Total:           {total_time:.2f} seg')
    print('='*60)
