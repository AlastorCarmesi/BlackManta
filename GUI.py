# Librerias necesarias para la interfaz grafica
import customtkinter as ctk
import random
import math
from pathlib import Path

ctk.set_appearance_mode("dark")  # Modo oscuro

# ------------- Paleta -----------------
BG = "#14121a"
Pink = "#ff2a5f"
Black_Pink = "#6e1530"
Cian = "#2ee6e6"
Shiny_Cian = "#0f6b6b"
Green = "#3dff9a"

# ------------- Recursos -----------------
Ruta_Font = Path(__file__).parent / "Recursos" / "PressStart2P-Regular.ttf"
Font = "Consolas"  # Fuente predeterminada
if Ruta_Font.exists():
    ctk.FontManager.load_font(str(Ruta_Font))
    Font = "Press Start 2P"  # Fuente personalizada si existe

# ------------- Datos de ejemplo -----------------
Songs = [
    ("NEON_RUNNER", "03:12"), ("MIDNIGHT_GRID", "04:20"),
    ("PIXEL", "02:30"), ("BLACK_WAVES", "03:45"),
    ("LASER_DRIVE", "03:21"), ("ECHO_CITY", "04:11"),
    ("STATIC_HEART", "03:30"), ("DARK_SIGNALIS", "04:00"),
    ("VHS_DREAMS", "03:15"), ("SIGNALIS", "04:25"),
]


def font(size, bold=False):
    return ctk.CTkFont(family=Font, size=size, weight="bold" if bold else "normal")


class APP(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Blackmanta - Reproductor MP3")
        self.geometry("1280x720")
        self.minsize(900, 560)
        self.configure(fg_color=BG)

        # Columna 0 y fila 1 (zona central) se estiran
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        random.seed(7)
        self.amplitudes = [0.25 + 0.75 * abs(math.sin(i / 9)) * random.uniform(0.5, 1)
                           for i in range(150)]

        self.Screens = {}
        self.buttons_tab = {}

        self.crear_pestañas()
        self.crear_principal()
        self.crear_screen()
        self.crear_downloads()
        self.crear_Pie()

        self.show_screen("REPRODUCTOR")
    # ------------- Navegacion -----------------
    def show_screen(self, Nom):
        if Nom not in self.Screens:
            return
        for frame in self.Screens.values():
            frame.grid_remove()
        self.Screens[Nom].grid()

        for nom, button in self.buttons_tab.items():
            button.configure(fg_color=Cian if nom == Nom else Pink)

    # ------------- Pestañas superiores -----------------
    def crear_pestañas(self):
        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.grid(row=0, column=0, sticky="ew", padx=40, pady=(25, 0))

        Noms = ["BIBLIOTECA", "PLAYLISTS", "DESCARGAS", "REPRODUCTOR", "AJUSTES"]
        for Nom in Noms:
            active = Nom == "REPRODUCTOR"
            ctk.CTkButton(barra, text=Nom, corner_radius=0, height=32,
                          font=font(11, True), text_color=BG,
                          fg_color=Cian if active else Pink,
                          hover_color=Green).pack(side="left", padx=4)

    # ------------- Zona central -----------------
    def crear_principal(self):
        principal = ctk.CTkFrame(self, fg_color="transparent")
        principal.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        principal.grid_columnconfigure(1, weight=1)
        principal.grid_rowconfigure(0, weight=1)

        self.crear_list(principal)
        self.crear_panel_player(principal)

    def crear_list(self, parent):
        lista = ctk.CTkScrollableFrame(parent, width=420, fg_color="transparent")
        lista.grid(row=0, column=0, sticky="ns", padx=(0, 30))
        lista.grid_columnconfigure(0, weight=1)

        for i, (Nom, Dur) in enumerate(Songs):
            color = Green if i == 0 else Pink
            ctk.CTkLabel(lista, text=Nom, text_color=color, anchor="w",
                         font=font(13, True)).grid(row=i, column=0, sticky="w", pady=10)
            ctk.CTkLabel(lista, text=Dur, text_color=color,
                         font=font(13, True)).grid(row=i, column=1, padx=(20, 0))

    def crear_panel_player(self, parent):
        panel = ctk.CTkFrame(parent, fg_color="transparent")
        panel.grid(row=0, column=1, sticky="nsew")
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(panel, text=Songs[0][0], text_color=Pink, anchor="w",
                     font=font(24, True)).grid(row=0, column=0, sticky="w")

        self.onda = ctk.CTkCanvas(panel, bg=BG, highlightthickness=0, height=200)
        self.onda.grid(row=1, column=0, sticky="nsew", pady=20)
        self.onda.bind("<Configure>", self.draw_onda)

        ctk.CTkLabel(panel, text="-01:57", text_color=Pink, anchor="e",
                     font=font(22, True)).grid(row=2, column=0, sticky="e")

        barra = ctk.CTkProgressBar(panel, height=8, corner_radius=0,
                                   fg_color=Black_Pink, progress_color=Pink)
        barra.set(0.4)
        barra.grid(row=3, column=0, sticky="ew", pady=(8, 20))

        button = ctk.CTkFrame(panel, fg_color="transparent")
        button.grid(row=4, column=0, sticky="w")
        for symbol, color in (("▶", Cian), ("❚❚", Pink), ("■", Pink)):
            ctk.CTkButton(button, text=symbol, width=64, height=64, corner_radius=0,
                          fg_color=color, text_color=BG, hover_color=Green,
                          font=font(18, True)).pack(side="left", padx=(0, 14))

    def draw_onda(self, event=None):
        C = self.onda
        C.delete("all")
        W, H = C.winfo_width(), C.winfo_height()
        centro = H // 2
        Step = 8
        for i, a in enumerate(self.amplitudes):
            X = 10 + i * Step
            if X > W - 10:
                break
            Alture = a * H * 0.45
            C.create_line(X, centro - Alture, X, centro + Alture, fill=Shiny_Cian, width=5)
            C.create_line(X, centro - Alture, X, centro + Alture, fill=Cian, width=2)
# ------------- Zona de descargas -----------------
def crear_downloads(self):
    panel = ctk.CTkFrame(self, fg_color="transparent")
    panel.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
    panel.grid_columnconfigure(0, weight=1)
    panel.grid_rowconfigure(5, weight=1)
    self.pantallas["DESCARGAS"] = panel

    ctk.CTkLabel(panel, text="DESCARGAR PLAYLIST", text_color=Pink, anchor="w", font=font(24,True)).grid(row=0, column=0, sticky="w")
    ctk.CTkLabel().grid()

   
# ------------- Pie de pantalla -----------------
    def crear_Pie(self):
        pie = ctk.CTkFrame(self, fg_color="transparent")
        pie.grid(row=2, column=0, sticky="ew", padx=40, pady=(0, 20))

        ctk.CTkFrame(pie, height=3, fg_color=Pink, corner_radius=0).pack(fill="x", pady=(0, 10))
        ctk.CTkLabel(pie, text="SELECCIONAR PISTA", text_color=Pink,
                     font=font(10)).pack(side="left")
        ctk.CTkLabel(pie, text="PLAY       PAUSE       STOP", text_color=Pink,
                     font=font(10)).pack(side="right")


if __name__ == "__main__":
    APP().mainloop()