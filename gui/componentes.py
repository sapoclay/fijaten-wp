"""
Fijaten-WP - Componentes de la interfaz
Widgets y componentes reutilizables
"""

import customtkinter as ctk
from typing import Callable, Optional


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
        
        # Crear textboxes para cada tab
        self.texto_resumen = ctk.CTkTextbox(
            self.pestana_resumen, 
            font=ctk.CTkFont(family="Consolas", size=13)
        )
        self.texto_resumen.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.texto_detalles = ctk.CTkTextbox(
            self.pestana_detalles, 
            font=ctk.CTkFont(family="Consolas", size=13)
        )
        self.texto_detalles.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.texto_tecnico = ctk.CTkTextbox(
            self.pestana_tecnico, 
            font=ctk.CTkFont(family="Consolas", size=13)
        )
        self.texto_tecnico.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        self.texto_acciones = ctk.CTkTextbox(
            self.pestana_acciones, 
            font=ctk.CTkFont(family="Consolas", size=13)
        )
        self.texto_acciones.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        
        # Mostrar mensaje inicial
        self.mostrar_mensaje(mensaje_inicial)
    
    def obtener_cajas_texto(self):
        """Retorna todas las cajas de texto"""
        return [self.texto_resumen, self.texto_detalles, self.texto_tecnico, self.texto_acciones]
    
    def mostrar_mensaje(self, mensaje: str):
        """Muestra un mensaje en todas las pestañas"""
        for caja_texto in self.obtener_cajas_texto():
            caja_texto.delete("1.0", "end")
            caja_texto.insert("1.0", mensaje)
    
    def limpiar_todo(self):
        """Limpia todas las pestañas"""
        for caja_texto in self.obtener_cajas_texto():
            caja_texto.delete("1.0", "end")
    
    def establecer_contenido(self, resumen: str, detalles: str, tecnico: str, acciones: str):
        """Establece el contenido de cada pestaña"""
        self.limpiar_todo()
        self.texto_resumen.insert("1.0", resumen)
        self.texto_detalles.insert("1.0", detalles)
        self.texto_tecnico.insert("1.0", tecnico)
        self.texto_acciones.insert("1.0", acciones)


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
            actual: Número de verificación actual (1-based)
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
