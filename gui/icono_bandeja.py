"""
Fijaten-WP - Icono de Bandeja del Sistema
Gestiona el icono en la bandeja del sistema (system tray)
"""

from __future__ import annotations
import threading
from pathlib import Path
from PIL import Image
import sys
from typing import Any, Optional

# Añadir directorio al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar pystray para motrar el icono
pystray: Any = None
item: Any = None
PYSTRAY_DISPONIBLE = False

try:
    import pystray as _pystray
    from pystray import MenuItem as _item
    pystray = _pystray
    item = _item
    PYSTRAY_DISPONIBLE = True
except ImportError:
    print("⚠️ pystray no está instalado. El icono de bandeja no estará disponible.")

from configuracion import APP_NAME, LOGO_PATH


class IconoBandeja:
    
    """Gestiona el icono en la bandeja del sistema"""
    
    def __init__(self, ventana_principal):
        """
        Inicializa el icono de la bandeja
        
        Args:
            ventana_principal: Referencia a la ventana principal de la aplicación
        """
        self.ventana = ventana_principal
        self.icono: Any = None
        self.icono_thread: Optional[threading.Thread] = None
        self._activo = False
        
        if not PYSTRAY_DISPONIBLE:
            return
    
    def iniciar(self):
        """Inicia el icono en la bandeja del sistema"""
        if not PYSTRAY_DISPONIBLE:
            return
        
        try:
            # Cargar imagen del logo
            imagen = self._cargar_imagen()
            
            # Crear menú
            menu = pystray.Menu(
                item('🔍 Mostrar aplicación', self._mostrar_ventana, default=True),
                item('─────────────', None, enabled=False),
                item('❌ Cerrar aplicación', self._cerrar_aplicacion)
            )
            
            # Crear icono
            self.icono = pystray.Icon(
                name=APP_NAME,
                icon=imagen,
                title=APP_NAME,
                menu=menu
            )
            
            # Ejecutar en hilo separado para no bloquear la GUI
            self._activo = True
            self.icono_thread = threading.Thread(target=self._ejecutar_icono, daemon=True)
            self.icono_thread.start()
            
        except Exception as e:
            print(f"⚠️ Error al crear icono de bandeja: {e}")
    
    def _cargar_imagen(self) -> Image.Image:
        """Carga la imagen del logo para el icono"""
        try:
            if LOGO_PATH.exists():
                imagen = Image.open(LOGO_PATH)
                # Redimensionar a tamaño adecuado para bandeja (típicamente 64x64 o menor)
                imagen = imagen.resize((64, 64), Image.Resampling.LANCZOS)
                return imagen
        except Exception as e:
            print(f"⚠️ Error al cargar logo: {e}")
        
        # Crear imagen por defecto si no se puede cargar el logo
        return self._crear_imagen_defecto()
    
    def _crear_imagen_defecto(self) -> Image.Image:
        """Crea una imagen por defecto para el icono"""
        # Crear una imagen simple de 64x64
        imagen = Image.new('RGBA', (64, 64), (41, 128, 185, 255))  # Azul
        return imagen
    
    def _ejecutar_icono(self):
        """Ejecuta el bucle del icono (en hilo separado)"""
        try:
            if self.icono is not None:
                self.icono.run()
        except Exception as e:
            print(f"⚠️ Error en icono de bandeja: {e}")
    
    def _mostrar_ventana(self, icon=None, item=None):
        """Muestra la ventana principal"""
        try:
            # Usar after para ejecutar en el hilo principal de tkinter
            self.ventana.after(0, self._restaurar_ventana)
        except Exception as e:
            print(f"Error al mostrar ventana: {e}")
    
    def _restaurar_ventana(self):
        """Restaura la ventana principal en el hilo de tkinter"""
        try:
            self.ventana.deiconify()  # Mostrar si está minimizada
            self.ventana.lift()  # Traer al frente
            self.ventana.focus_force()  # Dar foco
            self.ventana.state('normal')  # Asegurar estado normal
        except Exception as e:
            print(f"Error al restaurar ventana: {e}")
    
    def _cerrar_aplicacion(self, icon=None, item=None):
        """Cierra la aplicación completamente"""
        try:
            self.detener()
            # Usar after para ejecutar en el hilo principal de tkinter
            self.ventana.after(0, self.ventana.salir)
        except Exception as e:
            print(f"Error al cerrar aplicación: {e}")
    
    def detener(self):
        """Detiene el icono de la bandeja"""
        if self.icono and self._activo:
            try:
                self._activo = False
                self.icono.stop()
            except Exception:
                pass
    
    def actualizar_tooltip(self, texto: str):
        """Actualiza el texto del tooltip del icono"""
        if self.icono:
            try:
                self.icono.title = texto
            except Exception:
                pass


def crear_icono_bandeja(ventana_principal) -> IconoBandeja:
    """
    Crea e inicia el icono de la bandeja del sistema
    
    Args:
        ventana_principal: Referencia a la ventana principal
        
    Devuelve:
        Instancia de IconoBandeja
    """
    icono = IconoBandeja(ventana_principal)
    icono.iniciar()
    return icono
