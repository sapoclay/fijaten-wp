#!/usr/bin/env python3
"""
Fijaten-WP - Launcher
Script de arranque optimizado para el analizador de seguridad WordPress.

Características:
- Verificación y creación automática de entorno virtual
- Instalación inteligente de dependencias (solo si cambian)
- Verificación de requisitos del sistema
- Manejo robusto de errores y señales
- Splash screen informativo
"""

import os
import sys
import platform
import subprocess
import shutil
import hashlib
import signal
from pathlib import Path
from typing import Optional

# Constantes
APP_NAME = "Fijaten-WP"
APP_VERSION = "1.0.0"
VENV_DIR = "venv"
REQUIREMENTS_FILE = "requirements.txt"
MAIN_FILE = "main.py"
MIN_PYTHON_VERSION = (3, 8)


class Colors:
    """Colores ANSI para terminal"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    @classmethod
    def disable(cls):
        """Deshabilita colores para Windows sin soporte"""
        cls.HEADER = cls.BLUE = cls.CYAN = cls.GREEN = ''
        cls.YELLOW = cls.RED = cls.BOLD = cls.RESET = ''


def setup_colors():
    """Configura colores según el sistema operativo"""
    if platform.system().lower() == 'windows':
        try:
            import ctypes
            # windll solo existe en Windows, usamos getattr para evitar error de linter
            windll = getattr(ctypes, 'windll', None)
            if windll is not None:
                kernel32 = windll.kernel32
                kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        except Exception:
            Colors.disable()


def print_banner():
    """Muestra el banner de inicio de la aplicación"""
    banner = f"""
{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║   🔒  {APP_NAME} - Analizador de Seguridad WordPress  🔒        ║
║                                                                  ║
║   Versión: {APP_VERSION}                                              ║
║   https://github.com/sapoclay/fijaten-wp                         ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
{Colors.RESET}"""
    print(banner)


def print_status(message: str, status: str = "info"):
    """Imprime un mensaje con formato de estado"""
    icons = {
        "info": f"{Colors.BLUE}ℹ️ ",
        "success": f"{Colors.GREEN}✅",
        "warning": f"{Colors.YELLOW}⚠️ ",
        "error": f"{Colors.RED}❌",
        "working": f"{Colors.CYAN}⏳"
    }
    icon = icons.get(status, icons["info"])
    print(f"{icon} {message}{Colors.RESET}")


def print_exit_message():
    """Muestra mensaje de despedida"""
    print(f"\n{Colors.CYAN}{'─' * 50}")
    print(f"  👋 ¡Hasta pronto!")
    print(f"  🔒 Gracias por usar {APP_NAME}")
    print(f"{'─' * 50}{Colors.RESET}\n")


def check_python_version() -> bool:
    """Verifica que la versión de Python sea compatible"""
    current = sys.version_info[:2]
    if current < MIN_PYTHON_VERSION:
        print_status(
            f"Se requiere Python {MIN_PYTHON_VERSION[0]}.{MIN_PYTHON_VERSION[1]}+ "
            f"(actual: {current[0]}.{current[1]})",
            "error"
        )
        return False
    return True


def check_tkinter_available() -> bool:
    """Verifica que tkinter esté disponible"""
    try:
        import tkinter
        return True
    except ImportError:
        print_status("tkinter no está instalado.", "error")
        print(f"\n{Colors.YELLOW}Para instalarlo:{Colors.RESET}")
        if platform.system().lower() == 'linux':
            print("  Ubuntu/Debian: sudo apt-get install python3-tk")
            print("  Fedora: sudo dnf install python3-tkinter")
            print("  Arch: sudo pacman -S tk")
        elif platform.system().lower() == 'darwin':
            print("  macOS: brew install python-tk")
        else:
            print("  Windows: Reinstalar Python marcando 'tcl/tk and IDLE'")
        return False


def get_executable_path(name: str) -> Path:
    """Obtiene la ruta del ejecutable dentro del entorno virtual"""
    if platform.system().lower() == 'windows':
        return Path(VENV_DIR) / 'Scripts' / f'{name}.exe'
    return Path(VENV_DIR) / 'bin' / name


def is_venv_valid() -> bool:
    """Verifica si el entorno virtual existe y es válido"""
    venv_path = Path(VENV_DIR)
    python_exe = get_executable_path('python')
    pip_exe = get_executable_path('pip')
    
    if not venv_path.exists():
        return False
    
    if not python_exe.exists() or not pip_exe.exists():
        return False
    
    try:
        result = subprocess.run(
            [str(python_exe), '--version'],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception:
        return False


def create_venv() -> bool:
    """Crea el entorno virtual"""
    print_status("Creando entorno virtual...", "working")
    
    venv_path = Path(VENV_DIR)
    
    if venv_path.exists():
        print_status("Eliminando entorno virtual corrupto...", "warning")
        shutil.rmtree(venv_path, ignore_errors=True)
    
    try:
        import venv as venv_module
        venv_module.create(VENV_DIR, with_pip=True, clear=True)
        
        pip_exe = get_executable_path('pip')
        subprocess.run(
            [str(pip_exe), 'install', '--upgrade', 'pip', 'setuptools', 'wheel'],
            capture_output=True,
            check=True
        )
        
        print_status("Entorno virtual creado correctamente", "success")
        return True
        
    except Exception as e:
        print_status(f"Error al crear entorno virtual: {e}", "error")
        return False


def get_requirements_hash() -> str:
    """Calcula el hash SHA256 del archivo requirements.txt"""
    req_path = Path(REQUIREMENTS_FILE)
    if not req_path.exists():
        return ""
    return hashlib.sha256(req_path.read_bytes()).hexdigest()


def are_dependencies_installed() -> bool:
    """Verifica si las dependencias están instaladas y actualizadas"""
    stamp_path = Path(VENV_DIR) / '.requirements.sha256'
    
    if not stamp_path.exists():
        return False
    
    current_hash = get_requirements_hash()
    stored_hash = stamp_path.read_text(encoding='utf-8').strip()
    
    return current_hash == stored_hash


def install_dependencies() -> bool:
    """Instala las dependencias desde requirements.txt"""
    req_path = Path(REQUIREMENTS_FILE)
    
    if not req_path.exists():
        print_status(f"Archivo {REQUIREMENTS_FILE} no encontrado", "error")
        return False
    
    if are_dependencies_installed():
        print_status("Dependencias ya instaladas (sin cambios)", "success")
        return True
    
    print_status("Instalando dependencias...", "working")
    
    pip_exe = get_executable_path('pip')
    
    try:
        subprocess.run(
            [str(pip_exe), 'install', '-r', REQUIREMENTS_FILE, '--progress-bar', 'on'],
            capture_output=False,
            check=True
        )
        
        stamp_path = Path(VENV_DIR) / '.requirements.sha256'
        stamp_path.write_text(get_requirements_hash(), encoding='utf-8')
        
        print_status("Dependencias instaladas correctamente", "success")
        return True
        
    except subprocess.CalledProcessError:
        print_status("Error al instalar dependencias", "error")
        return False


def verify_main_file() -> bool:
    """Verifica que el archivo principal exista"""
    if not Path(MAIN_FILE).exists():
        print_status(f"Archivo {MAIN_FILE} no encontrado", "error")
        return False
    return True


def run_application() -> int:
    """Ejecuta la aplicación principal"""
    print_status("Iniciando aplicación...", "working")
    print(f"\n{Colors.GREEN}{'═' * 50}{Colors.RESET}")
    print(f"{Colors.BOLD}  🚀 Abriendo interfaz gráfica...{Colors.RESET}")
    print(f"{Colors.GREEN}{'═' * 50}{Colors.RESET}\n")
    
    python_exe = get_executable_path('python')
    
    try:
        process = subprocess.run(
            [str(python_exe), MAIN_FILE],
            check=False
        )
        return process.returncode
        
    except KeyboardInterrupt:
        return 0


def setup_signal_handlers():
    """Configura manejadores de señales para cierre limpio"""
    def signal_handler(signum, frame):
        print_exit_message()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    if hasattr(signal, 'SIGTERM'):
        signal.signal(signal.SIGTERM, signal_handler)


def main() -> int:
    """Función principal del launcher"""
    script_dir = Path(__file__).parent.absolute()
    os.chdir(script_dir)
    
    setup_colors()
    setup_signal_handlers()
    
    print_banner()
    
    print(f"{Colors.BOLD}📋 Verificando requisitos del sistema...{Colors.RESET}\n")
    
    if not check_python_version():
        return 1
    print_status(f"Python {sys.version_info[0]}.{sys.version_info[1]} detectado", "success")
    
    if not check_tkinter_available():
        return 1
    print_status("tkinter disponible", "success")
    
    if not verify_main_file():
        return 1
    print_status("Archivos de la aplicación encontrados", "success")
    
    print()
    
    print(f"{Colors.BOLD}🔧 Preparando entorno...{Colors.RESET}\n")
    
    if not is_venv_valid():
        if not create_venv():
            return 1
    else:
        print_status("Entorno virtual verificado", "success")
    
    if not install_dependencies():
        return 1
    
    print()
    
    try:
        exit_code = run_application()
        
        if exit_code == 0:
            print_exit_message()
        
        return exit_code
        
    except KeyboardInterrupt:
        print_exit_message()
        return 0
    except Exception as e:
        print_status(f"Error inesperado: {e}", "error")
        return 1


if __name__ == '__main__':
    sys.exit(main())