#Librerias 
import yt_dlp 
import re
from pathlib import Path

#Inicio de codigo
CARPETA_DESCARGA = Path("Songs_Downloaded")

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

#Metodo para descargar canciones de una playlist
def download_song(url):
    with yt_dlp.YoutubeDL({'quiet': True, "extract_flat": True}) as ydl:
        info = ydl.extract_info(url, download=False)

    # Diagnostico (puedes borrarlo cuando todo funcione)
    print("Tipo:", info.get("_type"))
    print("Título crudo:", repr(info.get("title")))

    titulo = info.get('title') or 'Playlist'
    Nom_Playlist = clear_name(titulo) or 'Playlist'
    print("Nombre final:", repr(Nom_Playlist))
    carpeta_descarga = create_folder(Nom_Playlist)

    Opt = {
        'format': 'bestaudio/best',
        'outtmpl': str(carpeta_descarga / '%(title)s.%(ext)s'),
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'ignoreerrors': True,
    }

    with yt_dlp.YoutubeDL(Opt) as ydl:
        ydl.download([url])


if __name__ == "__main__":
    #Llama a metodos de creacion de carpeta y descarga de canciones
    folder = create_folder()
    print(f"Carpeta de descarga: {folder.resolve()}")
    url = input("Pega la URL de la playlist: ").strip()
    download_song(url)
