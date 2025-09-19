import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from registro import RegistroEstudiantes
from Pase_lista import AsistenciaApp

class SistemaAsistenciaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Asistencia Cesun")
        self.geometry("1100x700")
        self.config(bg="#f0f0f0")

        # Estructura de columnas
        self.columnconfigure(0, weight=1, minsize=250)
        self.columnconfigure(1, weight=15)
        self.rowconfigure(0, weight=1)

        # --- Panel Izquierdo ---
        left_frame = tk.Frame(self, bg="#1E3A5F")
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Logo
        try:
            logo = Image.open("logo.png")
            logo = logo.resize((100, 100))
            logo_img = ImageTk.PhotoImage(logo)
            logo_label = tk.Label(left_frame, image=logo_img, bg="#1E3A5F")
            logo_label.image = logo_img
            logo_label.pack(pady=20)
        except:
            logo_label = tk.Label(left_frame, text="LOGO", font=("Arial", 40), bg="#1E3A5F", fg="white")
            logo_label.pack(pady=20)

        # Título
        title_label = tk.Label(left_frame, text="Sistema de Asistencia\nCesun",
                               font=("Arial", 14, "bold"), bg="#1E3A5F", fg="white")
        title_label.pack(pady=10)

        # --- Panel Derecho ---
        self.right_frame = tk.Frame(self, bg="white")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        # Funciones de navegación
        def mostrar_inicio():
            self._limpiar_panel()
            tk.Label(self.right_frame, text="Bienvenido al Sistema de Asistencia CESUN",
                     font=("Arial", 16), bg="white").pack(pady=20)

        def mostrar_registro():
            self._limpiar_panel()
            RegistroEstudiantes(self.right_frame)

        def mostrar_asistencia():
            self._limpiar_panel()
            AsistenciaApp(self.right_frame)

        def mostrar_lista():
            self._limpiar_panel()
            tk.Label(self.right_frame, text="Lista de Estudiantes (en construcción)",
                     font=("Arial", 16), bg="white").pack(pady=20)

        # Botones del menú
        botones_funciones = {
            "Inicio": mostrar_inicio,
            "Registro": mostrar_registro,
            "Asistencia": mostrar_asistencia,
            "Lista": mostrar_lista
        }

        for texto, accion in botones_funciones.items():
            btn = tk.Button(left_frame, text=texto, font=("Arial", 12),
                            bg="#2E5A88", fg="white", relief="flat",
                            activebackground="#4A90E2", activeforeground="white",
                            command=accion)
            btn.pack(fill="x", pady=5, padx=20)

        mostrar_inicio()

    def _limpiar_panel(self):
        for widget in self.right_frame.winfo_children():
            widget.destroy()

if __name__ == "__main__":
    app = SistemaAsistenciaApp()
    app.mainloop()