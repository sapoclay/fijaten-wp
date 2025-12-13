"""
Fijaten-WP - Diálogo Acerca de
Ventana con información sobre la aplicación
"""

import customtkinter as ctk
import webbrowser
from PIL import Image
from pathlib import Path
import sys
import os

# Añadir directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from configuracion import (
    APP_NAME, APP_VERSION, APP_DESCRIPTION, 
    APP_GITHUB, APP_AUTHOR, LOGO_PATH
)


class DialogoAcerca(ctk.CTkToplevel):
    """Ventana de diálogo Acerca de"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configuración de la ventana
        self.title(f"Acerca de {APP_NAME}")
        self.geometry("550x720")
        self.resizable(False, False)
        
        # Hacer la ventana modal (sin grab_set para evitar bloqueos)
        self.transient(parent)
        
        # Centrar la ventana respecto al padre
        self.after(10, lambda: self.centrar_ventana(parent))
        
        # Crear contenido
        self.crear_contenido()
        
        # Foco en esta ventana
        self.focus_set()
        
        # Manejar cierre con Escape
        self.bind("<Escape>", lambda e: self.destroy())
        
        # Mantener la ventana al frente
        self.lift()
        self.attributes('-topmost', True)
        self.after(100, lambda: self.attributes('-topmost', False))
    
    def centrar_ventana(self, parent):
        """Centra la ventana respecto a la ventana padre"""
        # Dimensiones fijas
        ancho = 550
        alto = 720
        
        # Obtener posición del padre
        padre_x = parent.winfo_x()
        padre_y = parent.winfo_y()
        padre_ancho = parent.winfo_width()
        padre_alto = parent.winfo_height()
        
        # Calcular posición centrada
        x = padre_x + (padre_ancho - ancho) // 2
        y = padre_y + (padre_alto - alto) // 2
        
        # Asegurar que no se salga de la pantalla
        x = max(0, x)
        y = max(0, y)
        
        self.geometry(f"{ancho}x{alto}+{x}+{y}")
    
    def crear_contenido(self):
        """Crea el contenido de la ventana Acerca de"""
        
        # Frame principal con padding
        frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        frame_principal.pack(fill="both", expand=True, padx=30, pady=20)
        
        # ═══════════════════════════════════════════════════════════
        # LOGO
        # ═══════════════════════════════════════════════════════════
        logo_frame = ctk.CTkFrame(frame_principal, fg_color="transparent")
        logo_frame.pack(fill="x", pady=(0, 15))
        
        # Intentar cargar el logo
        try:
            if LOGO_PATH.exists():
                logo_image = Image.open(LOGO_PATH)
                # Redimensionar manteniendo proporción
                max_size = 120
                ratio = min(max_size / logo_image.width, max_size / logo_image.height)
                new_size = (int(logo_image.width * ratio), int(logo_image.height * ratio))
                logo_image = logo_image.resize(new_size, Image.Resampling.LANCZOS)
                
                logo_ctk = ctk.CTkImage(
                    light_image=logo_image,
                    dark_image=logo_image,
                    size=new_size
                )
                
                logo_label = ctk.CTkLabel(logo_frame, image=logo_ctk, text="")
                logo_label.pack()
            else:
                # Logo de texto si no existe la imagen
                self._crear_logo_texto(logo_frame)
        except Exception as e:
            # Logo de texto como fallback
            self._crear_logo_texto(logo_frame)
        
        # ═══════════════════════════════════════════════════════════
        # TÍTULO Y VERSIÓN
        # ═══════════════════════════════════════════════════════════
        title_label = ctk.CTkLabel(
            frame_principal,
            text=APP_NAME,
            font=ctk.CTkFont(size=28, weight="bold")
        )
        title_label.pack(pady=(10, 5))
        
        version_label = ctk.CTkLabel(
            frame_principal,
            text=f"Versión {APP_VERSION}",
            font=ctk.CTkFont(size=14),
            text_color="gray"
        )
        version_label.pack(pady=(0, 15))
        
        # ═══════════════════════════════════════════════════════════
        # DESCRIPCIÓN
        # ═══════════════════════════════════════════════════════════
        desc_frame = ctk.CTkFrame(frame_principal)
        desc_frame.pack(fill="both", expand=True, pady=10)
        
        desc_textbox = ctk.CTkTextbox(
            desc_frame,
            font=ctk.CTkFont(size=13),
            wrap="word",
            height=280
        )
        desc_textbox.pack(fill="both", expand=True, padx=10, pady=10)
        desc_textbox.insert("1.0", APP_DESCRIPTION)
        desc_textbox.configure(state="disabled")  # Solo lectura
        
        # ═══════════════════════════════════════════════════════════
        # AUTOR
        # ═══════════════════════════════════════════════════════════
        author_label = ctk.CTkLabel(
            frame_principal,
            text=f"Desarrollado por {APP_AUTHOR}",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        author_label.pack(pady=(10, 5))
        
        # ═══════════════════════════════════════════════════════════
        # BOTONES
        # ═══════════════════════════════════════════════════════════
        buttons_frame = ctk.CTkFrame(frame_principal, fg_color="transparent")
        buttons_frame.pack(fill="x", pady=(15, 0))
        
        # Botón GitHub
        github_btn = ctk.CTkButton(
            buttons_frame,
            text="🌐 Visitar GitHub",
            font=ctk.CTkFont(size=14, weight="bold"),
            height=40,
            width=200,
            command=self.abrir_github
        )
        github_btn.pack(side="left", expand=True, padx=5)
        
        # Botón Cerrar
        close_btn = ctk.CTkButton(
            buttons_frame,
            text="Cerrar",
            font=ctk.CTkFont(size=14),
            height=40,
            width=120,
            fg_color="gray",
            hover_color="darkgray",
            command=self.destroy
        )
        close_btn.pack(side="right", expand=True, padx=5)
    
    def _crear_logo_texto(self, parent):
        """Crea un logo de texto como fallback"""
        logo_text = ctk.CTkLabel(
            parent,
            text="🔒",
            font=ctk.CTkFont(size=80)
        )
        logo_text.pack()
    
    def abrir_github(self):
        """Abre el enlace de GitHub en el navegador"""
        webbrowser.open(APP_GITHUB)
