import tkinter as tk
from tkinter import ttk

class SistemaAsistenciaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Asistencia Cesun")
        self.geometry("900x600")
        self.config(bg="#f0f0f0")
        
        # Dividir ventana en dos: Panel Izquierdo (menú) y Derecho (contenido)
        self.columnconfigure(0, weight=1, minsize=250)  # Panel izquierdo (30%)
        self.columnconfigure(1, weight=15)               # Panel derecho (70%)
        self.rowconfigure(0, weight=1)

        # --- Panel Izquierdo ---
        left_frame = tk.Frame(self, bg="#1E3A5F")  # azul oscuro
        left_frame.grid(row=0, column=0, sticky="nsew")

        # Logo (puede ser reemplazado por imagen)
        logo_label = tk.Label(left_frame, text="📘", font=("Arial", 40), bg="#1E3A5F", fg="white")
        logo_label.pack(pady=20)

        # Nombre de la app
        title_label = tk.Label(left_frame, text="Sistema de Asistencia\nCesun", 
                               font=("Arial", 14, "bold"), bg="#1E3A5F", fg="white")
        title_label.pack(pady=10)

        # Opciones del menú
        menu_buttons = ["Inicio", "Registro", "Asistencia", "Lista"]
        for opcion in menu_buttons:
            btn = tk.Button(left_frame, text=opcion, font=("Arial", 12), 
                            bg="#2E5A88", fg="white", relief="flat", 
                            activebackground="#4A90E2", activeforeground="white")
            btn.pack(fill="x", pady=5, padx=20)

        # --- Panel Derecho (contenido en blanco por ahora) ---
        right_frame = tk.Frame(self, bg="white")
        right_frame.grid(row=0, column=1, sticky="nsew")


if __name__ == "__main__":
    app = SistemaAsistenciaApp()
    app.mainloop()
