"""
Fijaten-WP - Navegador para sitios con Challenge
Usa Selenium con undetected-chromedriver para pasar verificaciones JavaScript
"""

import time
import subprocess
import re
import shutil
from typing import Optional, Dict, Tuple, Any
from urllib.parse import urlparse


# Patrones de detección de WAF/Challenge
PATRONES_WAF = {
    'Cloudflare': ['cloudflare', '__cf_bm', 'cf-browser-verification', '__cf_chl_'],
    'Sucuri WAF': ['sucuri', 'sucuri-bg'],
    'OpenResty/Nginx WAF': ['openresty'],
    'Wordfence': ['wordfence', 'wfwaf-'],
    'WAF genérico': ['ddos protection', 'checking your browser', 'challenge-platform'],
}

TITULOS_CHALLENGE = ['un momento', 'just a moment', 'please wait', 'checking', 'ddos']

INDICADORES_CHALLENGE = [
    'settimeout(function(){', 'window.location.reload()', 'location.reload()',
    'please wait', 'ddos protection', 'checking your browser', 'challenge-platform',
]


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
        rutas_chrome = [
            'google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser',
            '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
        ]
        
        for ruta in rutas_chrome:
            if shutil.which(ruta):
                return True, ruta
        
        # En Windows
        import platform
        if platform.system() == 'Windows':
            import os
            rutas_windows = [
                r'C:\Program Files\Google\Chrome\Application\chrome.exe',
                r'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe',
            ]
            for ruta in rutas_windows:
                if os.path.exists(ruta):
                    return True, ruta
        
        return False, "Chrome/Chromium no encontrado"
    
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
            
            # Detectar versión de Chrome
            chrome_version = self._obtener_version_chrome()
            
            self.driver = uc.Chrome(options=options, version_main=chrome_version)
            self.driver.set_page_load_timeout(self.timeout)
            return True
            
        except Exception as e:
            self._error_instalacion = str(e)
            return False
    
    def _obtener_version_chrome(self) -> int:
        """Obtiene la versión principal de Chrome instalada"""
        comandos = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
        
        for cmd in comandos:
            try:
                result = subprocess.run([cmd, '--version'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    match = re.search(r'(\d+)\.', result.stdout)
                    if match:
                        return int(match.group(1))
            except Exception:
                continue
        return 142  # Valor por defecto
    
    def cerrar(self):
        """Cierra el navegador"""
        if self.driver:
            try:
                self.driver.quit()
            except Exception:
                pass
            self.driver = None
    
    def _detectar_tipo_waf(self, html: str, titulo: str) -> str:
        """Detecta el tipo de WAF/challenge basándose en patrones conocidos"""
        html_lower = html.lower()
        titulo_lower = titulo.lower()
        
        # Buscar en patrones definidos
        for nombre_waf, patrones in PATRONES_WAF.items():
            if any(p in html_lower for p in patrones):
                return nombre_waf
        
        # Caso especial: OpenResty con título en español
        if 'un momento' in titulo_lower and 'reload' in html_lower:
            return 'OpenResty/Nginx WAF'
        
        return 'Desconocido'
    
    def _es_pagina_challenge(self, html: str, titulo: str) -> bool:
        """Verifica si el contenido es una página de challenge"""
        html_lower = html.lower()
        titulo_lower = titulo.lower()
        
        # Título indica challenge
        if any(t in titulo_lower for t in TITULOS_CHALLENGE):
            return True
        
        # Múltiples indicadores de challenge en HTML
        if sum(1 for ind in INDICADORES_CHALLENGE if ind.lower() in html_lower) >= 2:
            return True
        
        # HTML muy corto con reload
        if len(html) < 2000 and 'reload' in html_lower:
            return True
        
        return False
    
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
            assert self.driver is not None
            self.driver.get(url)
            
            titulo_inicial = self.driver.title
            html_inicial = self.driver.page_source
            resultado['tipo_waf'] = self._detectar_tipo_waf(html_inicial, titulo_inicial)
            
            # Verificar si el contenido inicial ya es válido
            if not self._es_pagina_challenge(html_inicial, titulo_inicial):
                resultado['html'] = html_inicial
                resultado['url_final'] = self.driver.current_url
                resultado['tipo_waf'] = 'Ninguno'
                for cookie in self.driver.get_cookies():
                    resultado['cookies'][cookie['name']] = cookie['value']
                return True, resultado
            
            # Intentar esperar a que se resuelva el challenge
            html = html_inicial
            for intento in range(max_intentos):
                wait_time = 5 if intento < 2 else espera_challenge
                time.sleep(wait_time)
                
                html = self.driver.page_source
                titulo = self.driver.title
                
                if not self._es_pagina_challenge(html, titulo) and len(html) > 2000:
                    resultado['html'] = html
                    resultado['url_final'] = self.driver.current_url
                    for cookie in self.driver.get_cookies():
                        resultado['cookies'][cookie['name']] = cookie['value']
                    return True, resultado
            
            # No pudimos pasar el challenge
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
    
    instrucciones = []
    if not chrome_ok:
        instrucciones.append("• Instalar Chrome/Chromium: sudo apt install chromium-browser")
    if not deps_ok:
        instrucciones.append("• Instalar dependencias: pip install selenium undetected-chromedriver")
    
    return {
        'chrome_instalado': chrome_ok,
        'chrome_info': chrome_msg,
        'dependencias_ok': deps_ok,
        'dependencias_info': deps_msg,
        'disponible': chrome_ok and deps_ok,
        'instrucciones': "\n".join(instrucciones) if instrucciones else "✅ Todo instalado"
    }
