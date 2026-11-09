# Librerias necesarias para la interfaz grafica
import customtkinter as ctk
import random
import math
from pathlib import Path
import queue
import threading
from Downloader import download_song

# ------------- Paleta -----------------
ctk.set_appearance_mode("dark")  # Modo oscuro
BG = "#14121a"
Pink = "#ff2a5f"
Black_Pink = "#6e1530"
Dim_Pink = "#a04060"
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

        self.Screens = {}       # nombre de pestaña -> frame de esa pantalla
        self.buttons_tab = {}   # nombre de pestaña -> boton
        self.cola = queue.Queue()
        self.cancel_event = threading.Event()
        self.downloading = False

        self.crear_pestañas()
        self.crear_principal()
        self.crear_downloads()
        self.crear_Pie()

        self.show_screen("REPRODUCTOR")
        self.protocol("WM_DELETE_WINDOW", self.al_cerrar)
        self.after(100, self.procesar_cola)

    # -------------Consola-----------------
    def escribir_console(self, texto):
        self.console.configure(state="normal")
        self.console.insert("end", f">{texto}\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

    def procesar_cola(self):
        try:
            while True:
                self.manejar_event(self.cola.get_nowait())
        except queue.Empty:
            pass
        self.after(100, self.procesar_cola)

    def manage_event(self, ev):
        tipo = ev["tipo"]
        if tipo == "log":
            self.escribir_console(ev["texto"])

        elif tipo == "info":
            self.stat_labels["TOTAL"].configure(text=str(ev["total"]))
            self.stat_labels["DESCARGADAS"].configure(text=str(ev["ya"]))
            self.stat_labels["PENDIENTES"].configure(text=str(ev["pendientes"]))
            self.lbl_progress.configure(text=f"0/{ev['pendientes']}")
            self.escribir_console(f"PLAYLIST: {ev['playlist']}") 

        elif tipo == "progreso":
            total = ev["total"]
            self.bar_download.set(ev["hechas"] / total if total else 0)
            self.lbl_progress.configure(text=f"{ev['hechas']}/{total}")
            self.stat_labels["DESCARGADAS"].configure(text=str(ev["ya"] + ev["ok"]))
            self.stat_labels["PENDIENTES"].configure(
                text=str(total - ev["ok"] - ev["fallidas"]))
            self.stat_labels["CON_ERROR"].configure(text=str(ev["fallidas"]))

        elif tipo == "fin":
            self.descargando = False
            self.btn_download.configure(state="normal")
            self.btn_cancel.configure(state="disabled")
            estado = "DESCARGA CANCELADA" if ev.get("cancelado") else "DESCARGA TERMINADA"
            self.escribir_console(f"{estado} | OK: {ev['ok']} | ERROR: {ev['fallidas']}")

    # ------------- Navegacion -----------------
    def show_screen(self, Nom):
        if Nom not in self.Screens:
            return  # esa pestaña aun no tiene pantalla
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
            button = ctk.CTkButton(barra, text=Nom, corner_radius=0, height=32,
                                   font=font(11, True), text_color=BG,
                                   fg_color=Pink, hover_color=Green,
                                   command=lambda n=Nom: self.show_screen(n))
            button.pack(side="left", padx=4)
            self.buttons_tab[Nom] = button

    # ------------- Pantalla: Reproductor -----------------
    def crear_principal(self):
        principal = ctk.CTkFrame(self, fg_color="transparent")
        principal.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        principal.grid_columnconfigure(1, weight=1)
        principal.grid_rowconfigure(0, weight=1)
        self.Screens["REPRODUCTOR"] = principal

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

    # ------------- Pantalla: Descargas -----------------
    def crear_downloads(self):
        panel = ctk.CTkFrame(self, fg_color="transparent")
        panel.grid(row=1, column=0, sticky="nsew", padx=40, pady=30)
        panel.grid_columnconfigure(0, weight=1)
        panel.grid_rowconfigure(5, weight=1)
        self.Screens["DESCARGAS"] = panel

        ctk.CTkLabel(panel, text="DESCARGAR PLAYLIST", text_color=Pink, anchor="w",
                     font=font(24, True)).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(panel, text="URL DE LA PLAYLIST", text_color=Dim_Pink, anchor="w",
                     font=font(10)).grid(row=1, column=0, sticky="w", pady=(25, 6))

        fila = ctk.CTkFrame(panel, fg_color="transparent")
        fila.grid(row=2, column=0, sticky="ew")
        fila.grid_columnconfigure(0, weight=1)

        self.in_URL = ctk.CTkEntry(
            fila, placeholder_text="INGRESA LA URL", height=48, corner_radius=0,
            border_width=2, border_color=Pink, fg_color=BG, text_color=Cian,
            placeholder_text_color=Dim_Pink, font=font(12))
        self.in_URL.grid(row=0, column=0, sticky="ew", padx=(0, 14))
        self.in_URL.bind("<Return>", lambda e: self.iniciar_descarga())

        self.btn_download = ctk.CTkButton(
            fila, text="DESCARGAR", width=170, height=48, corner_radius=0,
            fg_color=Cian, text_color=BG, hover_color=Green, font=font(12, True), command=self.iniciar_descarga)
        self.btn_download.grid(row=0, column=1, padx=(0, 10))

        self.btn_cancel = ctk.CTkButton(
            fila, text="CANCELAR", width=170, height=48, corner_radius=0,
            fg_color=Pink, text_color=BG, hover_color=Green, font=font(12, True),
            command=self.cancelar_download, state="disabled")
        self.btn_cancel.grid(row=0, column=2)

        stats = ctk.CTkFrame(panel, fg_color="transparent")
        stats.grid(row=3, column=0, sticky="ew", pady=(25, 0))
        self.stat_labels = {}
        datos = ("TOTAL", "DESCARGADAS", "PENDIENTES", "CON_ERROR")
        for i, title in enumerate(datos):
            stats.grid_columnconfigure(i, weight=1)
            box = ctk.CTkFrame(stats, fg_color="transparent", border_width=2,
                               border_color=Pink, corner_radius=0)
            box.grid(row=0, column=i, sticky="ew", padx=(0 if i == 0 else 10, 0))
            valor = ctk.CTkLabel(box, text="0", text_color=Cian, font=font(22, True))
            valor.pack(pady=(14, 4))
            ctk.CTkLabel(box, text=title, text_color=Pink, font=font(9)).pack(pady=(0, 12))
            self.stat_labels[title] = valor

        progress = ctk.CTkFrame(panel, fg_color="transparent")
        progress.grid(row=4, column=0, sticky="ew", pady=(25, 20))
        progress.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(progress, text="PROGRESO", text_color=Pink, anchor="w",
                     font=font(10)).grid(row=0, column=0, sticky="w")
        self.lbl_progress = ctk.CTkLabel(progress, text="0/0", text_color=Pink,
                                         anchor="e", font=font(10))
        self.lbl_progress.grid(row=0, column=1, sticky="e")

        self.bar_download = ctk.CTkProgressBar(
            progress, height=8, corner_radius=0,
            fg_color=Black_Pink, progress_color=Pink)
        self.bar_download.set(0)
        self.bar_download.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        self.console = ctk.CTkTextbox(
            panel, corner_radius=0, border_width=2, border_color=Pink,
            fg_color=BG, text_color=Green, font=font(10))
        self.console.grid(row=5, column=0, sticky="nsew")
        self.console.insert("end", "> ESPERANDO URL...\n")
        self.console.insert("end", "> EJEMPLO: PLAYLIST DETECTADA\n")
        self.console.insert("end", "> EJEMPLO: DESCARGANDO 3/120\n")
        self.console.configure(state="disabled")

    def iniciar_descarga(self):
        if self.downloading:
            return
        url = self.in_URL.get().strip()
        if not url:
            self.escribir_console("Inserta la URL")
            return

        self.descargando = True
        self.cancel_event.clear()
        self.btn_download.configure(state="disabled")
        self.btn_cancel.configure(state="normal")
        self.bar_download.set(0)
        self.lbl_progress.configure("0/0")
        for etiqueta in self.stat_labels.values():
            etiqueta.configure(text="0")
        self.clear_console()

        hilo = threading.Thread(target=self.work_download, args=(url,), daemon=True)
        hilo.start()

    def work_download(self, url):
        try:
            download_song(url, on_event=self.cola.put, cancel_event=self.cancel_event)
        except Exception as e:
            self.cola.put({"tipo": "log", "texto": f"ERROR: {e}"})
            self.cola.put({"tipo": "fin", "ok": 0, "fallidas": 0, "cancelado": False})   

    def cancelar_download(self):
        if self.descargando:
            self.cancel_event.set()
            self.btn_cancel.configure(state="disabled")
            self.escribir_console("CANCELANDO... ")

    def al_cerrar(self):
        self.cancel_event.set()
        self.destroy()

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