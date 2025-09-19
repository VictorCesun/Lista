import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk  # Importar correctamente Pillow

class SistemaAsistenciaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Asistencia Cesun")
        self.geometry("1100x700")
        self.config(bg="#f0f0f0")
        
        # Dividir ventana en dos: Panel Izquierdo (menú) y Derecho (contenido)
        self.columnconfigure(0, weight=1, minsize=250)  # Panel izquierdo (30%)
        self.columnconfigure(1, weight=15)              # Panel derecho (70%)
        self.rowconfigure(0, weight=1)

        # --- Panel Izquierdo ---
        left_frame = tk.Frame(self, bg="#1E3A5F")  # azul oscuro
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Logo (imagen)
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

        title_label = tk.Label(left_frame, text="Sistema de Asistencia\nCesun",
                               font=("Arial", 14, "bold"), bg="#1E3A5F", fg="white")
        title_label.pack(pady=10)

        self.right_frame = tk.Frame(self, bg="white")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        def mostrar_inicio():
            self._limpiar_panel()
            tk.Label(self.right_frame, text="Bienvenido al Sistema de Asistencia CESUN",
                     font=("Arial", 16), bg="white").pack(pady=20)

        def mostrar_registro():
            self._limpiar_panel()
            RegistroEstudiantes(self.right_frame)

        def mostrar_asistencia():
            self._limpiar_panel()
            tk.Label(self.right_frame, text="Módulo de Asistencia (en construcción)",
                     font=("Arial", 16), bg="white").pack(pady=20)

        def mostrar_lista():
            self._limpiar_panel()
            tk.Label(self.right_frame, text="Lista de Estudiantes (en construcción)",
                     font=("Arial", 16), bg="white").pack(pady=20)

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

        # --- Panel Derecho (contenido en blanco por ahora) ---
        right_frame = tk.Frame(self, bg="white")
        right_frame.grid(row=0, column=1, sticky="nsew")

if __name__ == "__main__":
    app = SistemaAsistenciaApp()
    app.mainloop()
