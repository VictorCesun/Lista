import calendar
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
import datetime
import json

class PantallaAsistencia(tk.Frame):
    def __init__(self, master, estudiantes_json):
        super().__init__(master, bg="white")
        self.master = master
        self.estudiantes_json = estudiantes_json

        self.alumnos = [f"{e['Nombre completo']} {e['Apellidos']}" for e in self.estudiantes_json]

        self.semana_var = tk.IntVar(value=1)
        self.parcial_var = tk.IntVar(value=1)
        self.asistencias = {}  # {(semana, parcial): { alumno: {fecha: valor} } }

        # 🔹 Nuevo: cargar lo que ya exista en asistencias.json
        self.cargar_asistencias_json()

        self.pack(expand=True, fill="both")
        self.crear_pantalla_asistencia()

    def cargar_asistencias_json(self):
        try:
            with open("asistencias.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        # Reestructuramos el archivo en el formato que usa la app
        for registro in data:
            alumno = registro["Nombre"]
            fecha = registro["Dia"]
            valor = registro["Asistencia"]

            # clave de control (parcial fijo, semana fija → podrías adaptarlo mejor si lo manejas en JSON)
            key = (1, 1)  # 👈 aquí puedes mapear con parcial/semana real si lo guardas
            if key not in self.asistencias:
                self.asistencias[key] = {}
            if alumno not in self.asistencias[key]:
                self.asistencias[key][alumno] = {}
            self.asistencias[key][alumno][fecha] = valor


    def crear_pantalla_asistencia(self):
        # Datos superiores
        top_frame = tk.Frame(self, bg="white", pady=10)
        top_frame.pack(fill="x")

        tk.Label(top_frame, text="Docente:", bg="white").grid(row=0, column=0, padx=5, sticky="w")
        docente_valor = self.estudiantes_json[0].get("Docente", "Ejemplo Docente") if self.estudiantes_json else "Ejemplo Docente"
        self.docente_var = tk.StringVar(value=docente_valor)
        tk.Entry(top_frame, textvariable=self.docente_var).grid(row=0, column=1, padx=5)

        tk.Label(top_frame, text="Grupo:", bg="white").grid(row=0, column=2, padx=5, sticky="w")
        grupo_valor = self.estudiantes_json[0].get("Grupo", "Grupo 1") if self.estudiantes_json else "Grupo 1"
        self.grupo_var = tk.StringVar(value=grupo_valor)
        tk.Entry(top_frame, textvariable=self.grupo_var).grid(row=0, column=3, padx=5)

        tk.Label(top_frame, text="Parcial:", bg="white").grid(row=0, column=4, padx=5, sticky="w")
        tk.Spinbox(top_frame, from_=1, to=3, textvariable=self.parcial_var, width=5, command=self.cargar_tabla).grid(row=0, column=5, padx=5)

        tk.Button(top_frame, text="Guardar", command=self.guardar_asistencias, bg="#2E5A88", fg="white").grid(row=0, column=6, padx=20)

        # Línea divisoria
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=10)

        # Tabla de asistencia
        self.tree = ttk.Treeview(self, columns=("Alumno", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes"), show="headings")
        self.tree.pack(expand=True, fill="both", padx=10, pady=10)

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        self.cargar_tabla()

        # Click simple para selección y edición
        self.tree.bind("<ButtonRelease-1>", self.on_cell_click)

        # Botones de semanas abajo
        semanas_frame = tk.Frame(self, bg="white", pady=10)
        semanas_frame.pack(fill="x", side="bottom")
        tk.Label(semanas_frame, text="Cambiar semana:", bg="white").pack(side="left", padx=5)
        for i in range(1, 5):
            tk.Button(semanas_frame, text=f"Semana {i}", command=lambda s=i: self.cambiar_semana(s),
                      bg="#2E5A88", fg="white", width=10).pack(side="left", padx=5)

    def cambiar_semana(self, semana):
        self.semana_var.set(semana)
        self.cargar_tabla()

    def cargar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        semana = self.semana_var.get()
        parcial = self.parcial_var.get()
        key = (semana, parcial)

        # Generar las fechas de la semana actual (Lunes → Viernes)
        hoy = datetime.date.today()
        inicio_semana = hoy - datetime.timedelta(days=hoy.weekday())  # lunes
        dias_semana = [(inicio_semana + datetime.timedelta(days=i)) for i in range(5)]
        self.dias_semana = [d.strftime("%d/%m/%Y") for d in dias_semana]  # lista de claves

        # Encabezados: "Lunes 16/09", etc.
        self.tree["columns"] = ["Alumno"] + [f"{calendar.day_name[d.weekday()]} {d.strftime('%d/%m')}" for d in dias_semana]
        self.tree.configure(show="headings")

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")

        # Inicializar asistencias si no existen
        if key not in self.asistencias:
            self.asistencias[key] = {
                alumno: {fecha: "" for fecha in self.dias_semana}
                for alumno in self.alumnos
            }

        # Cargar filas
        for alumno, dias in self.asistencias[key].items():
            valores = [dias.get(fecha, "") for fecha in self.dias_semana]
            self.tree.insert("", "end", values=[alumno] + valores)

    def on_cell_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        col_num = int(col_id.replace("#","")) - 1
        if col_num == 0:
            return

        alumno = self.tree.item(row_id)["values"][0]
        fecha = self.dias_semana[col_num-1]  # Usar la fecha como clave

        # Permitir edición solo del día actual
        hoy_str = datetime.date.today().strftime("%d/%m/%Y")
        if fecha != hoy_str:
            return

        self.tree.selection_set(row_id)
        self.mostrar_opciones(row_id, col_num, alumno, fecha)

    def mostrar_opciones(self, row_id, col_num, alumno, fecha):
        menu = tk.Menu(self, tearoff=0)
        for valor in ["A", "F", "R", "J"]:
            menu.add_command(
                label=valor,
                command=lambda v=valor: self.set_valor(row_id, col_num, alumno, fecha, v)
            )
        menu.post(self.winfo_pointerx(), self.winfo_pointery())

    def set_valor(self, row_id, col_num, alumno, fecha, valor):
        semana = self.semana_var.get()
        parcial = self.parcial_var.get()
        key = (semana, parcial)

        # Guardar el valor en el diccionario
        self.asistencias[key][alumno][fecha] = valor

        # Recargar tabla para mostrar cambios
        self.cargar_tabla()


    def guardar_asistencias(self):
        semana = self.semana_var.get()
        parcial = self.parcial_var.get()
        key = (semana, parcial)
        hoy = datetime.date.today()
        fecha_actual = hoy.strftime("%d/%m/%Y")
        fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Guardar solo asistencia del día actual
        for alumno, dias in self.asistencias[key].items():
            if dias.get(fecha_actual, "") == "":
                dias[fecha_actual] = "A"

        self.cargar_tabla()

        asistencias_guardar = []
        for e in self.estudiantes_json:
            nombre_completo = f"{e['Nombre completo']} {e['Apellidos']}"
            if nombre_completo in self.asistencias[key]:
                asistencia_valor = self.asistencias[key][nombre_completo][fecha_actual]
                asistencias_guardar.append({
                    "Matricula": e["Matricula"],
                    "Nombre": nombre_completo,
                    "Materia": e.get("Materia", "No definida"),
                    "Fecha": fecha_hora,
                    "Dia": fecha_actual,
                    "Asistencia": asistencia_valor
                })

        try:
            with open("asistencias.json", "r", encoding="utf-8") as f:
                data_existente = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data_existente = []

        data_existente.extend(asistencias_guardar)

        with open("asistencias.json", "w", encoding="utf-8") as f:
            json.dump(data_existente, f, indent=4, ensure_ascii=False)

        print("Asistencias guardadas en asistencias.json ✅")

# Función para mostrar la pantalla de asistencia en el panel derecho
def mostrar_asistencia(right_frame, estudiantes_json):
    # Limpiar panel derecho
    for widget in right_frame.winfo_children():
        widget.destroy()
    # Crear frame de asistencia
    PantallaAsistencia(right_frame, estudiantes_json)