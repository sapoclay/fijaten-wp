"""
Fijaten-WP - Barra de Menú
Menú superior de la aplicación
"""

import customtkinter as ctk
import tkinter as tk
import platform
from typing import Callable, Optional

from gui.gestor_temas import obtener_gestor_temas, TEMAS_APARIENCIA
from gui.notificaciones import obtener_notificador
from gui.dialogo_atajos import DialogoAtajos


# Detectar sistema operativo para atajos de teclado
ES_MAC = platform.system() == "Darwin"
ES_WINDOWS = platform.system() == "Windows"

# Tecla modificadora según el SO
MOD_KEY = "Command" if ES_MAC else "Control"
MOD_KEY_DISPLAY = "Cmd" if ES_MAC else "Ctrl"


class BarraMenu:
    """Barra de menú para la aplicación"""
    
    def __init__(self, parent: ctk.CTk, on_exit: Callable, on_about: Callable, 
                 on_options: Optional[Callable] = None,
                 on_escaneo_multiple: Optional[Callable] = None,
                 on_exportar_pdf: Optional[Callable] = None,
                 on_exportar_html: Optional[Callable] = None,
                 on_historial: Optional[Callable] = None,
                 on_guardar: Optional[Callable] = None):
        self.parent = parent
        self.al_salir = on_exit
        self.al_acerca_de = on_about
        self.al_opciones = on_options
        self.al_escaneo_multiple = on_escaneo_multiple
        self.al_exportar_pdf = on_exportar_pdf
        self.al_exportar_html = on_exportar_html
        self.al_historial = on_historial
        self.al_guardar = on_guardar
        
        # Obtener gestores
        self.gestor_temas = obtener_gestor_temas()
        self.notificador = obtener_notificador()
        
        # Variables para checkboxes del menú
        self.var_notificaciones = tk.BooleanVar(value=self.notificador.estan_habilitadas())
        self.var_sonido = tk.BooleanVar(value=self.notificador.sonido_habilitado())
        
        # Crear barra de menú usando tkinter nativo
        self.barra_menu = tk.Menu(parent)
        parent.configure(menu=self.barra_menu)
        
        # Crear menús
        self._crear_menu_archivo()
        self._crear_menu_herramientas()
        self._crear_menu_preferencias()
        self._crear_menu_ayuda()
    
    def _vincular_atajo(self, tecla: str, callback: Callable):
        """Vincula un atajo de teclado de forma multiplataforma"""
        # Vincular con Control (Windows/Linux)
        self.parent.bind(f"<Control-{tecla.lower()}>", lambda e: callback())
        self.parent.bind(f"<Control-{tecla.upper()}>", lambda e: callback())
        
        # Vincular también con Command en macOS
        if ES_MAC:
            self.parent.bind(f"<Command-{tecla.lower()}>", lambda e: callback())
            self.parent.bind(f"<Command-{tecla.upper()}>", lambda e: callback())
    
    def _crear_menu_archivo(self):
        """Crea el menú Archivo"""
        menu_archivo = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
        
        # Guardar informe
        menu_archivo.add_command(
            label="💾 Guardar Informe...",
            command=self._guardar_informe,
            accelerator=f"{MOD_KEY_DISPLAY}+S"
        )
        self._vincular_atajo("s", self._guardar_informe)
        
        menu_archivo.add_separator()
        
        # Submenú Exportar
        menu_exportar = tk.Menu(menu_archivo, tearoff=0)
        menu_archivo.add_cascade(label="📤 Exportar", menu=menu_exportar)
        
        menu_exportar.add_command(
            label="📄 Exportar a PDF...",
            command=self._exportar_pdf,
            accelerator=f"{MOD_KEY_DISPLAY}+P"
        )
        self._vincular_atajo("p", self._exportar_pdf)
        
        menu_exportar.add_command(
            label="🌐 Exportar a HTML...",
            command=self._exportar_html,
            accelerator=f"{MOD_KEY_DISPLAY}+H"
        )
        self._vincular_atajo("h", self._exportar_html)
        
        menu_archivo.add_separator()
        
        # Historial
        menu_archivo.add_command(
            label="📚 Historial de escaneos...",
            command=self._abrir_historial,
            accelerator=f"{MOD_KEY_DISPLAY}+L"
        )
        self._vincular_atajo("l", self._abrir_historial)
        
        menu_archivo.add_separator()
        
        menu_archivo.add_command(
            label="Salir",
            command=self.al_salir,
            accelerator=f"{MOD_KEY_DISPLAY}+Q"
        )
        
        # Vincular atajo de teclado multiplataforma
        self._vincular_atajo("q", self.al_salir)
    
    def _guardar_informe(self):
        """Guarda el informe en texto"""
        if self.al_guardar:
            self.al_guardar()
    
    def _exportar_pdf(self):
        """Exporta el informe a PDF"""
        if self.al_exportar_pdf:
            self.al_exportar_pdf()
    
    def _exportar_html(self):
        """Exporta el informe a HTML"""
        if self.al_exportar_html:
            self.al_exportar_html()
    
    def _abrir_historial(self):
        """Abre el diálogo de historial"""
        if self.al_historial:
            self.al_historial()
    
    def _crear_menu_herramientas(self):
        """Crea el menú Herramientas"""
        menu_herramientas = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Herramientas", menu=menu_herramientas)
        
        menu_herramientas.add_command(
            label="🌐 Escaneo Múltiple...",
            command=self._abrir_escaneo_multiple,
            accelerator=f"{MOD_KEY_DISPLAY}+M"
        )
        
        # Vincular atajo de teclado multiplataforma
        self._vincular_atajo("m", self._abrir_escaneo_multiple)
    
    def _abrir_escaneo_multiple(self):
        """Abre el diálogo de escaneo múltiple"""
        if self.al_escaneo_multiple:
            self.al_escaneo_multiple()
    
    def _crear_menu_preferencias(self):
        """Crea el menú Preferencias"""
        menu_preferencias = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Preferencias", menu=menu_preferencias)
        
        menu_preferencias.add_command(
            label="⚙️ Opciones de escaneo...",
            command=self._abrir_opciones,
            accelerator=f"{MOD_KEY_DISPLAY}+O"
        )
        
        menu_preferencias.add_separator()
        

        # ═══════════════════════════════════════════════════════════
        # SUBMENÚ DE APARIENCIA / TEMA
        # ═══════════════════════════════════════════════════════════
        
        menu_apariencia = tk.Menu(menu_preferencias, tearoff=0)
        menu_preferencias.add_cascade(label="🎨 Apariencia", menu=menu_apariencia)
        
        # Variable para radio buttons del tema
        self.var_tema = tk.StringVar(value=self.gestor_temas.obtener_modo_apariencia())
        
        menu_apariencia.add_radiobutton(
            label="🌙 Modo Oscuro",
            variable=self.var_tema,
            value="dark",
            command=lambda: self._cambiar_tema("dark")
        )
        
        menu_apariencia.add_radiobutton(
            label="☀️ Modo Claro",
            variable=self.var_tema,
            value="light",
            command=lambda: self._cambiar_tema("light")
        )
        
        menu_apariencia.add_radiobutton(
            label="💻 Seguir Sistema",
            variable=self.var_tema,
            value="system",
            command=lambda: self._cambiar_tema("system")
        )
        
        menu_apariencia.add_separator()
        
        menu_apariencia.add_command(
            label="🔄 Alternar Claro/Oscuro",
            command=self._alternar_tema,
            accelerator=f"{MOD_KEY_DISPLAY}+T"
        )
        
        # Vincular atajo de teclado para alternar tema
        self._vincular_atajo("t", self._alternar_tema)
        
        menu_preferencias.add_separator()
        
        # ═══════════════════════════════════════════════════════════
        # SUBMENÚ DE NOTIFICACIONES
        # ═══════════════════════════════════════════════════════════
        menu_notificaciones = tk.Menu(menu_preferencias, tearoff=0)
        menu_preferencias.add_cascade(label="🔔 Notificaciones", menu=menu_notificaciones)
        
        menu_notificaciones.add_checkbutton(
            label="Activar notificaciones de escritorio",
            variable=self.var_notificaciones,
            command=self._toggle_notificaciones
        )
        
        menu_notificaciones.add_checkbutton(
            label="Reproducir sonido",
            variable=self.var_sonido,
            command=self._toggle_sonido
        )
        
        # Vincular atajo de teclado
        self._vincular_atajo("o", self._abrir_opciones)
    
    def _cambiar_tema(self, modo: str):
        """Cambia el tema de la aplicación"""
        self.gestor_temas.cambiar_modo_apariencia(modo)
        self.var_tema.set(modo)
    
    def _alternar_tema(self):
        """Alternancia entre el modo claro y el oscuro"""
        self.gestor_temas.alternar_modo()
        self.var_tema.set(self.gestor_temas.obtener_modo_apariencia())
    
    def _toggle_notificaciones(self):
        """Activa/desactiva las notificaciones"""
        self.notificador.establecer_habilitadas(self.var_notificaciones.get())
    
    def _toggle_sonido(self):
        """Activa/desactiva el sonido de notificaciones"""
        self.notificador.establecer_sonido(self.var_sonido.get())
    
    def _abrir_opciones(self):
        """Abre el diálogo de opciones"""
        if self.al_opciones:
            self.al_opciones()
    
    def _mostrar_atajos(self):
        """Muestra el diálogo de atajos de teclado"""
        DialogoAtajos(self.parent)
    
    def _crear_menu_ayuda(self):
        """Crea el menú Ayuda"""
        menu_ayuda = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)
        
        menu_ayuda.add_command(
            label="⌨️ Atajos de teclado...",
            command=self._mostrar_atajos,
            accelerator=f"{MOD_KEY_DISPLAY}+K"
        )
        
        menu_ayuda.add_separator()
        
        menu_ayuda.add_command(
            label="ℹ️ Acerca de...",
            command=self.al_acerca_de,
            accelerator="F1"
        )
        

        # Vincular atajos de teclado
        self._vincular_atajo("k", self._mostrar_atajos)
        self.parent.bind("<F1>", lambda e: self.al_acerca_de())
