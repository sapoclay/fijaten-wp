"""
Fijaten-WP - Barra de Menú
Menú superior de la aplicación
"""

import customtkinter as ctk
import tkinter as tk
from typing import Callable, Optional

from gui.gestor_temas import obtener_gestor_temas, TEMAS_APARIENCIA
from gui.notificaciones import obtener_notificador


class BarraMenu:
    """Barra de menú para la aplicación"""
    
    def __init__(self, parent: ctk.CTk, on_exit: Callable, on_about: Callable, 
                 on_options: Optional[Callable] = None,
                 on_escaneo_multiple: Optional[Callable] = None):
        self.parent = parent
        self.al_salir = on_exit
        self.al_acerca_de = on_about
        self.al_opciones = on_options
        self.al_escaneo_multiple = on_escaneo_multiple
        
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
    
    def _crear_menu_archivo(self):
        """Crea el menú Archivo"""
        menu_archivo = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Archivo", menu=menu_archivo)
        
        menu_archivo.add_command(
            label="Salir",
            command=self.al_salir,
            accelerator="Ctrl+Q"
        )
        
        # Vincular atajo de teclado
        self.parent.bind("<Control-q>", lambda e: self.al_salir())
        self.parent.bind("<Control-Q>", lambda e: self.al_salir())
    
    def _crear_menu_herramientas(self):
        """Crea el menú Herramientas"""
        menu_herramientas = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Herramientas", menu=menu_herramientas)
        
        menu_herramientas.add_command(
            label="🌐 Escaneo Múltiple...",
            command=self._abrir_escaneo_multiple,
            accelerator="Ctrl+M"
        )
        
        # Vincular atajo de teclado
        self.parent.bind("<Control-m>", lambda e: self._abrir_escaneo_multiple())
        self.parent.bind("<Control-M>", lambda e: self._abrir_escaneo_multiple())
    
    def _abrir_escaneo_multiple(self):
        """Abre el diálogo de escaneo múltiple"""
        if self.al_escaneo_multiple:
            self.al_escaneo_multiple()
    
    def _crear_menu_preferencias(self):
        """Crea el menú Preferencias"""
        menu_preferencias = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Preferencias", menu=menu_preferencias)
        
        menu_preferencias.add_command(
            label="⚙️ Opciones de Escaneo...",
            command=self._abrir_opciones,
            accelerator="Ctrl+O"
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
            accelerator="Ctrl+T"
        )
        
        # Vincular atajo de teclado para alternar tema
        self.parent.bind("<Control-t>", lambda e: self._alternar_tema())
        self.parent.bind("<Control-T>", lambda e: self._alternar_tema())
        
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
        self.parent.bind("<Control-o>", lambda e: self._abrir_opciones())
        self.parent.bind("<Control-O>", lambda e: self._abrir_opciones())
    
    def _cambiar_tema(self, modo: str):
        """Cambia el tema de la aplicación"""
        self.gestor_temas.cambiar_modo_apariencia(modo)
        self.var_tema.set(modo)
    
    def _alternar_tema(self):
        """Alterna entre modo claro y oscuro"""
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
    
    def _crear_menu_ayuda(self):
        """Crea el menú Ayuda"""
        menu_ayuda = tk.Menu(self.barra_menu, tearoff=0)
        self.barra_menu.add_cascade(label="Ayuda", menu=menu_ayuda)
        
        menu_ayuda.add_command(
            label="Acerca de...",
            command=self.al_acerca_de,
            accelerator="F1"
        )
        
        # Vincular atajo de teclado
        self.parent.bind("<F1>", lambda e: self.al_acerca_de())
