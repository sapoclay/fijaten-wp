"""
Fijaten-WP - Componentes de la interfaz
Widgets y componentes reutilizables
"""

import customtkinter as ctk
import webbrowser
import re
from typing import Callable


class FrameCabecera(ctk.CTkFrame):
    
    """Frame de cabecera con título y subtítulo"""
    
    def __init__(self, parent, titulo: str, subtitulo: str):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        
        self.etiqueta_titulo = ctk.CTkLabel(
            self,
            text=titulo,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        self.etiqueta_titulo.pack(side="left")
        
        self.etiqueta_subtitulo = ctk.CTkLabel(
            self,
            text=subtitulo,
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        self.etiqueta_subtitulo.pack(side="left", padx=(20, 0))


class FrameEntrada(ctk.CTkFrame):
    
    """Frame de entrada con campo de dominio y botón de análisis"""
    
    def __init__(self, parent, al_analizar: Callable):
        super().__init__(parent)
        self.grid_columnconfigure(1, weight=1)
        self.al_analizar = al_analizar
        
        # Label
        self.etiqueta_dominio = ctk.CTkLabel(
            self,
            text="🌐 Dominio:",
            font=ctk.CTkFont(size=16)
        )
        self.etiqueta_dominio.grid(row=0, column=0, padx=(15, 10), pady=15)
        
        # Entry para el dominio
        self.entrada_dominio = ctk.CTkEntry(
            self,
            placeholder_text="Ejemplo: misitioweb.com o https://misitioweb.com",
            height=40,
            font=ctk.CTkFont(size=14)
        )
        self.entrada_dominio.grid(row=0, column=1, padx=10, pady=15, sticky="ew")
        self.entrada_dominio.bind("<Return>", lambda e: al_analizar())
        
        # Configurar menú contextual (clic derecho)
        self._configurar_menu_contextual()
        
        # Botón de escanear
        self.boton_escanear = ctk.CTkButton(
            self,
            text="🔍 Analizar",
            font=ctk.CTkFont(size=15, weight="bold"),
            height=40,
            width=140,
            command=al_analizar
        )
        self.boton_escanear.grid(row=0, column=2, padx=(10, 15), pady=15)
    
    def _configurar_menu_contextual(self):
        
        """Configura el menú contextual para el campo de entrada"""
        
        import tkinter as tk
        
        # Crear menú contextual nativo de tkinter
        self.menu_contextual = tk.Menu(self, tearoff=0)
        
        # Opciones del menú
        self.menu_contextual.add_command(
            label="📋 Pegar",
            command=self._pegar
        )
        self.menu_contextual.add_command(
            label="📄 Copiar",
            command=self._copiar
        )
        self.menu_contextual.add_command(
            label="✂️ Cortar",
            command=self._cortar
        )
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(
            label="🔘 Seleccionar todo",
            command=self._seleccionar_todo
        )
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(
            label="🗑️ Limpiar",
            command=self._limpiar
        )
        self.menu_contextual.add_separator()
        self.menu_contextual.add_command(
            label="🔍 Analizar",
            command=self.al_analizar
        )
        
        # Vincular clic derecho - se utiliza after para evitar bloqueos
        self.entrada_dominio.bind("<Button-3>", self._mostrar_menu_contextual)
    
    def _mostrar_menu_contextual(self, event):
        
        """Muestra el menú contextual en la posición del clic"""
        
        try:
            self.entrada_dominio.focus_set()
            # Usamos after(1, ...) para evitar bloqueo del evento
            self.after(1, lambda: self.menu_contextual.tk_popup(event.x_root, event.y_root))
        except Exception:
            pass
    
    def _pegar(self):
        
        """Pega el contenido del portapapeles"""
        
        try:
            # Obtener texto del portapapeles
            texto = self.winfo_toplevel().clipboard_get()
            # Obtener posición actual del cursor
            entry = self.entrada_dominio
            # Insertar en la posición actual o al final
            pos = entry._entry.index("insert")
            contenido_actual = entry.get()
            nuevo_contenido = contenido_actual[:pos] + texto + contenido_actual[pos:]
            entry.delete(0, "end")
            entry.insert(0, nuevo_contenido)
            # Mover cursor al final del texto pegado
            entry._entry.icursor(pos + len(texto))
        except Exception as e:
            print(f"Error al pegar: {e}")
    
    def _copiar(self):
        
        """Copia el texto seleccionado al portapapeles"""
        
        try:
            # Intentar obtener selección
            entry = self.entrada_dominio._entry
            if entry.selection_present():
                texto = entry.selection_get()
                toplevel = self.winfo_toplevel()
                toplevel.clipboard_clear()
                toplevel.clipboard_append(texto)
                toplevel.update()
        except Exception as e:
            print(f"Error al copiar: {e}")
    
    def _cortar(self):
        """Corta el texto seleccionado"""
        try:
            entry = self.entrada_dominio._entry
            if entry.selection_present():
                texto = entry.selection_get()
                toplevel = self.winfo_toplevel()
                toplevel.clipboard_clear()
                toplevel.clipboard_append(texto)
                toplevel.update()
                entry.delete("sel.first", "sel.last")
        except Exception as e:
            print(f"Error al cortar: {e}")
    
    def _seleccionar_todo(self):
        
        """Selecciona todo el texto"""
        
        self.entrada_dominio._entry.select_range(0, "end")
        self.entrada_dominio._entry.icursor("end")
    
    def _limpiar(self):
        
        """Limpia el campo de entrada"""
        
        self.entrada_dominio.delete(0, "end")
    
    def obtener_dominio(self) -> str:
        
        """Obtiene el dominio ingresado"""
        
        return self.entrada_dominio.get().strip()
    
    def establecer_escaneando(self, escaneando: bool):
        
        """Configura el estado de escaneo"""
        
        if escaneando:
            self.boton_escanear.configure(state="disabled", text="⏳ Analizando...")
        else:
            self.boton_escanear.configure(state="normal", text="🔍 Analizar")


class FrameResultados(ctk.CTkFrame):
    
    """Frame de resultados con pestañas"""
    
    # Fuentes monoespaciadas en orden de preferencia
    FUENTES_MONO = ["DejaVu Sans Mono", "Liberation Mono", "Ubuntu Mono", "Consolas", "Courier New", "monospace"]
    
    def __init__(self, parent, mensaje_inicial: str):
        super().__init__(parent)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Tabs para diferentes vistas
        
        self.vista_pestanas = ctk.CTkTabview(self)
        self.vista_pestanas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        # Crear tabs
        
        self.pestana_resumen = self.vista_pestanas.add("📊 Resumen")
        self.pestana_detalles = self.vista_pestanas.add("🔍 Detalles")
        self.pestana_tecnico = self.vista_pestanas.add("⚙️ Técnico")
        self.pestana_acciones = self.vista_pestanas.add("✅ Plan de acción")
        
        # Configurar cada tab
        
        for pestana in [self.pestana_resumen, self.pestana_detalles, self.pestana_tecnico, self.pestana_acciones]:
            pestana.grid_columnconfigure(0, weight=1)
            pestana.grid_rowconfigure(0, weight=1)
        
        # Obtener fuente monoespaciada disponible en el sistema
        fuente_mono = self._obtener_fuente_mono()
        
        # Crear textboxes para cada tab (solo lectura)
        self.texto_resumen = ctk.CTkTextbox(
            self.pestana_resumen, 
            font=ctk.CTkFont(family=fuente_mono, size=13),
            state="disabled"  # Solo lectura
        )
        self.texto_resumen.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.texto_detalles = ctk.CTkTextbox(
            self.pestana_detalles, 
            font=ctk.CTkFont(family=fuente_mono, size=13),
            state="disabled"  # Solo lectura
        )
        self.texto_detalles.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.texto_tecnico = ctk.CTkTextbox(
            self.pestana_tecnico, 
            font=ctk.CTkFont(family=fuente_mono, size=13),
            state="disabled"  # Solo lectura
        )
        self.texto_tecnico.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.texto_acciones = ctk.CTkTextbox(
            self.pestana_acciones, 
            font=ctk.CTkFont(family=fuente_mono, size=13),
            state="disabled"  # Solo lectura
        )
        self.texto_acciones.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Configurar enlaces clicables en todos los textboxes
        for textbox in self.obtener_cajas_texto():
            self._configurar_enlaces(textbox)
        
        # Mostrar mensaje inicial
        self.mostrar_mensaje(mensaje_inicial)
    
    def obtener_cajas_texto(self):
        """Retorna todas las cajas de texto"""
        return [self.texto_resumen, self.texto_detalles, self.texto_tecnico, self.texto_acciones]
    
    def _obtener_fuente_mono(self) -> str:
        """Obtiene la primera fuente monoespaciada disponible en el sistema"""
        import tkinter.font as tkfont
        
        try:
            # Intentar obtener las fuentes disponibles
            fuentes_disponibles = tkfont.families()
            
            # Buscar la primera fuente monoespaciada disponible
            for fuente in self.FUENTES_MONO:
                if fuente.lower() in [f.lower() for f in fuentes_disponibles]:
                    return fuente
            
            # Si ninguna está disponible, usar monospace como fallback
            return "monospace"
        except Exception:
            return "monospace"
    
    def _configurar_enlaces(self, textbox: ctk.CTkTextbox):
        """Configura el textbox para detectar y hacer clicables los enlaces"""
        # Obtener el widget Text interno de customtkinter
        widget_interno = textbox._textbox
        
        # Configurar el tag para enlaces
        widget_interno.tag_configure(
            "enlace",
            foreground="#3391ff",
            underline=True
        )
        
        # Cambiar cursor al pasar sobre enlaces
        widget_interno.tag_bind("enlace", "<Enter>", 
            lambda e: widget_interno.configure(cursor="hand2"))
        widget_interno.tag_bind("enlace", "<Leave>", 
            lambda e: widget_interno.configure(cursor="xterm"))
        
        # Abrir enlace al hacer clic
        widget_interno.tag_bind("enlace", "<Button-1>", 
            lambda e: self._abrir_enlace(widget_interno, e))
    
    def _abrir_enlace(self, widget, event):
        """Abre el enlace en el navegador por defecto"""
        import subprocess
        import os
        
        # Obtener el índice del clic
        index = widget.index(f"@{event.x},{event.y}")
        
        # Buscar los rangos del tag "enlace" en esa posición
        tag_ranges = widget.tag_ranges("enlace")
        
        for i in range(0, len(tag_ranges), 2):
            start = tag_ranges[i]
            end = tag_ranges[i + 1]
            
            # Verificar si el clic está dentro de este rango
            if widget.compare(start, "<=", index) and widget.compare(index, "<", end):
                # Obtener el texto del enlace
                url = widget.get(start, end)
                try:
                    # Abrir sin mostrar mensajes del navegador en la terminal
                    if os.name == 'nt':  # Windows
                        os.startfile(url)
                    elif os.name == 'posix':  # Linux/macOS
                        # Redirigir stdout/stderr para evitar mensajes del navegador
                        subprocess.Popen(
                            ['xdg-open', url],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            start_new_session=True
                        )
                except Exception:
                    # Fallback a webbrowser
                    webbrowser.open(url)
                break
    
    def _detectar_y_marcar_enlaces(self, textbox: ctk.CTkTextbox):
        """Detecta URLs en el texto y las marca con el tag 'enlace'"""
        widget_interno = textbox._textbox
        
        # Eliminar tags de enlaces anteriores
        widget_interno.tag_remove("enlace", "1.0", "end")
        
        # Obtener todo el texto
        contenido = widget_interno.get("1.0", "end-1c")
        
        # Patrón para detectar URLs
        patron_url = r'https?://[^\s<>"\'{}|\\^`\[\]()]+'
        
        # Encontrar todas las URLs con sus posiciones
        urls_encontradas = []
        for match in re.finditer(patron_url, contenido):
            url = match.group()
            # Limpiar puntuación final
            while url and url[-1] in '.,;:!?)]}':
                url = url[:-1]
            if url and len(url) >= 10:
                urls_encontradas.append(url)
        

        # Marcar cada URL encontrada usando búsqueda en el widget
        for url in urls_encontradas:
            inicio_busqueda = "1.0"
            while True:
                pos_inicio = widget_interno.search(url, inicio_busqueda, stopindex="end", exact=True)
                if not pos_inicio:
                    break
                
                # Calcular posición final
                pos_fin = f"{pos_inicio}+{len(url)}c"
                
                # Aplicar tag
                widget_interno.tag_add("enlace", pos_inicio, pos_fin)
                
                # Continuar buscando después de esta ocurrencia
                inicio_busqueda = pos_fin
    
    def _escribir_en_textbox(self, textbox: ctk.CTkTextbox, contenido: str):
        
        """Escribe contenido en un textbox de solo lectura"""
        
        textbox.configure(state="normal")  # Habilitar temporalmente
        textbox.delete("1.0", "end")
        textbox.insert("1.0", contenido)
        
        # Detectar y marcar enlaces clicables
        self._detectar_y_marcar_enlaces(textbox)
        textbox.configure(state="disabled")  # Volver a solo lectura
    
    def mostrar_mensaje(self, mensaje: str):
        
        """Muestra un mensaje en todas las pestañas"""
        
        for caja_texto in self.obtener_cajas_texto():
            self._escribir_en_textbox(caja_texto, mensaje)
    
    def limpiar_todo(self):
        
        """Limpia todas las pestañas"""
        
        for caja_texto in self.obtener_cajas_texto():
            caja_texto.configure(state="normal")
            caja_texto.delete("1.0", "end")
            caja_texto.configure(state="disabled")
    
    def establecer_contenido(self, resumen: str, detalles: str, tecnico: str, acciones: str):
        """Establece el contenido de cada pestaña"""
        self._escribir_en_textbox(self.texto_resumen, resumen)
        self._escribir_en_textbox(self.texto_detalles, detalles)
        self._escribir_en_textbox(self.texto_tecnico, tecnico)
        self._escribir_en_textbox(self.texto_acciones, acciones)


class FramePie(ctk.CTkFrame):
    """Frame de pie con barra de progreso detallada y botones"""
    
    def __init__(self, parent, al_guardar: Callable, al_limpiar: Callable):
        super().__init__(parent, corner_radius=0, fg_color="transparent")
        self.grid_columnconfigure(0, weight=1)
        
        # Frame para la barra de progreso y etiqueta de verificación
        self.frame_progreso = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_progreso.grid(row=0, column=0, sticky="ew", padx=(0, 10), pady=5)
        self.frame_progreso.grid_columnconfigure(0, weight=1)
        
        # Etiqueta de verificación actual (encima de la barra)
        self.etiqueta_verificacion = ctk.CTkLabel(
            self.frame_progreso,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.etiqueta_verificacion.grid(row=0, column=0, sticky="w", pady=(0, 2))
        
        # Barra de progreso
        self.barra_progreso = ctk.CTkProgressBar(self.frame_progreso)
        self.barra_progreso.grid(row=1, column=0, sticky="ew", pady=0)
        self.barra_progreso.set(0)
        
        # Etiqueta de porcentaje
        self.etiqueta_porcentaje = ctk.CTkLabel(
            self.frame_progreso,
            text="",
            font=ctk.CTkFont(size=11, weight="bold"),
            width=50
        )
        self.etiqueta_porcentaje.grid(row=1, column=1, padx=(10, 0))
        
        # Label de estado
        self.etiqueta_estado = ctk.CTkLabel(
            self,
            text="Listo para analizar",
            font=ctk.CTkFont(size=12)
        )
        self.etiqueta_estado.grid(row=1, column=0, sticky="w", pady=(5, 0))
        
        # Frame para botones
        self.frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_botones.grid(row=0, column=1, rowspan=2, sticky="e")
        
        # Botón guardar informe
        self.boton_guardar = ctk.CTkButton(
            self.frame_botones,
            text="💾 Guardar Informe",
            width=130,
            state="disabled",
            command=al_guardar
        )
        self.boton_guardar.pack(side="left", padx=5)
        
        # Botón limpiar
        self.boton_limpiar = ctk.CTkButton(
            self.frame_botones,
            text="🗑️ Limpiar",
            width=100,
            fg_color="gray",
            hover_color="darkgray",
            command=al_limpiar
        )
        self.boton_limpiar.pack(side="left", padx=5)
        
        # Variables para tracking de progreso
        self._progreso_actual = 0
        self._total_verificaciones = 0
        self._verificacion_actual = ""
    
    def establecer_estado(self, mensaje: str):
        """Actualiza el mensaje de estado"""
        self.etiqueta_estado.configure(text=mensaje)
    
    def establecer_verificacion_actual(self, verificacion: str, actual: int = 0, total: int = 0):
        """
        Muestra qué verificación se está ejecutando actualmente
        
        Args:
            verificacion: Nombre de la verificación en curso
            actual: Número de verificación actual 
            total: Total de verificaciones a realizar
        """
        self._verificacion_actual = verificacion
        self._progreso_actual = actual
        self._total_verificaciones = total
        
        if total > 0:
            texto = f"🔍 [{actual}/{total}] {verificacion}"
            porcentaje = int((actual / total) * 100)
            self.etiqueta_porcentaje.configure(text=f"{porcentaje}%")
            
            # Actualizar barra de progreso si no está en modo indeterminado
            try:
                self.barra_progreso.set(actual / total)
            except Exception:
                pass
        else:
            texto = f"🔍 {verificacion}"
            self.etiqueta_porcentaje.configure(text="")
        
        self.etiqueta_verificacion.configure(text=texto)
    
    def limpiar_verificacion(self):
        
        """Limpia la etiqueta de verificación"""
        self.etiqueta_verificacion.configure(text="")
        self.etiqueta_porcentaje.configure(text="")
        self._verificacion_actual = ""
        self._progreso_actual = 0
        self._total_verificaciones = 0
    
    def establecer_progreso(self, valor: float):
        
        """Establece el valor del progreso (0-1)"""
        self.barra_progreso.set(valor)
        if valor > 0:
            self.etiqueta_porcentaje.configure(text=f"{int(valor * 100)}%")
        else:
            self.etiqueta_porcentaje.configure(text="")
    
    def iniciar_progreso(self):
        """Inicia la animación de progreso indeterminado"""
        self.barra_progreso.configure(mode="indeterminate")
        self.barra_progreso.start()
    
    def detener_progreso(self):
        """Detiene la animación de progreso"""
        self.barra_progreso.stop()
        self.barra_progreso.configure(mode="determinate")
        self.limpiar_verificacion()
    
    def habilitar_guardar(self, habilitado: bool = True):
        """Habilita o deshabilita el botón de guardar"""
        self.boton_guardar.configure(state="normal" if habilitado else "disabled")
