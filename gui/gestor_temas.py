"""
Fijaten-WP - Gestor de Temas
Manejo de modo claro/oscuro y persistencia del tema
"""

import customtkinter as ctk
import json
from pathlib import Path
from typing import Callable, List

# Archivo de configuración del tema
ARCHIVO_CONFIG_TEMA = Path(__file__).parent.parent / "tema_config.json"

# Temas disponibles
TEMAS_APARIENCIA = {
    "dark": "Oscuro",
    "light": "Claro",
    "system": "Sistema"
}

TEMAS_COLOR = {
    "blue": "Azul",
    "green": "Verde",
    "dark-blue": "Azul Oscuro"
}


class GestorTemas:
    """Gestiona los temas de la aplicación"""
    
    _instancia = None
    _callbacks: List[Callable] = []
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia
    
    def __init__(self):
        if self._inicializado:
            return
        self._inicializado = True
        self._callbacks = []
        self._cargar_configuracion()
    
    def _cargar_configuracion(self):
        """Carga la configuración del tema desde archivo"""
        self.modo_apariencia = "dark"
        self.tema_color = "blue"
        
        try:
            if ARCHIVO_CONFIG_TEMA.exists():
                with open(ARCHIVO_CONFIG_TEMA, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.modo_apariencia = config.get("modo_apariencia", "dark")
                    self.tema_color = config.get("tema_color", "blue")
        except Exception:
            pass
        
        # Aplicar tema al cargar
        self._aplicar_tema()
    
    def _guardar_configuracion(self):
        """Guarda la configuración del tema en archivo"""
        try:
            config = {
                "modo_apariencia": self.modo_apariencia,
                "tema_color": self.tema_color
            }
            with open(ARCHIVO_CONFIG_TEMA, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass
    
    def _aplicar_tema(self):
        """Aplica el tema actual a la aplicación"""
        ctk.set_appearance_mode(self.modo_apariencia)
        ctk.set_default_color_theme(self.tema_color)
    
    def cambiar_modo_apariencia(self, modo: str):
        """Cambia el modo de apariencia (dark/light/system)"""
        if modo in TEMAS_APARIENCIA:
            self.modo_apariencia = modo
            ctk.set_appearance_mode(modo)
            self._guardar_configuracion()
            self._notificar_callbacks()
    
    def cambiar_tema_color(self, tema: str):
        """Cambia el tema de color"""
        if tema in TEMAS_COLOR:
            self.tema_color = tema
            ctk.set_default_color_theme(tema)
            self._guardar_configuracion()
            self._notificar_callbacks()
    
    def obtener_modo_apariencia(self) -> str:
        """Obtiene el modo de apariencia actual"""
        return self.modo_apariencia
    
    def obtener_tema_color(self) -> str:
        """Obtiene el tema de color actual"""
        return self.tema_color
    
    def registrar_callback(self, callback: Callable):
        """Registra un callback para cuando cambie el tema"""
        if callback not in self._callbacks:
            self._callbacks.append(callback)
    
    def _notificar_callbacks(self):
        """Notifica a todos los callbacks registrados"""
        for callback in self._callbacks:
            try:
                callback()
            except Exception:
                pass
    
    def alternar_modo(self):
        """Alterna entre modo claro y oscuro"""
        if self.modo_apariencia == "dark":
            self.cambiar_modo_apariencia("light")
        else:
            self.cambiar_modo_apariencia("dark")


# Instancia global del gestor de temas
gestor_temas = GestorTemas()


def obtener_gestor_temas() -> GestorTemas:
    """Obtiene la instancia del gestor de temas"""
    return gestor_temas
