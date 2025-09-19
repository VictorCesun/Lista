import tkinter as tk
from tkinter import ttk, messagebox
import datetime

class AsistenciaApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Asistencia - Cesun")
        self.geometry("1050x650")

        # ================== FECHA DEL SISTEMA ==================
        self.dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes"]
        hoy = datetime.datetime.today().weekday()  # 0 = lunes ... 6 = domingo
        self.dia_actual = self.dias[hoy] if hoy < 5 else None  # Solo lunes a viernes

        # ================== DATOS INICIALES ==================
        self.semanas = ["Semana 1", "Semana 2", "Semana 3", "Semana 4"]
        self.parciales = ["1er Parcial", "2do Parcial", "3er Parcial"]
        self.current_semana = 0
        self.current_parcial = 0

        # Datos en memoria: datos[parcial][semana][alumno][dia]
        self.datos = self.generar_datos_ejemplo()

        # ================== DATOS SUPERIORES ==================
        frame_datos = tk.Frame(self, pady=10)
        frame_datos.pack(fill="x")

        tk.Label(frame_datos, text="Docente:", font=("Arial", 10, "bold")).grid(row=0, column=0, padx=5, sticky="w")
        self.lbl_docente = tk.Label(frame_datos, text="Juan Pérez")
        self.lbl_docente.grid(row=0, column=1, padx=5, sticky="w")

        tk.Label(frame_datos, text="Grupo:", font=("Arial", 10, "bold")).grid(row=0, column=2, padx=5, sticky="w")
        self.lbl_grupo = tk.Label(frame_datos, text="3A")
        self.lbl_grupo.grid(row=0, column=3, padx=5, sticky="w")

        tk.Label(frame_datos, text="Parcial:", font=("Arial", 10, "bold")).grid(row=0, column=4, padx=5, sticky="w")
        self.combo_parcial = ttk.Combobox(frame_datos, values=self.parciales, state="readonly")
        self.combo_parcial.current(self.current_parcial)
        self.combo_parcial.grid(row=0, column=5, padx=5)
        self.combo_parcial.bind("<<ComboboxSelected>>", self.cambiar_parcial)

        # Botón Guardar
        self.btn_guardar = tk.Button(frame_datos, text="Guardar", command=self.guardar)
        self.btn_guardar.grid(row=0, column=6, padx=10)

        # Separador
        ttk.Separator(self, orient="horizontal").pack(fill="x", padx=10, pady=10)

        # ================== TABLA DE ASISTENCIA ==================
        frame_tabla = tk.Frame(self)
        frame_tabla.pack(fill="both", expand=True)

        self.columnas = ["Alumno"] + self.dias
        self.tree = ttk.Treeview(frame_tabla, columns=self.columnas, show="headings", height=15)
        for col in self.columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120, anchor="center")

        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<Button-1>", self.on_click)
        self.popup = None

        self.cargar_tabla()

        # ================== SELECCIÓN DE SEMANAS ==================
        frame_semanas = tk.Frame(self, pady=10)
        frame_semanas.pack(fill="x")

        tk.Label(frame_semanas, text="Seleccionar Semana:").pack(side="left", padx=5)
        for i, semana in enumerate(self.semanas):
            btn = tk.Button(frame_semanas, text=semana, command=lambda idx=i: self.cambiar_semana(idx))
            btn.pack(side="left", padx=5)

    def generar_datos_ejemplo(self):
        alumnos = ["Carlos López", "María Torres", "Ana Gómez", "Luis Fernández"]
        datos = {}
        for p, _ in enumerate(self.parciales):
            datos[p] = {}
            for s, _ in enumerate(self.semanas):
                datos[p][s] = {}
                for alumno in alumnos:
                    datos[p][s][alumno] = {dia: "" for dia in self.dias}
        # Ejemplo inicial
        datos[0][0]["Carlos López"]["Lunes"] = "A"
        datos[0][0]["María Torres"]["Martes"] = "F"
        return datos

    def cargar_tabla(self):
        self.tree.delete(*self.tree.get_children())
        semana_data = self.datos[self.current_parcial][self.current_semana]
        for alumno, dias in semana_data.items():
            valores = [alumno] + [dias[dia] for dia in self.dias]
            self.tree.insert("", "end", values=valores)

    # ================== POPUP ==================
    def on_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region == "cell":
            row_id = self.tree.identify_row(event.y)
            col_id = self.tree.identify_column(event.x)
            col_index = int(col_id.replace("#", "")) - 1
            col_name = self.columnas[col_index]

            # ✅ Solo permitir modificar el día actual
            if col_name == self.dia_actual:
                self.show_popup(event.x_root, event.y_root, row_id, col_id)

    def show_popup(self, x, y, row_id, col_id):
        if self.popup:
            self.popup.destroy()
        self.popup = tk.Toplevel(self)
        self.popup.overrideredirect(True)
        self.popup.geometry(f"+{x}+{y}")
        opciones = {"A": "Asistencia", "F": "Falta", "R": "Retardo", "J": "Justificación"}
        for i, key in enumerate(opciones.keys()):
            b = tk.Button(self.popup, text=key, width=2, command=lambda k=key: self.set_value(row_id, col_id, k))
            b.grid(row=0, column=i, padx=1, pady=1)
        self.popup.bind("<FocusOut>", lambda e: self.popup.destroy())
        self.popup.focus_set()

    def set_value(self, row_id, col_id, value):
        values = list(self.tree.item(row_id, "values"))
        col_index = int(col_id.replace("#", "")) - 1
        values[col_index] = value
        self.tree.item(row_id, values=values)
        alumno = values[0]
        self.datos[self.current_parcial][self.current_semana][alumno][self.columnas[col_index]] = value
        self.popup.destroy()

    # ================== SEMANAS ==================
    def cambiar_semana(self, idx):
        self.current_semana = idx
        self.cargar_tabla()

    # ================== PARCIALES ==================
    def cambiar_parcial(self, event):
        self.current_parcial = self.combo_parcial.current()
        self.cargar_tabla()

    # ================== GUARDAR ==================
    def guardar(self):
        if not self.dia_actual:
            messagebox.showwarning("Advertencia", "Hoy no es un día hábil (Lunes a Viernes).")
            return

        dia_index = self.dias.index(self.dia_actual) + 1  # +1 porque #1 es Alumno
        for row_id in self.tree.get_children():
            values = list(self.tree.item(row_id, "values"))
            if values[dia_index] == "":
                values[dia_index] = "A7"  # ✅ Solo rellena la columna del día actual
                alumno = values[0]
                self.datos[self.current_parcial][self.current_semana][alumno][self.dia_actual] = "A7"
            self.tree.item(row_id, values=values)

        messagebox.showinfo("Guardado", f"Asistencias del día {self.dia_actual} guardadas en {self.semanas[self.current_semana]}, {self.parciales[self.current_parcial]}.")


if __name__ == "__main__":
    app = AsistenciaApp()
    app.mainloop()
