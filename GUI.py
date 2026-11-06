#Librerias necesarias para la interfaz grafica
import customtkinter as ctk

ctk.set_appearance_mode("dark")  # Modo oscuro
ctk.set_default_color_theme("blue")  # Tema azul

class APP(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Blackmanta -Reproductor MP3")
        self.geometry("1280x720")
        self.minsize(640, 480)

        #Columna 01 Contenido
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_sidebar()
        self.crear_content()
        self.crear_player()

        # -------------Panel izquierdo-----------------

    def crear_sidebar(self):
        sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        sidebar.grid(row = 0, column = 0, sticky = "nsew")
        sidebar.grid_propagate(False)

        ctk.CTkLabel(sidebar, text='Mi Musica', font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(25, 20), padx=20)

        for Text in ("Biblioteca", "Playlist", "Descargas"):
            ctk.CTkButton(sidebar, text=Text, anchor="w", height=36).pack(fill="x", padx=15, pady=5)

        # -------------Panel Central-----------------

    def crear_content(self):
        Content = ctk.CTkFrame(self, fg_color="transparent")
        Content.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        Content.grid_columnconfigure(0, weight=1)
        Content.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(Content, text="Biblioteca", font=ctk.CTkFont(size=24, weight="bold")).grid(row=0, column=0, sticky="w", padx=10, pady=(0, 10))

        # Lista de canciones
        lista = ctk.CTkScrollableFrame(Content)
        lista.grid(row=1, column=0, sticky="nsew")
        lista.grid_columnconfigure(0, weight=1)

        for i in range(1, 16):
            fila = ctk.CTkFrame(lista)
            fila.grid(row=i, column=0, sticky="ew", pady=3)
            fila.grid_columnconfigure(1, weight=1)
            ctk.CTkLabel(fila, text=f"{i}", width=30).grid(row=0, column=0, padx=10, pady=8)
            ctk.CTkLabel(fila, text=f"Cancion de ejemplo {i}", anchor="w").grid(row=0, column=1, sticky="w")
            ctk.CTkLabel(fila, text="3:45", width=50).grid(row=0, column=2, padx=10)

# -------------Panel Central-----------------

    def crear_player(self):
        barra = ctk.CTkFrame(self, height=90, corner_radius=0)
        barra.grid(row=1, column=0, columnspan=2, sticky="ew")
        barra.grid_propagate(False)
        barra.grid_columnconfigure(1, weight=1)

        ctk.CTkLabel(barra, text="Ninguna cancion", width=200, anchor="w").grid(row=0, column=0, rowspan=2, padx=20)

        Center = ctk.CTkFrame(barra, fg_color="transparent")
        Center.grid(row=0, column=1, rowspan=2, sticky="ew")
        Center.grid_columnconfigure(0, weight=1)

        Buttons = ctk.CTkFrame(Center, fg_color="transparent")
        Buttons.grid(row=0, column=0, pady=(10,0))
        for Symbol in ("⏮", "▶", "⏭"):
            ctk.CTkButton(Buttons, text=Symbol, width=44, height=34).pack(side="left", padx=4)

        progress = ctk.CTkSlider(Center, from_=0, to=100)
        progress.set(0)
        progress.grid(row=1, column=0, sticky="ew", padx=20, pady=(8,0))

        Vol = ctk.CTkSlider(barra, from_=0, to=100, width=120)
        Vol.set(50)
        Vol.grid(row=0, column=2, rowspan=2, padx=20)

if __name__ == "__main__":
    APP().mainloop()


