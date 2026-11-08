# Librerias
import yt_dlp
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# Inicio de codigo
CARPETA_DESCARGA = Path(__file__).parent / "Songs_Downloaded"
MAX_HILOS = 3  # Numero maximo de hilos (si tu PC y tu internet aguantan, puedes subirlo a 5)


# Metodo para crear la carpeta de almacenamiento
def create_folder(Nom_Playlist=None):
    Ruta_Final = CARPETA_DESCARGA
    if Nom_Playlist:
        Ruta_Final = CARPETA_DESCARGA / Nom_Playlist
    Ruta_Final.mkdir(parents=True, exist_ok=True)
    return Ruta_Final


# Metodo para limpiar el nombre de la playlist
def clear_name(Nombre):
    return re.sub(r'[\\/*?:"<>|]', "", Nombre).strip()


# Opciones de yt-dlp para descargar una cancion
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


# Devuelve: True = ok, False = error, None = omitida por cancelacion
def download_one(url, carpeta_descarga, cancel_event=None):
    if cancel_event is not None and cancel_event.is_set():
        return None
    try:
        with yt_dlp.YoutubeDL(build_options(carpeta_descarga)) as ydl:
            return ydl.download([url]) == 0
    except Exception:
        return False


# Lee los IDs ya descargados (cada linea es "youtube ID_DEL_VIDEO")
def load_downloaded(carpeta_descarga):
    descargadas_file = carpeta_descarga / 'descargadas.txt'
    if not descargadas_file.exists():
        return set()
    return {line.split()[-1]
            for line in descargadas_file.read_text(encoding='utf-8').splitlines()
            if line.strip()}


# Metodo para descargar canciones de una playlist
# on_event recibe diccionarios: {"tipo": "log" | "info" | "progreso" | "fin", ...}
def download_song(url, on_event=None, cancel_event=None):
    def emit(type, **datos):
        if on_event:
            on_event({"tipo": type, **datos})

    emit("log", texto="LEYENDO PLAYLIST...")
    try:
        with yt_dlp.YoutubeDL({'quiet': True, "extract_flat": True}) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as e:
        emit("log", texto=f"ERROR AL LEER LA URL: {e}")
        emit("fin", ok=0, fallidas=0, cancelado=False)
        return
    if not info:
        emit("log", texto="NO SE PUDO LEER LA PLAYLIST")
        emit("fin", ok=0, fallidas=0, cancelado=False)
        return

    # Titulo de la playlist limpio para crear la subcarpeta
    Nom_Playlist = clear_name(info.get('title') or 'Playlist') or 'Playlist'
    carpeta_descarga = create_folder(Nom_Playlist)

    # Lista de URL individuales de la playlist
    entrada = [e for e in (info.get('entries') or []) if e]
    downloaded = load_downloaded(carpeta_descarga)

    Pendientes = []
    for e in entrada:
        if e['id'] in downloaded:
            continue
        link = e.get('url') or f"https://www.youtube.com/watch?v={e['id']}"
        Pendientes.append((link, e.get('title') or e['id']))

    total = len(Pendientes)
    ya = len(entrada) - total
    emit("info", playlist=Nom_Playlist, total=len(entrada), ya=ya, pendientes=total)

    if total == 0:
        emit("log", texto="NADA PENDIENTE: DESCARGAS COMPLETADAS")
        emit("fin", ok=0, fallidas=0, cancelado=False)
        return

    ok, fallidas, hechas = 0, [], 0
    with ThreadPoolExecutor(max_workers=MAX_HILOS) as pool:
        futures = {pool.submit(download_one, link, carpeta_descarga, cancel_event): (link, title)
                   for link, title in Pendientes}
        for future in as_completed(futures):
            link, title = futures[future]
            res = future.result()
            hechas += 1
            if res is None:
                continue  # omitida por cancelacion
            if res:
                ok += 1
                emit("log", texto=f"OK: {title}")
            else:
                fallidas.append(link)
                emit("log", texto=f"ERROR: {title}")
            # Alineado con "if res:", fuera del else
            emit("progreso", hechas=hechas, total=total, ya=ya,
                 ok=ok, fallidas=len(fallidas))

    if fallidas:
        (carpeta_descarga / 'fallidas.txt').write_text("\n".join(fallidas), encoding='utf-8')

    cancelado = bool(cancel_event and cancel_event.is_set())
    emit("fin", ok=ok, fallidas=len(fallidas), cancelado=cancelado,
         carpeta=str(carpeta_descarga.resolve()))


# Uso desde la terminal (sin interfaz)
def show_cli(ev):
    if ev["tipo"] == "log":
        print(ev["texto"])
    elif ev["tipo"] == "fin":
        print(f"Terminado... Correctas: {ev['ok']} | Con error: {ev['fallidas']}")


if __name__ == "__main__":
    url = input("Pega la URL de la playlist: ").strip()
    download_song(url, on_event=show_cli)