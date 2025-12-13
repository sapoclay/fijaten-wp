"""
Fijaten-WP - Configuración y Constantes
"""

import os
from pathlib import Path

# Información de la aplicación
APP_NAME = "Fijaten-WP"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = """Fijaten-WP es un analizador de seguridad para sitios WordPress.

Esta herramienta analiza las vulnerabilidades más comunes y críticas 
de cualquier sitio WordPress de forma no intrusiva, examinando 
únicamente información públicamente accesible.

Características principales:
• Detección de versión de WordPress expuesta
• Verificación de certificado SSL/HTTPS
• Análisis de XML-RPC (riesgo de ataques de fuerza bruta)
• Detección de enumeración de usuarios
• Búsqueda de archivos de configuración expuestos
• Verificación de modo debug activo
• Análisis de listado de directorios
• Detección de plugins y temas vulnerables
• Verificación de cabeceras de seguridad HTTP

Los informes generados son comprensibles tanto para usuarios 
técnicos como para aquellos sin conocimientos especializados."""

APP_AUTHOR = "Entreunosyceros"
APP_GITHUB = "https://github.com/sapoclay/fijaten-wp"
APP_LICENSE = "MIT"

# Rutas
BASE_DIR = Path(__file__).parent.absolute()  # Directorio raíz del proyecto
IMG_DIR = BASE_DIR / "img"
LOGO_PATH = IMG_DIR / "logo.png"

# Configuración de la ventana principal
WINDOW_TITLE = f"🔒 {APP_NAME} - Analizador de Seguridad WordPress"
WINDOW_SIZE = "1100x750"
WINDOW_MIN_SIZE = (900, 600)

# Configuración del tema
THEME_MODE = "dark"
THEME_COLOR = "blue"

# Configuración de fuentes
FONT_FAMILY_MONO = "Consolas"
FONT_SIZE_TITLE = 28
FONT_SIZE_SUBTITLE = 14
FONT_SIZE_NORMAL = 14
FONT_SIZE_SMALL = 12
FONT_SIZE_TEXTBOX = 13

# Colores personalizados
COLORS = {
    "success": "#28a745",
    "warning": "#ffc107",
    "danger": "#dc3545",
    "info": "#17a2b8",
    "primary": "#007bff",
    "secondary": "#6c757d",
    "dark": "#343a40",
    "light": "#f8f9fa"
}

# Mensajes
MESSAGES = {
    "welcome": """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                       🔒 FIJATEN-WP 🔒                                       ║
║                 Analizador de Seguridad WordPress                            ║
║                                                                              ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║   Bienvenido al analizador de seguridad de WordPress.                        ║
║                                                                              ║
║   Este programa analiza las vulnerabilidades más comunes en sitios           ║
║   WordPress y genera un informe claro y comprensible.                        ║
║                                                                              ║
║   📝 INSTRUCCIONES:                                                          ║
║                                                                              ║
║   1. Escribe el dominio del sitio WordPress en la barra superior             ║
║      Ejemplo: misitioweb.com o https://misitioweb.com                        ║
║                                                                              ║
║   2. Haz clic en "Analizar" o presiona Enter                                 ║
║                                                                              ║
║   3. Espera mientras se realiza el análisis (puede tardar unos segundos)     ║
║                                                                              ║
║   4. Revisa los resultados en las diferentes pestañas:                       ║
║      • Resumen: Vista general para todos los públicos                        ║
║      • Detalles: Explicación simple de cada problema                         ║
║      • Técnico: Información técnica detallada                                ║
║      • Plan de Acción: Pasos a seguir ordenados por prioridad                ║
║                                                                              ║
║   🔍 VULNERABILIDADES QUE ANALIZA:                                           ║
║                                                                              ║
║   • Versión de WordPress expuesta o desactualizada                           ║
║   • Configuración SSL/HTTPS                                                  ║
║   • XML-RPC habilitado (puede usarse para ataques)                           ║
║   • Enumeración de usuarios                                                  ║
║   • Archivos de configuración expuestos                                      ║
║   • Modo debug activo                                                        ║
║   • Listado de directorios                                                   ║
║   • Plugins y temas vulnerables                                              ║
║   • Cabeceras de seguridad HTTP                                              ║
║   • Y más...                                                                 ║
║                                                                              ║
║   ⚠️  NOTA: Este análisis es informativo y no intrusivo.                     ║
║       Solo analiza información pública del sitio.                            ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
""",
    "ready": "Listo para analizar",
    "analyzing": "Analizando...",
    "cleaned": "Resultados limpiados. Introduce un nuevo dominio para analizar.",
    "no_domain": "Por favor, introduce un dominio para analizar.",
    "scan_in_progress": "Ya hay un análisis en curso. Espera a que termine.",
    "no_report": "No hay informe para guardar."
}
