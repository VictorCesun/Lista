import tkinter as tk
from tkinter import ttk
import json

class ListaEstudiantes(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Resumen de Asistencia", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # Filtro
        filtro_frame = tk.Frame(self, bg="white")
        filtro_frame.pack(pady=5)
        tk.Label(filtro_frame, text="Filtrar:", bg="white").pack(side="left", padx=5)
        self.filtro_var = tk.StringVar(value="Todos")
        opciones = ["Todos", "En riesgo", "Normales"]
        filtro_menu = ttk.Combobox(filtro_frame, textvariable=self.filtro_var, values=opciones, state="readonly", width=15)
        filtro_menu.pack(side="left")
        filtro_menu.bind("<<ComboboxSelected>>", lambda e: self.mostrar_tabla())

        # Tabla
        self.tabla_frame = tk.Frame(self, bg="white")
        self.tabla_frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.tree = ttk.Treeview(self.tabla_frame, columns=["Matricula", "Nombre", "Asistencia"], show="headings", height=20)
        for col in ["Matricula", "Nombre", "Asistencia"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150, anchor="center")
        self.tree.pack(fill="both", expand=True)

        # Scroll
        scrollbar = ttk.Scrollbar(self.tabla_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")

        self.tree.tag_configure("riesgo", foreground="red")
        self.mostrar_tabla()

    def mostrar_tabla(self):
        self.tree.delete(*self.tree.get_children())
        filtro = self.filtro_var.get()

        try:
            with open("estudiantes.json", "r", encoding="utf-8") as f:
                estudiantes = json.load(f)
            with open("asistencias.json", "r", encoding="utf-8") as f:
                registros = json.load(f)
        except:
            estudiantes = []
            registros = []

        # Agrupar asistencias por matrícula
        conteo = {}
        for est in estudiantes:
            mat = est.get("Matricula")
            conteo[mat] = {"nombre": f"{est.get('Nombre completo', '')} {est.get('Apellidos', '')}".strip(),
                           "faltas": 0, "total": 0}

        for reg in registros:
            mat = reg.get("Matricula")
            if mat in conteo:
                conteo[mat]["total"] += 1
                if reg.get("Asistencia") == "F":
                    conteo[mat]["faltas"] += 1

        for mat, datos in conteo.items():
            total = datos["total"]
            faltas = datos["faltas"]
            porcentaje = round(100 * (total - faltas) / total, 1) if total > 0 else 0

            if filtro == "En riesgo" and porcentaje >= 80:
                continue
            if filtro == "Normales" and porcentaje < 80:
                continue

            fila = self.tree.insert("", "end", values=[mat, datos["nombre"], f"{porcentaje}%"])
            if porcentaje < 80:
                self.tree.item(fila, tags=("riesgo",))