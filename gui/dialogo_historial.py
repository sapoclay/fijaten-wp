"""
Fijaten-WP - Diálogo de Historial
Interfaz para ver y comparar escaneos anteriores
"""

import customtkinter as ctk
from tkinter import messagebox
from typing import Optional, Callable

from gui.historial_escaneos import obtener_historial


class DialogoHistorial(ctk.CTkToplevel):
    """Diálogo para ver el historial de escaneos"""
    
    def __init__(self, parent, dominio_actual: Optional[str] = None,
                 callback_cargar: Optional[Callable] = None):
        super().__init__(parent)
        
        self.parent = parent
        self.dominio_actual = dominio_actual
        self.callback_cargar = callback_cargar
        self.historial = obtener_historial()
        self.escaneo_seleccionado = None
        self.escaneos_para_comparar = []
        
        # Configuración de la ventana
        self.title("📚 Historial de Escaneos")
        self.geometry("900x600")
        self.minsize(700, 500)
        
        # Hacer modal la ventana
        self.transient(parent)
        self.grab_set()
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Cargar datos
        self._cargar_historial()
        
        # Centrar ventana
        self.after(100, self._centrar_ventana)
    
    def _centrar_ventana(self):
        """Centra la ventana en la pantalla"""
        self.update_idletasks()
        ancho = self.winfo_width()
        alto = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (ancho // 2)
        y = (self.winfo_screenheight() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    def _crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        # Frame principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header con filtro
        frame_header = ctk.CTkFrame(self)
        frame_header.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        frame_header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_header,
            text="🔍 Filtrar por dominio:",
            font=("", 12)
        ).grid(row=0, column=0, padx=10, pady=10)
        
        self.entry_filtro = ctk.CTkEntry(
            frame_header,
            width=300,
            placeholder_text="Dejar vacío para ver todos..."
        )
        self.entry_filtro.grid(row=0, column=1, padx=10, pady=10, sticky="ew")
        
        if self.dominio_actual:
            self.entry_filtro.insert(0, self.dominio_actual)
        
        self.entry_filtro.bind("<KeyRelease>", lambda e: self._cargar_historial())
        
        ctk.CTkButton(
            frame_header,
            text="🔄 Actualizar",
            width=100,
            command=self._cargar_historial
        ).grid(row=0, column=2, padx=10, pady=10)
        
        # Frame central con lista y detalles
        frame_central = ctk.CTkFrame(self)
        frame_central.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        frame_central.grid_columnconfigure(0, weight=1)
        frame_central.grid_columnconfigure(1, weight=2)
        frame_central.grid_rowconfigure(0, weight=1)
        
        # Lista de escaneos (izquierda)
        frame_lista = ctk.CTkFrame(frame_central)
        frame_lista.grid(row=0, column=0, sticky="nsew", padx=(10, 5), pady=10)
        frame_lista.grid_rowconfigure(1, weight=1)
        frame_lista.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame_lista,
            text="📋 Escaneos",
            font=("", 14, "bold")
        ).grid(row=0, column=0, pady=(10, 5))
        
        # Scrollable frame para la lista
        self.scroll_lista = ctk.CTkScrollableFrame(frame_lista)
        self.scroll_lista.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.scroll_lista.grid_columnconfigure(0, weight=1)
        
        # Detalles del escaneo (derecha)
        frame_detalles = ctk.CTkFrame(frame_central)
        frame_detalles.grid(row=0, column=1, sticky="nsew", padx=(5, 10), pady=10)
        frame_detalles.grid_rowconfigure(1, weight=1)
        frame_detalles.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame_detalles,
            text="📊 Detalles",
            font=("", 14, "bold")
        ).grid(row=0, column=0, pady=(10, 5))
        
        self.texto_detalles = ctk.CTkTextbox(
            frame_detalles,
            font=("Consolas", 11),
            wrap="word"
        )
        self.texto_detalles.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.texto_detalles.configure(state="disabled")
        
        # Frame de acciones (abajo)
        frame_acciones = ctk.CTkFrame(self)
        frame_acciones.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        self.btn_comparar = ctk.CTkButton(
            frame_acciones,
            text="📊 Comparar Seleccionados",
            command=self._comparar_escaneos,
            state="disabled"
        )
        self.btn_comparar.pack(side="left", padx=10, pady=10)
        
        self.btn_eliminar = ctk.CTkButton(
            frame_acciones,
            text="🗑️ Eliminar",
            fg_color="#dc2626",
            hover_color="#b91c1c",
            command=self._eliminar_escaneo,
            state="disabled"
        )
        self.btn_eliminar.pack(side="left", padx=10, pady=10)
        
        ctk.CTkButton(
            frame_acciones,
            text="🧹 Limpiar Todo",
            fg_color="#6b7280",
            hover_color="#4b5563",
            command=self._limpiar_historial
        ).pack(side="left", padx=10, pady=10)
        
        # Estadísticas
        self.label_estadisticas = ctk.CTkLabel(
            frame_acciones,
            text="",
            font=("", 11)
        )
        self.label_estadisticas.pack(side="right", padx=10, pady=10)
        
        ctk.CTkButton(
            frame_acciones,
            text="Cerrar",
            width=80,
            command=self.destroy
        ).pack(side="right", padx=10, pady=10)
    
    def _cargar_historial(self):
        
        """Carga el historial de escaneos"""
        # Limpiar lista actual
        for widget in self.scroll_lista.winfo_children():
            widget.destroy()
        
        self.escaneos_para_comparar = []
        self.escaneo_seleccionado = None
        
        # Obtener filtro
        filtro = self.entry_filtro.get().strip()
        
        # Obtener escaneos
        if filtro:
            escaneos = self.historial.obtener_historial_dominio(filtro)
            # Mostrar estadísticas del dominio
            stats = self.historial.obtener_estadisticas_dominio(filtro)
            if "error" not in stats:
                self.label_estadisticas.configure(
                    text=f"📈 {stats['total_escaneos']} escaneos | {stats['tendencia']}"
                )
            else:
                self.label_estadisticas.configure(text="")
        else:
            escaneos = self.historial.obtener_todos_escaneos()
            self.label_estadisticas.configure(text=f"Total: {len(escaneos)} escaneos")
        
        if not escaneos:
            ctk.CTkLabel(
                self.scroll_lista,
                text="No hay escaneos en el historial",
                text_color="gray"
            ).grid(row=0, column=0, pady=20)
            return
        
        # Crear checkboxes para cada escaneo
        self.checkboxes = {}
        
        for i, escaneo in enumerate(escaneos):
            frame_item = ctk.CTkFrame(self.scroll_lista)
            frame_item.grid(row=i, column=0, sticky="ew", pady=2)
            frame_item.grid_columnconfigure(1, weight=1)
            
            # Checkbox para comparar
            var = ctk.BooleanVar()
            cb = ctk.CTkCheckBox(
                frame_item,
                text="",
                variable=var,
                width=24,
                command=self._actualizar_seleccion
            )
            cb.grid(row=0, column=0, padx=5, pady=5)
            self.checkboxes[escaneo["id"]] = var
            
            # Determinar color según puntuación
            puntuacion = escaneo["puntuacion"]
            if puntuacion >= 80:
                color = "#16a34a"
            elif puntuacion >= 60:
                color = "#ca8a04"
            elif puntuacion >= 40:
                color = "#ea580c"
            else:
                color = "#dc2626"
            
            # Botón con info del escaneo
            texto = f"{escaneo['dominio']}\n{escaneo['fecha_legible']} | {puntuacion}/100"
            btn = ctk.CTkButton(
                frame_item,
                text=texto,
                anchor="w",
                fg_color="transparent",
                text_color=("black", "white"),
                hover_color=("gray90", "gray20"),
                command=lambda e=escaneo: self._seleccionar_escaneo(e)
            )
            btn.grid(row=0, column=1, sticky="ew", padx=5, pady=5)
            
            # Indicador de puntuación
            ctk.CTkLabel(
                frame_item,
                text="●",
                text_color=color,
                font=("", 20)
            ).grid(row=0, column=2, padx=10, pady=5)
    
    def _seleccionar_escaneo(self, escaneo: dict):
        """Muestra los detalles de un escaneo"""
        self.escaneo_seleccionado = escaneo
        self.btn_eliminar.configure(state="normal")
        
        # Cargar datos completos
        datos = self.historial.obtener_escaneo(escaneo["id"])
        if not datos:
            return
        
        # Formatear detalles
        texto = f"""
{'=' * 50}
📊 DETALLES DEL ESCANEO
{'=' * 50}

🌐 Dominio: {datos['dominio']}
📅 Fecha: {datos['fecha_legible']}
🎯 Puntuación: {datos['puntuacion']}/100
🔍 Total vulnerabilidades: {datos['total_vulnerabilidades']}

📋 RESUMEN:
   🔴 Críticas: {datos['resumen']['criticas']}
   🟠 Altas: {datos['resumen']['altas']}
   🟡 Medias: {datos['resumen']['medias']}
   🟢 Bajas: {datos['resumen']['bajas']}
   ℹ️ Info: {datos['resumen']['info']}

{'─' * 50}
🔍 VULNERABILIDADES ENCONTRADAS:
{'─' * 50}
"""
        
        for i, vuln in enumerate(datos['vulnerabilidades'], 1):
            texto += f"\n{i}. [{vuln['severidad']}] {vuln['nombre']}"
        
        if not datos['vulnerabilidades']:
            texto += "\n✅ No se encontraron vulnerabilidades"
        
        # Mostrar en el textbox
        self.texto_detalles.configure(state="normal")
        self.texto_detalles.delete("1.0", "end")
        self.texto_detalles.insert("1.0", texto)
        self.texto_detalles.configure(state="disabled")
    
    def _actualizar_seleccion(self):
        """Actualiza la lista de escaneos seleccionados para comparar"""
        self.escaneos_para_comparar = [
            id_escaneo for id_escaneo, var in self.checkboxes.items()
            if var.get()
        ]
        
        # Habilitar botón de comparar si hay 2 seleccionados
        if len(self.escaneos_para_comparar) == 2:
            self.btn_comparar.configure(state="normal")
        else:
            self.btn_comparar.configure(state="disabled")
    
    def _comparar_escaneos(self):
        """Compara los dos escaneos seleccionados"""
        if len(self.escaneos_para_comparar) != 2:
            messagebox.showwarning("Advertencia", "Selecciona exactamente 2 escaneos para comparar")
            return
        
        id1, id2 = self.escaneos_para_comparar
        
        # Determinar cuál es más antiguo
        escaneo1 = self.historial.obtener_escaneo(id1)
        escaneo2 = self.historial.obtener_escaneo(id2)
        
        if not escaneo1 or not escaneo2:
            messagebox.showerror("Error", "No se pudieron cargar los escaneos seleccionados")
            return
        
        if escaneo1["fecha"] > escaneo2["fecha"]:
            id1, id2 = id2, id1
        
        # Realizar comparación
        comparacion = self.historial.comparar_escaneos(id1, id2)
        
        if "error" in comparacion:
            messagebox.showerror("Error", comparacion["error"])
            return
        
        # Mostrar resultado
        self.texto_detalles.configure(state="normal")
        self.texto_detalles.delete("1.0", "end")
        self.texto_detalles.insert("1.0", comparacion["resumen"])
        self.texto_detalles.configure(state="disabled")
    
    def _eliminar_escaneo(self):
        """Elimina el escaneo seleccionado"""
        if not self.escaneo_seleccionado:
            return
        
        confirmacion = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Eliminar el escaneo del {self.escaneo_seleccionado['fecha_legible']}?"
        )
        
        if confirmacion:
            self.historial.eliminar_escaneo(self.escaneo_seleccionado["id"])
            self._cargar_historial()
            self.texto_detalles.configure(state="normal")
            self.texto_detalles.delete("1.0", "end")
            self.texto_detalles.configure(state="disabled")
            self.btn_eliminar.configure(state="disabled")
    
    def _limpiar_historial(self):
        """Limpia todo el historial"""
        cantidad = len(self.historial.obtener_todos_escaneos())
        
        if cantidad == 0:
            messagebox.showinfo("Info", "El historial ya está vacío")
            return
        



        confirmacion = messagebox.askyesno(
            "Confirmar limpieza",
            f"¿Eliminar TODOS los {cantidad} escaneos del historial?\n\nEsta acción no se puede deshacer."
        )


        
        if confirmacion:
            eliminados = self.historial.limpiar_historial()
            messagebox.showinfo("Completado", f"Se eliminaron {eliminados} escaneos")
            self._cargar_historial()
            self.texto_detalles.configure(state="normal")
            self.texto_detalles.delete("1.0", "end")
            self.texto_detalles.configure(state="disabled")
