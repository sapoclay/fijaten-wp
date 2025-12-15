"""
Fijaten-WP - Navegador para sitios con Challenge
Usa Selenium con undetected-chromedriver para pasar verificaciones JavaScript
"""

import time
import subprocess
import sys
from typing import Optional, Dict, Tuple, Any, TYPE_CHECKING
from urllib.parse import urlparse

if TYPE_CHECKING:
    from selenium.webdriver.chrome.webdriver import WebDriver


class NavegadorChallenge:
    """Navegador automatizado para pasar challenges JavaScript"""
    
    DEPENDENCIAS = ['selenium', 'undetected-chromedriver']
    
    def __init__(self, timeout: int = 30):
        self.timeout = timeout
        self.driver: Optional[Any] = None  # WebDriver cuando está inicializado
        self._disponible: Optional[bool] = None
        self._error_instalacion: Optional[str] = None
    
    @classmethod
    def verificar_dependencias(cls) -> Tuple[bool, str]:
        """Verifica si las dependencias están instaladas"""
        faltantes = []
        
        try:
            import selenium
        except ImportError:
            faltantes.append('selenium')
        
        try:
            import undetected_chromedriver
        except ImportError:
            faltantes.append('undetected-chromedriver')
        
        if faltantes:
            return False, f"Faltan dependencias: {', '.join(faltantes)}"
        
        return True, ""
    
    @classmethod
    def instalar_dependencias(cls, callback=None) -> Tuple[bool, str]:
        """Instala las dependencias necesarias"""
        try:
            import subprocess
            import sys
            
            for dep in cls.DEPENDENCIAS:
                if callback:
                    callback(f"Instalando {dep}...")
                
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', dep],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode != 0:
                    return False, f"Error instalando {dep}: {result.stderr}"
            
            return True, "Dependencias instaladas correctamente"
            
        except Exception as e:
            return False, f"Error durante la instalación: {str(e)}"
    
    @classmethod
    def verificar_chrome_instalado(cls) -> Tuple[bool, str]:
        """Verifica si Chrome/Chromium está instalado"""
        import shutil
        
        # Buscar Chrome en ubicaciones comunes
        rutas_chrome = [
            'google-chrome',
            'google-chrome-stable',
            'chromium',
            'chromium-browser',
            '/usr/bin/google-chrome',
            '/usr/bin/chromium',
            '/usr/bin/chromium-browser',
            '/opt/google/chrome/chrome',
        ]
        
        for ruta in rutas_chrome:
            if shutil.which(ruta):
                return True, ruta
        
        # En Windows
        import platform
        if platform.system() == 'Windows':
            rutas_windows = [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            ]
            import os
            for ruta in rutas_windows:
                if os.path.exists(ruta):
                    return True, ruta
        
        return False, "Chrome/Chromium no encontrado. Por favor, instálalo primero."
    
    def esta_disponible(self) -> Tuple[bool, str]:
        """Verifica si el navegador está disponible para usar"""
        if self._disponible is not None:
            return self._disponible, self._error_instalacion or ""
        
        # Verificar Chrome
        chrome_ok, chrome_msg = self.verificar_chrome_instalado()
        if not chrome_ok:
            self._disponible = False
            self._error_instalacion = chrome_msg
            return False, chrome_msg
        
        # Verificar dependencias Python
        deps_ok, deps_msg = self.verificar_dependencias()
        if not deps_ok:
            self._disponible = False
            self._error_instalacion = deps_msg
            return False, deps_msg
        
        self._disponible = True
        return True, ""
    
    def iniciar(self) -> bool:
        """Inicia el navegador en modo headless"""
        disponible, error = self.esta_disponible()
        if not disponible:
            raise RuntimeError(f"Navegador no disponible: {error}")
        
        try:
            import undetected_chromedriver as uc
            
            options = uc.ChromeOptions()
            options.add_argument('--headless=new')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('--window-size=1920,1080')
            options.add_argument('--disable-blink-features=AutomationControlled')
            
            # Detectar versión de Chrome automáticamente
            try:
                import subprocess
                result = subprocess.run(['google-chrome', '--version'], capture_output=True, text=True)
                if result.returncode == 0:
                    version_str = result.stdout.strip()
                    # Ejemplo: "Google Chrome 142.0.7444.175"
                    import re
                    match = re.search(r'(\d+)\.', version_str)
                    if match:
                        chrome_version = int(match.group(1))
                    else:
                        chrome_version = None
                else:
                    chrome_version = None
            except Exception:
                chrome_version = None
            
            self.driver = uc.Chrome(options=options, version_main=chrome_version)
            self.driver.set_page_load_timeout(self.timeout)
            
            return True
            
        except Exception as e:
            self._error_instalacion = str(e)
            return False
    
    def cerrar(self):
        """Cierra el navegador"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
    
    def _detectar_tipo_challenge(self, html: str, titulo: str) -> str:
        """Detecta el tipo de challenge para dar información más específica"""
        html_lower = html.lower()
        titulo_lower = titulo.lower()
        
        # Cloudflare
        if 'cloudflare' in html_lower or '__cf_bm' in html_lower:
            return 'Cloudflare'
        
        # Sucuri
        if 'sucuri' in html_lower:
            return 'Sucuri WAF'
        
        # OpenResty / Nginx WAF
        if 'openresty' in html_lower or ('un momento' in titulo_lower and 'location.reload' in html_lower):
            return 'OpenResty/Nginx WAF'
        
        # Wordfence
        if 'wordfence' in html_lower:
            return 'Wordfence'
        
        # Genérico
        if any(x in html_lower for x in ['just a moment', 'checking your browser', 'ddos protection']):
            return 'WAF genérico'
        
        return 'Desconocido'
    
    def pasar_challenge(self, url: str, max_intentos: int = 5, 
                        espera_challenge: int = 15) -> Tuple[bool, Dict]:
        """
        Intenta pasar el challenge JavaScript de un sitio
        
        Returns:
            Tuple[bool, Dict]: (éxito, {cookies, html, url_final, tipo_waf})
        """
        if not self.driver:
            if not self.iniciar():
                return False, {'error': 'No se pudo iniciar el navegador'}
        
        resultado = {
            'cookies': {},
            'html': '',
            'url_final': '',
            'error': None,
            'tipo_waf': 'Desconocido'
        }
        
        try:
            # Asegurar que el driver está inicializado
            assert self.driver is not None, "Driver no inicializado"
            
            self.driver.get(url)
            
            # Verificar título inicial
            titulo_inicial = self.driver.title
            html_inicial = self.driver.page_source
            
            resultado['tipo_waf'] = self._detectar_tipo_challenge(html_inicial, titulo_inicial)
            
            # Indicadores de que seguimos en el challenge
            indicadores_challenge = [
                'setTimeout(function(){',
                'window.location.reload()',
                'Un momento',
                'Just a moment',
                'Checking your browser',
                'Please wait',
                'DDoS protection',
            ]
            
            # Variable para guardar el HTML
            html = html_inicial
            
            # Intentar esperar a que se resuelva el challenge
            for intento in range(max_intentos):
                time.sleep(espera_challenge)
                
                # Verificar si pasamos el challenge
                html = self.driver.page_source  # type: ignore[union-attr]
                titulo = self.driver.title  # type: ignore[union-attr]
                
                sigue_en_challenge = (
                    any(ind in html for ind in indicadores_challenge) or
                    titulo_inicial.lower() == titulo.lower()  # Título no cambió
                )
                
                if not sigue_en_challenge and len(html) > 1000:
                    # Parece que pasamos el challenge
                    resultado['html'] = html
                    resultado['url_final'] = self.driver.current_url  # type: ignore[union-attr]
                    
                    # Obtener cookies
                    for cookie in self.driver.get_cookies():  # type: ignore[union-attr]
                        resultado['cookies'][cookie['name']] = cookie['value']
                    
                    return True, resultado
            
            # Si llegamos aquí, no pudimos pasar el challenge
            error_msg = (
                f'No se pudo pasar el challenge de {resultado["tipo_waf"]}. '
                f'Este tipo de protección es muy agresiva y puede requerir '
                f'intervención manual o un navegador en modo visible.'
            )
            resultado['error'] = error_msg
            resultado['html'] = html
            return False, resultado
            
        except Exception as e:
            resultado['error'] = str(e)
            return False, resultado
    
    def obtener_sesion_requests(self, url: str):
        """
        Pasa el challenge y devuelve una sesión requests con las cookies válidas
        
        Returns:
            requests.Session o None si falla
        """
        import requests
        
        exito, resultado = self.pasar_challenge(url)
        if not exito:
            return None
        
        # Crear sesión con las cookies del navegador
        session = requests.Session()
        
        # Obtener User-Agent del navegador si está disponible
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        if self.driver:
            try:
                user_agent = self.driver.execute_script("return navigator.userAgent")
            except Exception:
                pass
        
        session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        })
        
        # Transferir cookies
        parsed = urlparse(url)
        domain = parsed.netloc
        
        for nombre, valor in resultado['cookies'].items():
            session.cookies.set(nombre, valor, domain=domain)
        
        return session
    
    def __enter__(self):
        self.iniciar()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cerrar()
        return False


def verificar_soporte_navegador() -> Dict:
    """Verifica el estado del soporte de navegador para challenges"""
    nav = NavegadorChallenge()
    
    chrome_ok, chrome_msg = nav.verificar_chrome_instalado()
    deps_ok, deps_msg = nav.verificar_dependencias()
    
    return {
        'chrome_instalado': chrome_ok,
        'chrome_info': chrome_msg,
        'dependencias_ok': deps_ok,
        'dependencias_info': deps_msg,
        'disponible': chrome_ok and deps_ok,
        'instrucciones_instalacion': _generar_instrucciones_instalacion(chrome_ok, deps_ok)
    }


def _generar_instrucciones_instalacion(chrome_ok: bool, deps_ok: bool) -> str:
    """Genera instrucciones de instalación según lo que falte"""
    instrucciones = []
    
    if not chrome_ok:
        instrucciones.append("""
📦 INSTALAR CHROME/CHROMIUM:

Ubuntu/Debian:
  sudo apt update
  sudo apt install chromium-browser

Fedora:
  sudo dnf install chromium

Arch Linux:
  sudo pacman -S chromium

Windows:
  Descargar desde https://www.google.com/chrome/
""")
    
    if not deps_ok:
        instrucciones.append("""
📦 INSTALAR DEPENDENCIAS PYTHON:

Ejecuta en el terminal:
  pip install selenium undetected-chromedriver

O desde Fijaten-WP, usa el botón "Instalar soporte Challenge"
en las opciones de escaneo.
""")
    
    if not instrucciones:
        return "✅ Todo está instalado correctamente."
    
    return "\n".join(instrucciones)
