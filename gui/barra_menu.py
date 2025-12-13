"""
Fijaten-WP - Barra de Menú
Menú superior de la aplicación
"""

import customtkinter as ctk
import tkinter as tk
from typing import Callable


class BarraMenu:
    """Barra de menú para la aplicación"""
    
    def __init__(self, parent: ctk.CTk, on_exit: Callable, on_about: Callable):
        self.parent = parent
        self.al_salir = on_exit
        self.al_acerca_de = on_about
        
        # Crear barra de menú usando tkinter nativo
        self.barra_menu = tk.Menu(parent)
        parent.configure(menu=self.barra_menu)
        
        # Crear menús
        self._crear_menu_archivo()
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
