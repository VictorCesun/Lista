import tkinter as tk
from tkinter import ttk, messagebox
import datetime
import json
import calendar
from datetime import date, datetime, timedelta

class PantallaAsistencia(tk.Frame):
    def __init__(self, master, estudiantes_json):
        super().__init__(master, bg="white")
        self.master = master
        self.pack(expand=True, fill="both")

        # datos pasados desde la app principal
        self.estudiantes_json = estudiantes_json or []
        self.alumnos = [f"{e.get('Nombre completo','') } {e.get('Apellidos','')}".strip() for e in self.estudiantes_json]

        # control parcial/semana
        self.parcial_var = tk.IntVar(value=1)
        self.semana_var = tk.IntVar(value=1)

        # configuración del cuatrimestre (ajusta si necesitas otra fecha / duraciones)
        self.INICIO_CUATRIMESTRE = date(2025, 9, 1)   # cambiar aquí si es necesario
        # cada tupla: (inicio_en_semanas_desde_inicio, fin_exclusivo_en_semanas)
        self.PARCIALES = {
            1: (0, 5),
            2: (5, 10),
            3: (10, 15)
        }

        # asistencias en memoria: clave -> "p{parcial}_s{semana}" -> { "Alumno Nombre": { "dd/mm/YYYY": valor } }
        self.asistencias = {}

        # cargar registros existentes desde archivo (si existen)
        self._cargar_asistencias_desde_archivo()

        # calcular en qué parcial/semana estamos HOY
        parcial_hoy, semana_hoy = self.fecha_a_parcial_semana(date.today())
        self.parcial_var.set(parcial_hoy)
        self.semana_var.set(semana_hoy)

        # crear UI
        self._crear_pantalla_asistencia()

        # primera carga de tabla
        self.cargar_tabla()
    # ---------------- Helpers de fechas / parciales ----------------
    def _parse_fecha_str(self, fecha_str):
        """Intenta parsear dd/mm/YYYY o YYYY-mm-dd y devuelve date o None."""
        if not fecha_str:
            return None
        for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%Y/%m/%d"):
            try:
                return datetime.strptime(fecha_str, fmt).date()
            except Exception:
                pass
        return None

    def fecha_a_parcial_semana(self, d: date):
        """Dada una fecha, devuelve (parcial, semana_local) según INICIO_CUATRIMESTRE y PARCIALES."""
        semanas_desde_inicio = (d - self.INICIO_CUATRIMESTRE).days // 7
        # si está antes del inicio, lo ubicamos en el primer parcial semana 1
        if semanas_desde_inicio < 0:
            return 1, 1
        for p, (start, end) in self.PARCIALES.items():
            if start <= semanas_desde_inicio < end:
                semana_local = semanas_desde_inicio - start + 1
                if semana_local < 1:
                    semana_local = 1
                return p, semana_local
        # si está después del último parcial, lo asignamos al último parcial
        last_p = max(self.PARCIALES.keys())
        last_start, last_end = self.PARCIALES[last_p]
        semana_local = semanas_desde_inicio - last_start + 1
        if semana_local < 1:
            semana_local = 1
        return last_p, semana_local


    # ---------------- Archivo JSON ----------------
    def _cargar_asistencias_desde_archivo(self):
        """Carga asistencias.json (si existe) y lo transforma al dict interno self.asistencias."""
        try:
            with open("asistencias.json", "r", encoding="utf-8") as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return

        # data puede ser lista de registros (esperado)
        if isinstance(data, dict):
            # posiblemente formato antiguo: intentar normalizar
            # si dict y tiene claves de parcial, lo ponemos directo
            # pero para robustez asumimos lista de registros preferible
            return

        for registro in data:
            nombre = registro.get("Nombre") or f"{registro.get('Nombre completo','')} {registro.get('Apellidos','')}".strip()
            dia_str = registro.get("Dia") or registro.get("Fecha") or ""
            fecha_obj = self._parse_fecha_str(dia_str)
            if fecha_obj:
                # si Parcial/Semana vienen en el registro, preferirlos
                parcial = registro.get("Parcial")
                semana = registro.get("Semana")
                if parcial is None or semana is None:
                    parcial, semana = self.fecha_a_parcial_semana(fecha_obj)
                key = f"p{int(parcial)}_s{int(semana)}"
                if key not in self.asistencias:
                    self.asistencias[key] = {}
                if nombre not in self.asistencias[key]:
                    self.asistencias[key][nombre] = {}
                # usar formato dd/mm/YYYY interno
                dia_interno = fecha_obj.strftime("%d/%m/%Y")
                self.asistencias[key][nombre][dia_interno] = registro.get("Asistencia", registro.get("Valor",""))
            else:
                # no se pudo parsear la fecha: ignorar o loggear
                continue

    def _leer_json_como_lista(self):
        try:
            with open("asistencias.json", "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return []

    def _escribir_json_lista(self, lista):
        with open("asistencias.json", "w", encoding="utf-8") as f:
            json.dump(lista, f, indent=4, ensure_ascii=False)


    # ---------------- Interfaz ----------------
    def _crear_pantalla_asistencia(self):
        # Top frame - controles
        top = tk.Frame(self, bg="white", pady=8)
        top.pack(fill="x")

        tk.Label(top, text="Docente:", bg="white").grid(row=0, column=0, sticky="w", padx=6)
        docente_valor = self.estudiantes_json[0].get("Docente", "Ejemplo Docente") if self.estudiantes_json else "Ejemplo Docente"
        self.docente_var = tk.StringVar(value=docente_valor)
        tk.Entry(top, textvariable=self.docente_var, width=18).grid(row=0, column=1, padx=6)

        tk.Label(top, text="Grupo:", bg="white").grid(row=0, column=2, sticky="w", padx=6)
        grupo_valor = self.estudiantes_json[0].get("Grupo", "Grupo 1") if self.estudiantes_json else "Grupo 1"
        self.grupo_var = tk.StringVar(value=grupo_valor)
        tk.Entry(top, textvariable=self.grupo_var, width=10).grid(row=0, column=3, padx=6)

        tk.Label(top, text="Parcial:", bg="white").grid(row=0, column=4, sticky="w", padx=6)
        spin_parcial = tk.Spinbox(top, from_=1, to=3, textvariable=self.parcial_var, width=4, command=self.cargar_tabla)
        spin_parcial.grid(row=0, column=5, padx=6)

        tk.Label(top, text="Semana:", bg="white").grid(row=0, column=6, sticky="w", padx=6)
        # semanas 1..5
        for i in range(1, 6):
            btn = tk.Button(top, text=f"{i}", width=3, command=lambda s=i: self._set_semana(s))
            btn.grid(row=0, column=6 + i, padx=2)

        btn_guardar = tk.Button(top, text="Guardar", bg="#2E5A88", fg="white", command=self.guardar_asistencias)
        btn_guardar.grid(row=0, column=13, padx=12)

        # Separador
        ttk.Separator(self, orient="horizontal").pack(fill="x", pady=6)

        # Treeview sin columnas fijas (se crean dinámicamente)
        self.tree = ttk.Treeview(self, show="headings")
        self.tree.pack(expand=True, fill="both", padx=8, pady=8)

        # bind
        self.tree.bind("<ButtonRelease-1>", self.on_cell_click)


    def _set_semana(self, s):
        self.semana_var.set(s)
        self.cargar_tabla()


    # ----------------- Cargar / mostrar datos en la tabla -----------------
    def obtener_dias_de_semana_segun_parcial(self, parcial, semana_local):
        """Calcula los 5 días (date objs) de la semana solicitada dentro del cuatrimestre."""
        inicio_parcial, fin_parcial = self.PARCIALES.get(parcial, (0,5))
        semana_global = inicio_parcial + (semana_local - 1)
        inicio_semana = self.INICIO_CUATRIMESTRE + timedelta(weeks=semana_global)
        return [inicio_semana + timedelta(days=i) for i in range(5)]


    def cargar_tabla(self):
        # volver a leer estudiantes.json por si hubo cambios
        try:
            with open("estudiantes.json", "r", encoding="utf-8") as f:
                self.estudiantes_json = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.estudiantes_json = []

        self.alumnos = [f"{e.get('Nombre completo','')} {e.get('Apellidos','')}".strip() for e in self.estudiantes_json]

        # limpiar filas previas
        for it in self.tree.get_children():
            self.tree.delete(it)

        # limpiar columnas previas
        for col in self.tree["columns"]:
            self.tree.heading(col, text="")
            self.tree.column(col, width=0)
        self.tree["columns"] = ()

        parcial = int(self.parcial_var.get())
        semana_local = int(self.semana_var.get())

        dias_date = self.obtener_dias_de_semana_segun_parcial(parcial, semana_local)
        self.dias_semana = [d.strftime("%d/%m/%Y") for d in dias_date]

        # encabezados visuales (en español)
        daynames_es = ["Lunes","Martes","Miércoles","Jueves","Viernes","Sábado","Domingo"]
        columnas = ["Alumno"] + [f"{daynames_es[d.weekday()]} {d.strftime('%d/%m')}" for d in dias_date]
        self.tree["columns"] = columnas
        for col in columnas:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")

        # clave interna por parcial+semana
        key = f"p{parcial}_s{semana_local}"
        if key not in self.asistencias:
            self.asistencias[key] = {}

        # asegurar que todos los alumnos aparezcan aunque no tengan registros
        for estudiante in self.estudiantes_json:
            nombre = f"{estudiante.get('Nombre completo','')} {estudiante.get('Apellidos','')}".strip()
            if not nombre:
                continue
            if nombre not in self.asistencias[key]:
                self.asistencias[key][nombre] = {fecha: "" for fecha in self.dias_semana}
            else:
                for fecha in self.dias_semana:
                    if fecha not in self.asistencias[key][nombre]:
                        self.asistencias[key][nombre][fecha] = ""

        # poblar filas
        for estudiante in self.estudiantes_json:
            nombre = f"{estudiante.get('Nombre completo','')} {estudiante.get('Apellidos','')}".strip()
            if not nombre:
                continue
            registros = self.asistencias[key].get(nombre, {fecha: "" for fecha in self.dias_semana})
            valores = [nombre] + [registros.get(fecha,"") for fecha in self.dias_semana]
            self.tree.insert("", "end", values=valores)

    # ----------------- Interacción: editar celda (solo día actual) -----------------
    def on_cell_click(self, event):
        region = self.tree.identify("region", event.x, event.y)
        if region != "cell":
            return

        row_id = self.tree.identify_row(event.y)
        col_id = self.tree.identify_column(event.x)
        if not row_id or not col_id:
            return
        col_num = int(col_id.replace("#","")) - 1
        if col_num == 0:
            return  # columna alumno

        # obtener alumno y fecha
        alumno = self.tree.item(row_id, "values")[0]
        fecha = self.dias_semana[col_num-1]   # dd/mm/YYYY

        # permitir edición solo si la fecha coincide con hoy
        hoy_str = date.today().strftime("%d/%m/%Y")
        if fecha != hoy_str:
            # opcional: avisar con tooltip o nada; aquí no hacemos nada
            return

        # mostrar menú contextual para elegir valor
        menu = tk.Menu(self, tearoff=0)
        for valor in ["A", "F", "R", "J"]:
            menu.add_command(label=valor, command=lambda v=valor, rid=row_id, cnum=col_num, a=alumno, f=fecha: self.set_valor(rid, cnum, a, f, v))
        menu.post(self.winfo_pointerx(), self.winfo_pointery())


    def set_valor(self, row_id, col_num, alumno, fecha, valor):
        parcial = int(self.parcial_var.get())
        semana_local = int(self.semana_var.get())
        key = f"p{parcial}_s{semana_local}"

        # asegurar existencia
        if key not in self.asistencias:
            self.asistencias[key] = {}
        if alumno not in self.asistencias[key]:
            self.asistencias[key][alumno] = {fecha: ""}

        # guardar en memoria
        self.asistencias[key][alumno][fecha] = valor

        # actualizar celda en la vista (usar nombre de columna)
        col_name = self.tree["columns"][col_num]
        try:
            self.tree.set(row_id, col_name, valor)
        except Exception:
            # fallback: recargar toda la tabla
            self.cargar_tabla()


    # ----------------- Guardar en asistencias.json -----------------
    def guardar_asistencias(self):
        parcial = int(self.parcial_var.get())
        semana_local = int(self.semana_var.get())
        key = f"p{parcial}_s{semana_local}"
        fecha_hoy = date.today().strftime("%d/%m/%Y")
        fecha_hora_iso = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # si faltan valores para hoy, poner "A"
        for alumno, dias in self.asistencias[key].items():
            if dias.get(fecha_hoy, "") == "":
                dias[fecha_hoy] = "A"

        # leer archivo actual como lista
        data = self._leer_json_como_lista()

        # helper para encontrar registro existente por matrícula+dia+parcial+semana
        def encontrar_indice(matricula, dia, parcial_val, semana_val):
            for idx, r in enumerate(data):
                if (str(r.get("Matricula","")) == str(matricula)
                    and r.get("Dia") == dia
                    and int(r.get("Parcial", parcial_val)) == parcial_val
                    and int(r.get("Semana", semana_val)) == semana_val):
                    return idx
            return None

        # actualizar/crear registros para la semana/parcial actual
        for estudiante in self.estudiantes_json:
            nombre = f"{estudiante.get('Nombre completo','')} {estudiante.get('Apellidos','')}".strip()
            matricula = estudiante.get("Matricula", "")
            materia = estudiante.get("Materia", estudiante.get("Materia",""))
            asistencia_val = self.asistencias[key][nombre].get(fecha_hoy, "A")

            registro = {
                "Matricula": matricula,
                "Nombre": nombre,
                "Materia": materia,
                "Grupo": self.grupo_var.get(),
                "Fecha": fecha_hora_iso,
                "Dia": fecha_hoy,
                "Asistencia": asistencia_val,
                "Parcial": parcial,
                "Semana": semana_local
            }

            idx = encontrar_indice(matricula, fecha_hoy, parcial, semana_local)
            if idx is not None:
                # actualizar el registro existente
                data[idx].update(registro)
            else:
                data.append(registro)

        # escribir archivo
        try:
            self._escribir_json_lista(data)
            messagebox.showinfo("Guardado", "Asistencias guardadas en asistencias.json ✅")
        except Exception as ex:
            messagebox.showerror("Error", f"No se pudo guardar el archivo: {ex}")



# función de ayuda para integrarlo desde tu app
def mostrar_asistencia(right_frame, estudiantes_json):
    # limpiar panel derecho y crear la vista
    for w in right_frame.winfo_children():
        w.destroy()
    PantallaAsistencia(right_frame, estudiantes_json)
