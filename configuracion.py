"""
Fijaten-WP - Configuración y Constantes
"""

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
• Detección de tecnologías web (CMS, frameworks, lenguajes)

Funcionalidades adicionales:
• Exportación de informes a PDF y HTML
• Historial de escaneos con filtrado y comparación
• Escaneo múltiple de dominios
• Enlaces clicables en los informes
• Menú contextual en campo de URL (clic derecho)
• Atajos de teclado personalizados
• Modo claro/oscuro

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
# Fuentes monoespaciadas en orden de preferencia (la primera disponible se usa)
FONT_FAMILY_MONO = "monospace"  # En Linux usa la fuente monoespaciada del sistema
FONT_FAMILY_MONO_FALLBACKS = ["DejaVu Sans Mono", "Liberation Mono", "Consolas", "Courier New", "monospace"]
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
+------------------------------------------------------------------------------+
|                          FIJATEN-WP                                          |
|                  Analizador de Seguridad WordPress                           |
+------------------------------------------------------------------------------+

  Bienvenido al analizador de seguridad de WordPress.

  Este programa analiza las vulnerabilidades mas comunes en sitios
  WordPress y genera un informe claro y comprensible.

  INSTRUCCIONES:

  1. Escribe el dominio del sitio WordPress en la barra superior
     Ejemplo: misitioweb.com o https://misitioweb.com

  2. Haz clic en "Analizar" o presiona Enter

  3. Espera mientras se realiza el analisis (puede tardar unos segundos)

  4. Revisa los resultados en las diferentes pestanas:
     - Resumen: Vista general para todos los publicos
     - Detalles: Explicacion simple de cada problema
     - Tecnico: Informacion tecnica detallada
     - Plan de Accion: Pasos a seguir ordenados por prioridad

  VULNERABILIDADES QUE ANALIZA:

  - Version de WordPress expuesta o desactualizada
  - Configuracion SSL/HTTPS
  - XML-RPC habilitado (puede usarse para ataques)
  - Enumeracion de usuarios
  - Archivos de configuracion expuestos
  - Modo debug activo
  - Listado de directorios
  - Plugins y temas vulnerables
  - Cabeceras de seguridad HTTP
  - Y mas...

  NOTA: Este analisis es informativo y no intrusivo.
        Solo analiza informacion publica del sitio.

+------------------------------------------------------------------------------+
""",
    "ready": "Listo para analizar",
    "analyzing": "Analizando...",
    "cleaned": "Resultados limpiados. Introduce un nuevo dominio para analizar.",
    "no_domain": "Por favor, introduce un dominio para analizar.",
    "scan_in_progress": "Ya hay un análisis en curso. Espera a que termine.",
    "no_report": "No hay informe para guardar."
}
