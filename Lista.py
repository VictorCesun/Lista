import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import datetime

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

        # --- Panel Derecho (contenido de Asistencia) ---
        self.right_frame = tk.Frame(self, bg="white")
        self.right_frame.grid(row=0, column=1, sticky="nsew")

        self.crear_pantalla_asistencia()

    def crear_pantalla_asistencia(self):
        # Datos superiores
        top_frame = tk.Frame(self.right_frame, bg="white", pady=10)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Docente:", bg="white").grid(row=0, column=0, padx=5, sticky="w")
        self.docente_var = tk.StringVar(value="Ejemplo Docente")
        tk.Entry(top_frame, textvariable=self.docente_var).grid(row=0, column=1, padx=5)

        tk.Label(top_frame, text="Grupo:", bg="white").grid(row=0, column=2, padx=5, sticky="w")
        self.grupo_var = tk.StringVar(value="Grupo 1")
        tk.Entry(top_frame, textvariable=self.grupo_var).grid(row=0, column=3, padx=5)
        
        tk.Label(top_frame, text="Materia:", bg="white").grid(row=0, column=4, padx=5, sticky="w")
        self.materia_var = tk.StringVar(value="Materia 1")
        tk.Entry(top_frame, textvariable=self.materia_var).grid(row=0, column=5, padx=5)
        
        tk.Label(top_frame, text="Programa:", bg="white").grid(row=0, column=6, padx=5, sticky="w")
        self.programa_var = tk.StringVar(value="Programa 1")
        tk.Entry(top_frame, textvariable=self.programa_var).grid(row=0, column=7, padx=5)

        tk.Label(top_frame, text="Parcial:", bg="white").grid(row=0, column=8, padx=5, sticky="w")
        self.parcial_var = tk.IntVar(value=1)
        parcial_spin = tk.Spinbox(top_frame, from_=1, to=3, textvariable=self.parcial_var, width=5, command=self.cargar_tabla)
        parcial_spin.grid(row=0, column=9, padx=5)

        tk.Button(top_frame, text="Guardar", command=self.guardar_asistencias, bg="#2E5A88", fg="white").grid(row=0, column=10, padx=20)

        # Línea divisoria
        ttk.Separator(self.right_frame, orient="horizontal").pack(fill="x", pady=10)

        # Tabla
        self.tree = ttk.Treeview(self.right_frame, columns=("Alumno", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes"), show="headings")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        # Datos de ejemplo
        self.alumnos = ["Ana López", "Juan Pérez", "Carlos Ruiz", "María Torres"]
        self.asistencias = {}  # { (semana, parcial): { alumno: {dia: valor} } }

        self.semana_var = tk.IntVar(value=1)

        self.cargar_tabla()

        # Detectar clic en celda con un clic
        self.tree.bind("<ButtonRelease-1>", self.on_cell_click)

        # --- Control de semanas abajo ---
        semanas_frame = tk.Frame(self.right_frame, bg="white", pady=10)
        semanas_frame.pack(fill="x", side="bottom")

        tk.Label(semanas_frame, text="Cambiar semana:", bg="white").pack(side="left", padx=5)
        for i in range(1, 5):
            tk.Button(semanas_frame, text=f"Semana {i}", command=lambda s=i: self.cambiar_semana(s),
                      bg="#2E5A88", fg="white", width=10).pack(side="left", padx=5)

    def cambiar_semana(self, semana):
        self.semana_var.set(semana)
        self.cargar_tabla()

    def cargar_tabla(self):
        # Limpiar tabla
        for item in self.tree.get_children():
            self.tree.delete(item)

        semana = self.semana_var.get()
        parcial = self.parcial_var.get()
        key = (semana, parcial)

        if key not in self.asistencias:
            self.asistencias[key] = {alumno: {dia: "" for dia in ["Lunes","Martes","Miércoles","Jueves","Viernes"]} for alumno in self.alumnos}

        for alumno, dias in self.asistencias[key].items():
            self.tree.insert("", "end", values=[alumno] + [dias[d] for d in dias])

    def on_cell_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        col_num = int(col_id.replace("#","")) - 1  # columna

        if col_num == 0:  # Nombre del alumno
            return

        alumno = self.tree.item(row_id)["values"][0]
        dias = ["Lunes","Martes","Miércoles","Jueves","Viernes"]
        dia = dias[col_num-1]

        # Validar si es el día actual
        hoy = datetime.datetime.now().strftime("%A")
        mapa_dias = {
            "Monday": "Lunes",
            "Tuesday": "Martes",
            "Wednesday": "Miércoles",
            "Thursday": "Jueves",
            "Friday": "Viernes"
        }
        if mapa_dias.get(hoy) != dia:
            return  # Solo permite editar el día actual

        # Selección en azul inmediata
        self.tree.selection_set(row_id)

        self.mostrar_opciones(row_id, col_num, alumno, dia)

    def mostrar_opciones(self, row_id, col_num, alumno, dia):
        menu = tk.Menu(self, tearoff=0)
        for valor in ["A", "F", "R", "J"]:
            menu.add_command(label=valor, command=lambda v=valor: self.set_valor(row_id, col_num, alumno, dia, v))
        menu.post(self.winfo_pointerx(), self.winfo_pointery())

    def set_valor(self, row_id, col_num, alumno, dia, valor):
        semana = self.semana_var.get()
        parcial = self.parcial_var.get()
        key = (semana, parcial)
        self.asistencias[key][alumno][dia] = valor
        self.cargar_tabla()

    def guardar_asistencias(self):
        semana = self.semana_var.get()
        parcial = self.parcial_var.get()
        key = (semana, parcial)
        hoy = datetime.datetime.now().strftime("%A")
        mapa_dias = {
            "Monday": "Lunes",
            "Tuesday": "Martes",
            "Wednesday": "Miércoles",
            "Thursday": "Jueves",
            "Friday": "Viernes"
        }
        dia_actual = mapa_dias.get(hoy)

        for alumno, dias in self.asistencias[key].items():
            if dias[dia_actual] == "":
                dias[dia_actual] = "A7"

        self.cargar_tabla()

if __name__ == "__main__":
    app = SistemaAsistenciaApp()
    app.mainloop()
