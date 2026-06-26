import customtkinter as ctk
import json
import os

class QuinielaManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("QuinielaManager")
        self.geometry("1000x600")
        ctk.set_appearance_mode("dark")
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar Completo
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="⚽ QuinielaManager", font=("Arial", 18, "bold")).pack(pady=20)
        
        buttons = [
            (" Registrar resultado", self.action_registrar),
            (" Tabla de posiciones", self.action_tabla),
            (" Ver pronosticos", self.action_pronosticos),
            (" Historial", self.action_historial),
            ("⚙️ Configuracion", self.action_config)
        ]
        for text, command in buttons:
            ctk.CTkButton(self.sidebar, text=text, command=command, fg_color="transparent", anchor="w").pack(pady=5, padx=10, fill="x")

        # Area central
        self.main_frame = ctk.CTkScrollableFrame(self)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def cargar_datos(self):
        if not os.path.exists("data/torneo.json"): return {"carpetas": {"General": []}}
        with open("data/torneo.json", "r", encoding='utf-8') as f: return json.load(f)

    def guardar_datos(self, datos):
        if not os.path.exists("data"): os.makedirs("data")
        with open("data/torneo.json", "w", encoding='utf-8') as f: json.dump(datos, f, indent=4)

    def action_registrar(self):
        for widget in self.main_frame.winfo_children(): widget.destroy()
        datos = self.cargar_datos()
        
        header = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header.pack(fill="x", pady=10)
        ctk.CTkLabel(header, text="Partidos", font=("Arial", 20, "bold")).pack(side="left", padx=10)
        ctk.CTkButton(header, text="Eliminar todo", width=100, fg_color="#CC0000", command=self.confirmar_eliminar_todo).pack(side="right", padx=5)
        ctk.CTkButton(header, text="Nueva carpeta", width=120, fg_color="#2CC985", command=self.ventana_nueva_carpeta).pack(side="right", padx=5)

        for nombre, partidos in datos["carpetas"].items():
            frame_carpeta = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b")
            frame_carpeta.pack(fill="x", pady=10, padx=5)
            
            h_carpeta = ctk.CTkFrame(frame_carpeta, fg_color="transparent")
            h_carpeta.pack(fill="x", pady=5, padx=10)
            ctk.CTkLabel(h_carpeta, text=nombre, font=("Arial", 16, "bold")).pack(side="left")
            ctk.CTkButton(h_carpeta, text="🗑️", width=30, fg_color="#CC0000", command=lambda n=nombre: self.confirmar_eliminar_carpeta(n)).pack(side="right", padx=5)
            ctk.CTkButton(h_carpeta, text="+ Partido", width=80, command=lambda n=nombre: self.ventana_nuevo_partido(n)).pack(side="right", padx=5)

            for p in partidos:
                card = ctk.CTkFrame(frame_carpeta, fg_color="#333333")
                card.pack(fill="x", pady=2, padx=10)
                texto = f"{p['local']} {f'{p['marcador'][0]}-{p['marcador'][1]}' if p['jugado'] else 'vs'} {p['visita']}"
                ctk.CTkLabel(card, text=texto).pack(side="left", padx=10)
                ctk.CTkButton(card, text="🗑️", width=30, fg_color="#CC0000", command=lambda p=p, n=nombre: self.confirmar_eliminar_partido(p, n)).pack(side="right", padx=5)
                ctk.CTkButton(card, text="Marcador", width=70, command=lambda p=p, n=nombre: self.abrir_editor(p, n)).pack(side="right", padx=5)

    # --- Confirmaciones ---
    def confirmar_eliminar_carpeta(self, nombre):
        ventana = ctk.CTkToplevel(self); ventana.title("Confirmar"); ventana.geometry("350x150")
        ctk.CTkLabel(ventana, text=f"¿Seguro que quieres eliminar\nla carpeta '{nombre}'?").pack(pady=20)
        ctk.CTkButton(ventana, text="Confirmar eliminacion", fg_color="#CC0000", command=lambda: self.eliminar_carpeta(nombre, ventana)).pack()

    def confirmar_eliminar_partido(self, p, carpeta):
        ventana = ctk.CTkToplevel(self); ventana.title("Confirmar"); ventana.geometry("350x150")
        ctk.CTkLabel(ventana, text=f"¿Seguro que quieres eliminar\n{p['local']} vs {p['visita']}?").pack(pady=20)
        ctk.CTkButton(ventana, text="Confirmar eliminacion", fg_color="#CC0000", command=lambda: self.eliminar_partido(p, carpeta, ventana)).pack()

    def confirmar_eliminar_todo(self):
        ventana = ctk.CTkToplevel(self); ventana.title("Confirmar"); ventana.geometry("350x150")
        ctk.CTkLabel(ventana, text="¡CUIDADO!\n¿Eliminar TODOS los partidos?", font=("Arial", 12, "bold")).pack(pady=20)
        ctk.CTkButton(ventana, text="SI, BORRAR TODO", fg_color="#CC0000", command=lambda: self.borrar_todo(ventana)).pack()

    # --- Acciones de Datos ---
    def eliminar_carpeta(self, nombre, ventana):
        datos = self.cargar_datos(); del datos["carpetas"][nombre]
        self.guardar_datos(datos); ventana.destroy(); self.action_registrar()

    def eliminar_partido(self, p, carpeta, ventana):
        datos = self.cargar_datos(); datos["carpetas"][carpeta].remove(p)
        self.guardar_datos(datos); ventana.destroy(); self.action_registrar()

    def borrar_todo(self, ventana):
        self.guardar_datos({"carpetas": {"General": []}}); ventana.destroy(); self.action_registrar()

    def ventana_nueva_carpeta(self):
        ventana = ctk.CTkToplevel(self); ventana.title("Nueva Carpeta")
        ent = ctk.CTkEntry(ventana, placeholder_text="Nombre carpeta"); ent.pack(pady=20, padx=20)
        ctk.CTkButton(ventana, text="Guardar", command=lambda: self.guardar_carpeta(ent.get(), ventana)).pack(pady=10)

    def guardar_carpeta(self, nombre, ventana):
        datos = self.cargar_datos()
        if nombre and nombre not in datos["carpetas"]: datos["carpetas"][nombre] = []; self.guardar_datos(datos)
        ventana.destroy(); self.action_registrar()

    def ventana_nuevo_partido(self, carpeta):
        ventana = ctk.CTkToplevel(self); ventana.title("Nuevo Partido")
        ent_l = ctk.CTkEntry(ventana, placeholder_text="Local"); ent_l.pack(pady=5)
        ent_v = ctk.CTkEntry(ventana, placeholder_text="Visita"); ent_v.pack(pady=5)
        ctk.CTkButton(ventana, text="Guardar", command=lambda: self.guardar_partido(carpeta, ent_l.get(), ent_v.get(), ventana)).pack(pady=10)

    def guardar_partido(self, carpeta, local, visita, ventana):
        datos = self.cargar_datos()
        datos["carpetas"][carpeta].append({"local": local, "visita": visita, "marcador": [0,0], "jugado": False})
        self.guardar_datos(datos); ventana.destroy(); self.action_registrar()

    def abrir_editor(self, partido, carpeta):
        ventana = ctk.CTkToplevel(self); ventana.title("Marcador")
        ent_l = ctk.CTkEntry(ventana, placeholder_text="Goles Local"); ent_l.pack(pady=5)
        ent_v = ctk.CTkEntry(ventana, placeholder_text="Goles Visita"); ent_v.pack(pady=5)
        ctk.CTkButton(ventana, text="Guardar", command=lambda: self.guardar_resultado(partido, carpeta, ent_l.get(), ent_v.get(), ventana)).pack(pady=10)

    def guardar_resultado(self, partido, carpeta, l, v, ventana):
        datos = self.cargar_datos()
        for p in datos["carpetas"][carpeta]:
            if p["local"] == partido["local"] and p["visita"] == partido["visita"]:
                p["marcador"] = [int(l), int(v)]; p["jugado"] = True
        self.guardar_datos(datos); ventana.destroy(); self.action_registrar()

    def action_tabla(self): pass
    def action_pronosticos(self): pass
    def action_historial(self): pass
    def action_config(self): pass

if __name__ == "__main__":
    app = QuinielaManagerApp(); app.mainloop()