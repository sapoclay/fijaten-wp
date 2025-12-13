#!/usr/bin/env python3
"""
Fijaten-WP - Analizador de Seguridad WordPress
Punto de entrada principal de la aplicación
"""

import sys
import os

# Añadir el directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import VentanaPrincipal


def principal():
    """Función principal"""
    app = VentanaPrincipal()
    app.mainloop()


if __name__ == "__main__":
    principal()
