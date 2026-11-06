#Librerias 
import yt_dlp 
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

#Inicio de codigo
CARPETA_DESCARGA = Path(__file__).parent / "Songs_Downloaded"
MAX_HILOS = 5 # Número máximo de hilos para la descarga concurrente

#Metodo para crear la carpeta de almacenamiento 
def create_folder(Nom_Playlist=None):
    # Crear la carpeta para las canciones 
    Ruta_Final = CARPETA_DESCARGA 
    if Nom_Playlist:
        Ruta_Final = CARPETA_DESCARGA / Nom_Playlist
    Ruta_Final.mkdir(parents=True, exist_ok=True)

    return Ruta_Final

#Metodo para limpiar el nombre de la playlist
def clear_name(Nombre):
    return re.sub(r'[\\/*?:"<>|]', "", Nombre).strip()

#Metodo para descargar una sola cancion           
def build_options(carpeta_descarga):
     return {
        'format': 'bestaudio/best',
        'outtmpl': str(carpeta_descarga / '%(title)s.%(ext)s'),
        'windowsfilenames': True,
        'download_archive': str(carpeta_descarga / 'descargadas.txt'),
        'quiet': True,
        'no_warnings': True,
        'noprogress': True,
        'ignoreerrors': True,
        'retries': 5,
        'socket_timeout': 30,
        'sleep_interval': 1,
        'max_sleep_interval': 3,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],

    }

def download_one(url, carpeta_descarga):
    try:
        with yt_dlp.YoutubeDL(build_options(carpeta_descarga)) as ydl:
            ydl.download([url]) == 0
    except Exception as e:
        print(f"Error al descargar {url}: {e}")
        return False
def load_downloaded(carpeta_descarga):
    descargadas_file = carpeta_descarga / 'descargadas.txt'
    if not descargadas_file.exists():
        return set()
    return {line.strip() for line in descargadas_file.read_text(encoding='utf-8').splitlines() if line.strip()}

#Metodo para descargar canciones de una playlist
def download_song(url):

    with yt_dlp.YoutubeDL({'quiet': True, "extract_flat": True}) as ydl:
        info = ydl.extract_info(url, download=False)

# Obtenemos el titulo de la playlist y lo limpiamos para crear la Subcarpeta
    titulo = info.get('title') or 'Playlist'
    Nom_Playlist = clear_name(titulo) or 'Playlist'
    carpeta_descarga = create_folder(Nom_Playlist)

    #Lista de URL individuales de la playlist
    entrada = [e for e in (info.get('entries') or []) if e]
    downloaded = load_downloaded(carpeta_descarga)

    Pendientes = []
    for e in entrada:
        if e['id'] in downloaded:
            continue
        Pendientes.append((e['id'], e.get('url') or f"https://www.youtube.com/watch?v={e['id']}"))


    print(f"Playlist: {Nom_Playlist} | Total: {len(entrada)} | "
          f"Ya descargadas: {len(downloaded)} | Pendientes: {len(Pendientes)}")
    
    ok, fallidas = 0, []
    pool = ThreadPoolExecutor(max_workers=MAX_HILOS) 
    futures = {pool.submit(download_one, u, carpeta_descarga): vid for vid, u in Pendientes}
    try: 
            for i, future in enumerate(as_completed(futures), 1):
                if future.result():
                    ok += 1
                else:
                    fallidas += 1
                print(f"Progreso: {i}/{Pendientes}", end="\r")
    except KeyboardInterrupt:
            print("\n Descarga cancelada...")
            pool.shutdown(wait=False, cancel_futures=True)
    if fallidas:
        (carpeta_descarga / 'fallidas.txt').write_text('\n'.join(fallidas), encoding='utf-8')

    print(f"\nTerminado. Correctas: {ok} | Con error: {fallidas}")
    print(f"Carpeta: {carpeta_descarga.resolve()}")


if __name__ == "__main__":
    #Llama a metodos de creacion de carpeta y descarga de canciones
    folder = create_folder()
    print(f"Carpeta de descarga: {folder.resolve()}")
    url = input("Pega la URL de la playlist: ").strip()
    download_song(url)
