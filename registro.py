import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import json
import pandas as pd
from PyPDF2 import PdfReader

class RegistroEstudiantes(tk.Frame):
    def __init__(self, master):
        super().__init__(master, bg="white")
        self.pack(fill="both", expand=True)

        tk.Label(self, text="Registro de Estudiantes", font=("Arial", 16, "bold"), bg="white").pack(pady=10)

        # Botones principales
        btn_frame = tk.Frame(self, bg="white")
        btn_frame.pack(pady=10)

        tk.Button(btn_frame, text="Importar Lista", command=self.importar_lista, bg="#145374", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Exportar", command=self.exportar_lista, bg="#145374", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="+ Agregar", command=self.agregar_manual, bg="#145374", fg="white", font=("Arial", 12)).pack(side="left", padx=5)
        tk.Button(btn_frame, text="Editar estudiante", command=self.editar_estudiante, bg="#145374", fg="white", font=("Arial", 12)).pack(side="left", padx=5)

        # Buscador
        search_frame = tk.Frame(self, bg="white")
        search_frame.pack(pady=10)
        self.search_var = tk.StringVar()
        tk.Label(search_frame, text="Buscar estudiante:", bg="white").pack(side="left", padx=5)
        tk.Entry(search_frame, textvariable=self.search_var, width=30).pack(side="left")
        tk.Button(search_frame, text="Buscar", command=self.buscar_estudiante, bg="#145374", fg="white").pack(side="left", padx=5)

        self.mostrar_tabla_estudiantes()

    def importar_lista(self):
        archivo = filedialog.askopenfilename(title="Selecciona archivo", filetypes=[
            ("Archivos Excel", "*.xlsx"),
            ("Archivos CSV", "*.csv"),
            ("Archivos PDF", "*.pdf")
        ])
        if not archivo:
            return

        try:
            if archivo.endswith(".xlsx"):
                df = pd.read_excel(archivo)
            elif archivo.endswith(".csv"):
                df = pd.read_csv(archivo)
            elif archivo.endswith(".pdf"):
                reader = PdfReader(archivo)
                texto = ""
                for page in reader.pages:
                    texto += page.extract_text()
                messagebox.showinfo("PDF leído", "Contenido:\n" + texto[:500])
                return
            else:
                messagebox.showerror("Formato no soportado", "Solo se aceptan archivos PDF, Excel o CSV.")
                return

            lista = df.to_dict(orient="records")
            with open("estudiantes.json", "w", encoding="utf-8") as f:
                json.dump(lista, f, indent=4, ensure_ascii=False)
            messagebox.showinfo("Importación exitosa", f"{len(lista)} estudiantes importados.")
            self.mostrar_tabla_estudiantes()
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo importar: {e}")

    def exportar_lista(self):
        try:
            with open("estudiantes.json", "r", encoding="utf-8") as f:
                lista = json.load(f)
            df = pd.DataFrame(lista)
            archivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[
                ("Excel", "*.xlsx"),
                ("CSV", "*.csv")
            ])
            if archivo.endswith(".xlsx"):
                df.to_excel(archivo, index=False)
            elif archivo.endswith(".csv"):
                df.to_csv(archivo, index=False)
            messagebox.showinfo("Exportación", "Lista exportada correctamente.")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar: {e}")

    def buscar_estudiante(self):
        criterio = self.search_var.get().lower()
        try:
            with open("estudiantes.json", "r", encoding="utf-8") as f:
                lista = json.load(f)
            resultados = [est for est in lista if criterio in est.get("Nombre completo", "").lower() or criterio in est.get("Matricula", "").lower()]
            if resultados:
                mensaje = "\n".join([f"{e['Nombre completo']} - {e['Matricula']}" for e in resultados])
                messagebox.showinfo("Resultados", mensaje)
            else:
                messagebox.showinfo("Sin resultados", "No se encontró ningún estudiante.")
        except:
            messagebox.showerror("Error", "No se pudo buscar en la lista.")

    def agregar_manual(self):
        ventana = tk.Toplevel(self)
        ventana.title("Agregar estudiante")
        ventana.geometry("400x400")
        ventana.config(bg="white")

        campos = {
            "Nombre completo": tk.StringVar(),
            "Apellidos": tk.StringVar(),
            "Matricula": tk.StringVar(),
            "Correo": tk.StringVar(),
            "Grupo": tk.StringVar(),
            "Materia": tk.StringVar(),
            "Programa": tk.StringVar(),
            "Docente": tk.StringVar()
        }

        for campo, var in campos.items():
            frame = tk.Frame(ventana, bg="white")
            frame.pack(pady=3)
            tk.Label(frame, text=campo + ":", width=15, anchor="w", bg="white").pack(side="left")
            tk.Entry(frame, textvariable=var, width=25).pack(side="left")

        def guardar():
            datos = {k: v.get() for k, v in campos.items()}
            if all(datos.values()):
                try:
                    with open("estudiantes.json", "r", encoding="utf-8") as f:
                        lista = json.load(f)
                except:
                    lista = []
                lista.append(datos)
                with open("estudiantes.json", "w", encoding="utf-8") as f:
                    json.dump(lista, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Guardado", "Estudiante agregado.")
                ventana.destroy()
                self.mostrar_tabla_estudiantes()
            else:
                messagebox.showwarning("Campos incompletos", "Completa todos los campos.")

        tk.Button(ventana, text="Guardar", command=guardar, bg="#145374", fg="white", font=("Arial", 12)).pack(pady=10)

    def editar_estudiante(self):
        ventana = tk.Toplevel(self)
        ventana.title("Editar estudiante")
        ventana.geometry("400x500")
        ventana.config(bg="white")

        search_var = tk.StringVar()

        tk.Label(ventana, text="Buscar por matrícula:", bg="white", font=("Arial", 12)).pack(pady=10)
        tk.Entry(ventana, textvariable=search_var, width=30).pack()

        def buscar():
            criterio = search_var.get().strip().lower()
            try:
                with open("estudiantes.json", "r", encoding="utf-8") as f:
                    lista = json.load(f)
            except:
                lista = []

            coincidencias = [e for e in lista if criterio in e.get("Matricula", "").lower()]
            if not coincidencias:
                messagebox.showinfo("Sin resultados", "No se encontró ningún estudiante.")
                return

            estudiante = coincidencias[0]
            campos = {k: tk.StringVar(value=estudiante.get(k, "")) for k in estudiante.keys()}

            form_frame = tk.Frame(ventana, bg="white")
            form_frame.pack(pady=10)

            for campo, var in campos.items():
                fila = tk.Frame(form_frame, bg="white")
                fila.pack(pady=3)
                tk.Label(fila, text=campo + ":", width=15, anchor="w", bg="white").pack(side="left")
                tk.Entry(fila, textvariable=var, width=25).pack(side="left")

            def guardar():
                nuevos_datos = {k: v.get() for k, v in campos.items()}
                for i, est in enumerate(lista):
                    if est.get("Matricula", "").lower() == criterio:
                        lista[i] = nuevos_datos
                        break
                with open("estudiantes.json", "w", encoding="utf-8") as f:
                    json.dump(lista, f, indent=4, ensure_ascii=False)
                messagebox.showinfo("Actualizado", "Estudiante editado correctamente.")
                ventana.destroy()
                self.mostrar_tabla_estudiantes()

            tk.Button(ventana, text="Guardar cambios", command=guardar, bg="#145374", fg="white", font=("Arial", 12)).pack(pady=10)

        tk.Button(ventana, text="Buscar", command=buscar, bg="#145374", fg="white", font=("Arial", 12)).pack(pady=10)

    def mostrar_tabla_estudiantes(self):
        try:
            with open("estudiantes.json", "r", encoding="utf-8") as f:
                lista = json.load(f)
        except:
            lista = []

        # Destruir tabla anterior si existe
        if hasattr(self, "tabla_frame") and self.tabla_frame:
            self.tabla_frame.destroy()

        self.tabla_frame = tk.Frame(self, bg="white")
        self.tabla_frame.pack(fill="both", expand=True, pady=10)

        columnas = ["Matricula", "Nombre completo", "Apellidos", "Grupo", "Materia", "Programa", "Docente", "Correo"]

        tree = ttk.Treeview(self.tabla_frame, columns=columnas, show="headings")
        for col in columnas:
            tree.heading(col, text=col)
            tree.column(col, width=120)

        # Agrupar por grupo
        grupos = {}
        for est in lista:
            grupo = est.get("Grupo", "Sin grupo")
            grupos.setdefault(grupo, []).append(est)

        for grupo, estudiantes in grupos.items():
            for est in estudiantes:
                tree.insert("", "end", values=[est.get(c, "") for c in columnas])

        # Scroll vertical
        scrollbar = ttk.Scrollbar(self.tabla_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        tree.pack(fill="both", expand=True)