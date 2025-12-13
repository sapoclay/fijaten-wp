"""
Módulo de análisis de vulnerabilidades de WordPress
Contiene todas las funciones para detectar vulnerabilidades comunes
"""

import requests
import re
import ssl
import socket
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import Enum
import concurrent.futures

class Severidad(Enum):
    """Niveles de severidad de vulnerabilidades"""
    CRITICA = "🔴 CRÍTICA"
    ALTA = "🟠 ALTA"
    MEDIA = "🟡 MEDIA"
    BAJA = "🟢 BAJA"
    INFO = "🔵 INFO"

@dataclass
class Vulnerabilidad:
    """Representa una vulnerabilidad detectada"""
    nombre: str
    severidad: Severidad
    descripcion: str
    explicacion_simple: str
    recomendacion: str
    detalles: str = ""

class AnalizadorWordPress:
    """Analizador de vulnerabilidades para sitios WordPress"""
    
    def __init__(self, dominio: str, callback=None):
        self.dominio_original = dominio
        self.dominio = self._normalizar_dominio(dominio)
        self.callback = callback
        self.vulnerabilidades: List[Vulnerabilidad] = []
        self.info_sitio: Dict = {}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.timeout = 10
        
    def _normalizar_dominio(self, dominio: str) -> str:
        """Normaliza el dominio añadiendo protocolo si es necesario"""
        dominio = dominio.strip()
        if not dominio.startswith(('http://', 'https://')):
            dominio = 'https://' + dominio
        return dominio.rstrip('/')
    
    def _registrar_mensaje(self, mensaje: str):
        """Envía mensajes de progreso al callback"""
        if self.callback:
            self.callback(mensaje)
    
    def _realizar_peticion(self, url: str, metodo: str = 'GET', **kwargs) -> Optional[requests.Response]:
        """Realiza una petición HTTP con manejo de errores"""
        try:
            kwargs.setdefault('timeout', self.timeout)
            kwargs.setdefault('verify', True)
            kwargs.setdefault('allow_redirects', True)
            
            if metodo.upper() == 'GET':
                return self.session.get(url, **kwargs)
            elif metodo.upper() == 'HEAD':
                return self.session.head(url, **kwargs)
            elif metodo.upper() == 'POST':
                return self.session.post(url, **kwargs)
        except requests.exceptions.SSLError:
            # Intentar sin verificación SSL
            kwargs['verify'] = False
            try:
                if metodo.upper() == 'GET':
                    return self.session.get(url, **kwargs)
                elif metodo.upper() == 'HEAD':
                    return self.session.head(url, **kwargs)
            except:
                pass
        except:
            pass
        return None
    
    def verificar_es_wordpress(self) -> bool:
        """Verifica si el sitio es WordPress"""
        self._registrar_mensaje("🔍 Verificando si es un sitio WordPress...")
        
        indicadores = [
            '/wp-content/',
            '/wp-includes/',
            '/wp-admin/',
            'wp-json',
            '/xmlrpc.php',
            'WordPress'
        ]
        
        response = self._realizar_peticion(self.dominio)
        if not response:
            return False
        
        contenido = response.text
        
        for indicador in indicadores:
            if indicador in contenido:
                self.info_sitio['es_wordpress'] = True
                return True
        
        # Verificar wp-login.php
        login_response = self._realizar_peticion(f"{self.dominio}/wp-login.php")
        if login_response and login_response.status_code == 200:
            self.info_sitio['es_wordpress'] = True
            return True
        
        return False
    
    def detectar_version_wordpress(self):
        """Detecta la versión de WordPress"""
        self._registrar_mensaje("🔍 Detectando versión de WordPress...")
        
        version = None
        metodo = None
        
        # Método 1: Meta generator
        response = self._realizar_peticion(self.dominio)
        if response:
            soup = BeautifulSoup(response.text, 'html.parser')
            meta = soup.find('meta', attrs={'name': 'generator'})
            if meta:
                content = meta.get('content', '')
                if content and isinstance(content, str) and 'WordPress' in content:
                    match = re.search(r'WordPress\s+([\d.]+)', content)
                    if match:
                        version = match.group(1)
                        metodo = "Meta tag generator"
        
        # Método 2: readme.html
        if not version:
            readme_response = self._realizar_peticion(f"{self.dominio}/readme.html")
            if readme_response and readme_response.status_code == 200:
                match = re.search(r'Version\s+([\d.]+)', readme_response.text)
                if match:
                    version = match.group(1)
                    metodo = "readme.html expuesto"
                    self.vulnerabilidades.append(Vulnerabilidad(
                        nombre="Archivo readme.html expuesto",
                        severidad=Severidad.BAJA,
                        descripcion="El archivo readme.html está accesible públicamente y revela la versión de WordPress.",
                        explicacion_simple="Es como dejar visible el manual de instrucciones de tu casa, que indica qué cerradura tienes instalada.",
                        recomendacion="Eliminar o restringir el acceso al archivo readme.html",
                        detalles=f"URL: {self.dominio}/readme.html"
                    ))
        
        # Método 3: RSS Feed
        if not version:
            feed_response = self._realizar_peticion(f"{self.dominio}/feed/")
            if feed_response and feed_response.status_code == 200:
                match = re.search(r'generator>https?://wordpress\.org/\?v=([\d.]+)<', feed_response.text)
                if match:
                    version = match.group(1)
                    metodo = "RSS Feed"
        
        if version:
            self.info_sitio['version_wordpress'] = version
            self.info_sitio['metodo_version'] = metodo
            
            # Verificar si es versión antigua
            try:
                partes = [int(x) for x in version.split('.')]
                if partes[0] < 6 or (partes[0] == 6 and len(partes) > 1 and partes[1] < 4):
                    self.vulnerabilidades.append(Vulnerabilidad(
                        nombre="Versión de WordPress desactualizada",
                        severidad=Severidad.ALTA,
                        descripcion=f"WordPress versión {version} está desactualizada y puede contener vulnerabilidades conocidas.",
                        explicacion_simple="Es como usar una cerradura antigua que los ladrones ya saben cómo abrir. Las versiones nuevas corrigen fallos de seguridad.",
                        recomendacion="Actualizar WordPress a la última versión estable disponible.",
                        detalles=f"Versión detectada: {version}"
                    ))
            except:
                pass
        else:
            self.info_sitio['version_wordpress'] = "No detectada (bien ocultada)"
    
    def verificar_ssl(self):
        """Verifica la configuración SSL/HTTPS"""
        self._registrar_mensaje("🔒 Verificando certificado SSL/HTTPS...")
        
        parsed = urlparse(self.dominio)
        hostname = parsed.netloc
        
        # Verificar si usa HTTPS
        try:
            http_response = self._realizar_peticion(f"http://{hostname}", allow_redirects=False)
            if http_response:
                if http_response.status_code not in [301, 302, 307, 308]:
                    self.vulnerabilidades.append(Vulnerabilidad(
                        nombre="Sitio accesible por HTTP sin redirección",
                        severidad=Severidad.ALTA,
                        descripcion="El sitio permite acceso por HTTP sin redirigir a HTTPS.",
                        explicacion_simple="Es como enviar una carta sin sobre: cualquiera puede leer lo que escribes, incluyendo contraseñas.",
                        recomendacion="Configurar redirección forzada de HTTP a HTTPS en el servidor.",
                        detalles="El tráfico HTTP no está cifrado y puede ser interceptado."
                    ))
        except:
            pass
        
        # Verificar certificado SSL
        try:
            context = ssl.create_default_context()
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    cert = ssock.getpeercert()
                    self.info_sitio['ssl_valido'] = True
                    if cert:
                        issuer = cert.get('issuer', [])
                        self.info_sitio['ssl_emisor'] = {item[0][0]: item[0][1] for item in issuer if item}
        except ssl.SSLCertVerificationError as e:
            self.info_sitio['ssl_valido'] = False
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="Certificado SSL inválido",
                severidad=Severidad.CRITICA,
                descripcion=f"El certificado SSL no es válido: {str(e)}",
                explicacion_simple="El 'candado' de seguridad de la web está roto. Los visitantes verán advertencias de seguridad.",
                recomendacion="Renovar o instalar un certificado SSL válido (Let's Encrypt es gratuito).",
                detalles=str(e)
            ))
        except Exception as e:
            self.info_sitio['ssl_valido'] = False
    
    def verificar_xmlrpc(self):
        """Verifica si XML-RPC está habilitado"""
        self._registrar_mensaje("🔍 Verificando XML-RPC...")
        
        xmlrpc_url = f"{self.dominio}/xmlrpc.php"
        response = self._realizar_peticion(xmlrpc_url, method='POST', 
                                        data='<?xml version="1.0"?><methodCall><methodName>system.listMethods</methodName></methodCall>',
                                        headers={'Content-Type': 'application/xml'})
        
        if response and response.status_code == 200 and 'methodResponse' in response.text:
            metodos = re.findall(r'<string>([^<]+)</string>', response.text)
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="XML-RPC habilitado",
                severidad=Severidad.ALTA,
                descripcion="El archivo xmlrpc.php está activo y responde a peticiones.",
                explicacion_simple="Es como tener una puerta trasera en tu casa. Los atacantes pueden usarla para intentar adivinar contraseñas miles de veces por minuto.",
                recomendacion="Deshabilitar XML-RPC si no se usa, o usar un plugin de seguridad para protegerlo.",
                detalles=f"Métodos disponibles: {len(metodos)}"
            ))
            self.info_sitio['xmlrpc_activo'] = True
        else:
            self.info_sitio['xmlrpc_activo'] = False
    
    def verificar_enumeracion_usuarios(self):
        """Verifica si es posible enumerar usuarios"""
        self._registrar_mensaje("👥 Verificando enumeración de usuarios...")
        
        usuarios_encontrados = []
        
        # Método 1: ?author=N
        for i in range(1, 6):
            response = self._realizar_peticion(f"{self.dominio}/?author={i}", allow_redirects=False)
            if response and response.status_code in [301, 302]:
                location = response.headers.get('Location', '')
                match = re.search(r'/author/([^/]+)', location)
                if match:
                    usuarios_encontrados.append(match.group(1))
        
        # Método 2: wp-json/wp/v2/users
        response = self._realizar_peticion(f"{self.dominio}/wp-json/wp/v2/users")
        if response and response.status_code == 200:
            try:
                users = response.json()
                for user in users:
                    if user.get('slug') and user['slug'] not in usuarios_encontrados:
                        usuarios_encontrados.append(user['slug'])
            except:
                pass
        
        if usuarios_encontrados:
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="Enumeración de usuarios posible",
                severidad=Severidad.MEDIA,
                descripcion="Es posible descubrir nombres de usuario del sitio.",
                explicacion_simple="Los atacantes pueden ver los nombres de usuario, lo que les facilita intentar adivinar contraseñas.",
                recomendacion="Deshabilitar la enumeración de usuarios con un plugin de seguridad o reglas en .htaccess",
                detalles=f"Usuarios encontrados: {', '.join(usuarios_encontrados)}"
            ))
            self.info_sitio['usuarios_expuestos'] = usuarios_encontrados
    
    def verificar_wp_config_backup(self):
        """Busca backups expuestos de wp-config.php"""
        self._registrar_mensaje("📁 Buscando archivos de configuración expuestos...")
        
        archivos_backup = [
            'wp-config.php.bak',
            'wp-config.php.old',
            'wp-config.php.save',
            'wp-config.php~',
            'wp-config.php.swp',
            'wp-config.bak',
            'wp-config.old',
            '.wp-config.php.swp',
            'wp-config.txt'
        ]
        
        archivos_expuestos = []
        for archivo in archivos_backup:
            response = self._realizar_peticion(f"{self.dominio}/{archivo}")
            if response and response.status_code == 200 and len(response.text) > 100:
                if 'DB_NAME' in response.text or 'DB_PASSWORD' in response.text:
                    archivos_expuestos.append(archivo)
        
        if archivos_expuestos:
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="Backup de wp-config.php expuesto",
                severidad=Severidad.CRITICA,
                descripcion="Se encontraron archivos de backup de configuración accesibles públicamente.",
                explicacion_simple="¡GRAVE! Es como dejar las llaves de tu casa y la combinación de tu caja fuerte en el buzón. Contiene contraseñas de la base de datos.",
                recomendacion="URGENTE: Eliminar inmediatamente estos archivos del servidor.",
                detalles=f"Archivos encontrados: {', '.join(archivos_expuestos)}"
            ))
    
    def verificar_debug_mode(self):
        """Verifica si el modo debug está activo"""
        self._registrar_mensaje("🐛 Verificando modo debug...")
        
        response = self._realizar_peticion(self.dominio)
        if response:
            # Buscar indicadores de debug activo
            indicadores_debug = [
                'Notice:',
                'Warning:',
                'Fatal error:',
                'Parse error:',
                'WP_DEBUG',
                'Deprecated:',
                'Stack trace:'
            ]
            
            for indicador in indicadores_debug:
                if indicador in response.text:
                    self.vulnerabilidades.append(Vulnerabilidad(
                        nombre="Modo Debug posiblemente activo",
                        severidad=Severidad.MEDIA,
                        descripcion="Se detectaron mensajes de error que podrían indicar que WP_DEBUG está activo.",
                        explicacion_simple="El sitio está mostrando errores técnicos que pueden revelar información interna a los atacantes.",
                        recomendacion="Desactivar WP_DEBUG en wp-config.php para sitios en producción.",
                        detalles=f"Indicador encontrado: {indicador}"
                    ))
                    break
        
        # Verificar debug.log
        debug_log = self._realizar_peticion(f"{self.dominio}/wp-content/debug.log")
        if debug_log and debug_log.status_code == 200 and len(debug_log.text) > 50:
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="Archivo debug.log expuesto",
                severidad=Severidad.ALTA,
                descripcion="El archivo de log de debug es accesible públicamente.",
                explicacion_simple="Es como dejar un diario con todos los errores del sitio abierto. Puede contener información sensible.",
                recomendacion="Mover o proteger el archivo debug.log. Añadir regla en .htaccess para bloquearlo.",
                detalles=f"URL: {self.dominio}/wp-content/debug.log"
            ))
    
    def verificar_listado_directorios(self):
        """Verifica si hay listado de directorios habilitado"""
        self._registrar_mensaje("📂 Verificando listado de directorios...")
        
        directorios = [
            '/wp-content/',
            '/wp-content/uploads/',
            '/wp-content/plugins/',
            '/wp-content/themes/',
            '/wp-includes/'
        ]
        
        directorios_listables = []
        for directorio in directorios:
            response = self._realizar_peticion(f"{self.dominio}{directorio}")
            if response and response.status_code == 200:
                if 'Index of' in response.text or 'Parent Directory' in response.text:
                    directorios_listables.append(directorio)
        
        if directorios_listables:
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="Listado de directorios habilitado",
                severidad=Severidad.MEDIA,
                descripcion="Algunos directorios permiten ver su contenido.",
                explicacion_simple="Es como dejar las puertas de los armarios abiertas: cualquiera puede ver qué hay dentro.",
                recomendacion="Deshabilitar el listado de directorios en el servidor o añadir 'Options -Indexes' en .htaccess",
                detalles=f"Directorios listables: {', '.join(directorios_listables)}"
            ))
    
    def verificar_plugins_vulnerables(self):
        """Detecta plugins instalados y busca vulnerabilidades conocidas"""
        self._registrar_mensaje("🔌 Analizando plugins instalados...")
        
        plugins_detectados = []
        
        response = self._realizar_peticion(self.dominio)
        if response:
            # Buscar plugins en el código fuente
            plugin_matches = re.findall(r'/wp-content/plugins/([^/\'"]+)', response.text)
            plugins_detectados.extend(set(plugin_matches))
        
        # Verificar plugins comunes
        plugins_comunes = [
            'contact-form-7',
            'elementor',
            'woocommerce',
            'yoast-seo',
            'wordfence',
            'akismet',
            'jetpack',
            'wp-super-cache',
            'wpforms-lite',
            'classic-editor'
        ]
        
        for plugin in plugins_comunes:
            if plugin not in plugins_detectados:
                response = self._realizar_peticion(f"{self.dominio}/wp-content/plugins/{plugin}/readme.txt")
                if response and response.status_code == 200:
                    plugins_detectados.append(plugin)
        
        self.info_sitio['plugins_detectados'] = list(set(plugins_detectados))
        
        # Verificar readme.txt de plugins (pueden revelar versiones)
        plugins_con_version = []
        for plugin in plugins_detectados[:10]:  # Limitar a 10 para no tardar mucho
            response = self._realizar_peticion(f"{self.dominio}/wp-content/plugins/{plugin}/readme.txt")
            if response and response.status_code == 200:
                version_match = re.search(r'Stable tag:\s*([\d.]+)', response.text)
                if version_match:
                    plugins_con_version.append(f"{plugin} v{version_match.group(1)}")
        
        if plugins_con_version:
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="Versiones de plugins expuestas",
                severidad=Severidad.BAJA,
                descripcion="Los archivos readme.txt de los plugins revelan sus versiones.",
                explicacion_simple="Los atacantes pueden saber qué versiones de plugins usas y buscar fallos conocidos.",
                recomendacion="Eliminar o restringir acceso a archivos readme.txt de plugins.",
                detalles=f"Plugins con versión visible: {', '.join(plugins_con_version)}"
            ))
    
    def verificar_temas(self):
        """Detecta el tema y busca vulnerabilidades"""
        self._registrar_mensaje("🎨 Analizando tema instalado...")
        
        response = self._realizar_peticion(self.dominio)
        if response:
            theme_match = re.search(r'/wp-content/themes/([^/\'"]+)', response.text)
            if theme_match:
                tema = theme_match.group(1)
                self.info_sitio['tema_activo'] = tema
                
                # Verificar style.css del tema
                style_response = self._realizar_peticion(f"{self.dominio}/wp-content/themes/{tema}/style.css")
                if style_response and style_response.status_code == 200:
                    version_match = re.search(r'Version:\s*([\d.]+)', style_response.text)
                    if version_match:
                        self.info_sitio['tema_version'] = version_match.group(1)
    
    def verificar_login_seguridad(self):
        """Verifica la seguridad de la página de login"""
        self._registrar_mensaje("🔐 Verificando seguridad del login...")
        
        login_url = f"{self.dominio}/wp-login.php"
        response = self._realizar_peticion(login_url)
        
        if response and response.status_code == 200:
            # Verificar si muestra errores específicos
            # Intentar login fallido para ver mensaje de error
            login_response = self._realizar_peticion(
                login_url,
                method='POST',
                data={
                    'log': 'test_user_nonexistent',
                    'pwd': 'test_password_wrong',
                    'wp-submit': 'Log In'
                },
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if login_response:
                if 'usuario no está registrado' in login_response.text.lower() or \
                   'invalid username' in login_response.text.lower() or \
                   'unknown username' in login_response.text.lower():
                    self.vulnerabilidades.append(Vulnerabilidad(
                        nombre="Mensajes de error de login revelan información",
                        severidad=Severidad.BAJA,
                        descripcion="Los mensajes de error indican si un usuario existe o no.",
                        explicacion_simple="El sitio dice si un nombre de usuario existe, lo que ayuda a los atacantes a saber qué usuarios probar.",
                        recomendacion="Usar mensajes de error genéricos que no revelen si el usuario existe.",
                        detalles="El formulario de login revela la existencia de usuarios"
                    ))
    
    def verificar_wp_cron(self):
        """Verifica si wp-cron está expuesto"""
        self._registrar_mensaje("⏰ Verificando wp-cron...")
        
        response = self._realizar_peticion(f"{self.dominio}/wp-cron.php")
        if response and response.status_code == 200:
            self.info_sitio['wp_cron_accesible'] = True
    
    def verificar_rest_api(self):
        """Verifica la exposición de la REST API"""
        self._registrar_mensaje("🔌 Verificando REST API...")
        
        response = self._realizar_peticion(f"{self.dominio}/wp-json/")
        if response and response.status_code == 200:
            try:
                data = response.json()
                if 'routes' in data:
                    rutas_sensibles = [r for r in data['routes'].keys() if 'user' in r.lower()]
                    if rutas_sensibles:
                        self.info_sitio['rest_api_expuesta'] = True
            except:
                pass
    
    def verificar_cabeceras_seguridad(self):
        """Verifica las cabeceras de seguridad HTTP"""
        self._registrar_mensaje("🛡️ Verificando cabeceras de seguridad...")
        
        response = self._realizar_peticion(self.dominio)
        if not response:
            return
        
        cabeceras = response.headers
        cabeceras_faltantes = []
        
        cabeceras_importantes = {
            'X-Content-Type-Options': 'Previene ataques de tipo MIME sniffing',
            'X-Frame-Options': 'Previene ataques de clickjacking',
            'X-XSS-Protection': 'Ayuda a prevenir ataques XSS',
            'Strict-Transport-Security': 'Fuerza conexiones HTTPS',
            'Content-Security-Policy': 'Controla qué recursos puede cargar la página'
        }
        
        for cabecera, descripcion in cabeceras_importantes.items():
            if cabecera.lower() not in [h.lower() for h in cabeceras.keys()]:
                cabeceras_faltantes.append(f"{cabecera}: {descripcion}")
        
        if cabeceras_faltantes:
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="Cabeceras de seguridad HTTP faltantes",
                severidad=Severidad.MEDIA,
                descripcion="El servidor no envía algunas cabeceras de seguridad recomendadas.",
                explicacion_simple="Es como no tener cerrojos adicionales en la puerta. Estas cabeceras añaden capas extra de protección.",
                recomendacion="Configurar las cabeceras de seguridad en el servidor web o usando un plugin.",
                detalles="\n".join(cabeceras_faltantes)
            ))
    
    def verificar_archivo_robots(self):
        """Verifica el archivo robots.txt"""
        self._registrar_mensaje("🤖 Verificando robots.txt...")
        
        response = self._realizar_peticion(f"{self.dominio}/robots.txt")
        if response and response.status_code == 200:
            contenido = response.text.lower()
            rutas_sensibles = []
            
            if '/wp-admin' in contenido or '/wp-login' in contenido:
                rutas_sensibles.append('wp-admin/wp-login')
            
            if rutas_sensibles:
                self.vulnerabilidades.append(Vulnerabilidad(
                    nombre="Robots.txt revela rutas sensibles",
                    severidad=Severidad.BAJA,
                    descripcion="El archivo robots.txt menciona rutas de administración.",
                    explicacion_simple="Aunque robots.txt es para buscadores, los atacantes también lo leen para encontrar páginas interesantes.",
                    recomendacion="Considerar no listar rutas sensibles en robots.txt",
                    detalles=f"URL: {self.dominio}/robots.txt"
                ))
    
    def verificar_malware_conocido(self):
        """Busca patrones de código malicioso conocido en archivos accesibles"""
        self._registrar_mensaje("🦠 Buscando indicadores de malware...")
        
        # Patrones de malware conocidos en WordPress
        patrones_malware = [
            (r'eval\s*\(\s*base64_decode', 'Código ofuscado con eval/base64'),
            (r'eval\s*\(\s*gzinflate', 'Código comprimido malicioso'),
            (r'eval\s*\(\s*str_rot13', 'Código ofuscado con ROT13'),
            (r'preg_replace\s*\([^)]*["\']\/e["\']', 'preg_replace con modificador /e (ejecución)'),
            (r'assert\s*\(\s*\$_(GET|POST|REQUEST)', 'Backdoor con assert'),
            (r'\$\w+\s*=\s*\$_(GET|POST|REQUEST)\s*\[\s*["\'][^"\']+["\']\s*\]\s*;\s*@?\$\w+\s*\(', 'Web shell'),
            (r'<\?php\s+\/\*\s*[a-f0-9]{32}\s*\*\/', 'Firma de malware conocido'),
            (r'FilesMan|WSO|c99|r57|b374k', 'Shell conocida detectada'),
            (r'passthru|shell_exec|system\s*\(\s*\$_(GET|POST)', 'Ejecución de comandos sospechosa'),
        ]
        
        # Archivos a verificar
        archivos_verificar = [
            '/wp-includes/version.php',
            '/index.php',
            '/wp-blog-header.php',
            '/wp-load.php',
        ]
        
        indicadores_encontrados = []
        
        for archivo in archivos_verificar:
            response = self._realizar_peticion(f"{self.dominio}{archivo}")
            if response and response.status_code == 200:
                contenido = response.text
                for patron, descripcion in patrones_malware:
                    if re.search(patron, contenido, re.IGNORECASE):
                        indicadores_encontrados.append(f"{archivo}: {descripcion}")
        
        # Verificar archivos sospechosos en ubicaciones comunes
        archivos_sospechosos = [
            '/wp-content/uploads/wp-info.php',
            '/wp-content/uploads/info.php',
            '/wp-content/uploads/shell.php',
            '/wp-content/uploads/.htaccess',
            '/wp-includes/wp-tmp.php',
            '/wp-admin/css/colors/blue/blue.php',
        ]
        
        for archivo in archivos_sospechosos:
            response = self._realizar_peticion(f"{self.dominio}{archivo}")
            if response and response.status_code == 200:
                # Si responde 200 a estos archivos, es muy sospechoso
                if 'php' in archivo and len(response.text) > 0:
                    indicadores_encontrados.append(f"{archivo}: Archivo sospechoso accesible")
        
        if indicadores_encontrados:
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="Posible malware o código malicioso detectado",
                severidad=Severidad.CRITICA,
                descripcion="Se encontraron indicadores de código malicioso en el sitio.",
                explicacion_simple="¡ALERTA! Tu sitio podría estar infectado con malware. Es como encontrar un ladrón escondido en tu casa. Esto puede robar datos de tus visitantes.",
                recomendacion="URGENTE: Realizar una limpieza completa del sitio. Restaurar desde backup limpio o contratar un servicio de limpieza de malware.",
                detalles="\n".join(indicadores_encontrados[:10])  # Limitar a 10
            ))
            self.info_sitio['malware_detectado'] = True
        else:
            self.info_sitio['malware_detectado'] = False
    
    def verificar_permisos_archivos(self):
        """Verifica si archivos críticos están expuestos o tienen permisos incorrectos"""
        self._registrar_mensaje("📁 Verificando exposición de archivos críticos...")
        
        # Archivos que NO deberían ser accesibles directamente
        archivos_criticos = [
            ('/wp-config.php', 'Archivo de configuración principal'),
            ('/.htaccess', 'Archivo de configuración del servidor'),
            ('/wp-content/debug.log', 'Log de depuración'),
            ('/wp-content/uploads/wc-logs/', 'Logs de WooCommerce'),
            ('/error_log', 'Log de errores'),
            ('/php_error.log', 'Log de errores PHP'),
            ('/.env', 'Variables de entorno'),
            ('/.git/config', 'Configuración de Git'),
            ('/composer.json', 'Dependencias de Composer'),
            ('/wp-config.php.save', 'Backup de configuración'),
            ('/wp-content/backup-db/', 'Backups de base de datos'),
        ]
        
        archivos_expuestos = []
        
        for archivo, descripcion in archivos_criticos:
            response = self._realizar_peticion(f"{self.dominio}{archivo}")
            if response:
                # 200 = accesible (malo para estos archivos)
                # 403 = prohibido (bien)
                # 404 = no existe (bien)
                if response.status_code == 200:
                    # Verificar que realmente hay contenido sensible
                    contenido = response.text.lower()
                    if any(palabra in contenido for palabra in ['db_name', 'db_password', 'define(', '<?php', 'rewriterule', 'error', 'exception', 'stack trace']):
                        archivos_expuestos.append(f"{archivo} - {descripcion}")
        
        if archivos_expuestos:
            severidad = Severidad.CRITICA if any('wp-config' in a or 'db' in a.lower() for a in archivos_expuestos) else Severidad.ALTA
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="Archivos críticos expuestos públicamente",
                severidad=severidad,
                descripcion="Archivos sensibles del sistema están accesibles desde internet.",
                explicacion_simple="Es como dejar documentos importantes en la calle. Cualquiera puede ver información privada como contraseñas de base de datos.",
                recomendacion="Bloquear el acceso a estos archivos mediante .htaccess o configuración del servidor. Mover archivos sensibles fuera del directorio público.",
                detalles="\n".join(archivos_expuestos)
            ))
            self.info_sitio['archivos_expuestos'] = archivos_expuestos
    
    def verificar_politica_contrasenas(self):
        """Verifica si el sitio permite contraseñas débiles"""
        self._registrar_mensaje("🔑 Analizando política de contraseñas...")
        
        problemas_encontrados = []
        
        # Verificar página de registro
        registro_urls = [
            f"{self.dominio}/wp-login.php?action=register",
            f"{self.dominio}/registro/",
            f"{self.dominio}/register/",
        ]
        
        registro_habilitado = False
        for url in registro_urls:
            response = self._realizar_peticion(url)
            if response and response.status_code == 200:
                contenido = response.text.lower()
                if 'user_login' in contenido or 'user_email' in contenido or 'registr' in contenido:
                    registro_habilitado = True
                    
                    # Verificar si hay indicadores de política de contraseñas
                    if 'password' in contenido or 'contraseña' in contenido:
                        # Buscar indicadores de validación de contraseña
                        tiene_validacion = any(indicador in contenido for indicador in [
                            'password-strength',
                            'pw-strength',
                            'passwordstrength',
                            'zxcvbn',  # Librería popular de validación
                            'minimum',
                            'mínimo',
                            'at least',
                            'al menos',
                            'strong password',
                            'contraseña segura'
                        ])
                        
                        if not tiene_validacion:
                            problemas_encontrados.append("No se detectó validación de fortaleza de contraseña en el registro")
                    break
        
        # Verificar si el registro está abierto (puede ser un problema)
        if registro_habilitado:
            self.info_sitio['registro_abierto'] = True
            
            # Verificar protección contra spam en registro
            response = self._realizar_peticion(f"{self.dominio}/wp-login.php?action=register")
            if response and response.status_code == 200:
                contenido = response.text.lower()
                tiene_captcha = any(captcha in contenido for captcha in [
                    'recaptcha',
                    'hcaptcha',
                    'captcha',
                    'g-recaptcha',
                    'cf-turnstile'
                ])
                
                if not tiene_captcha:
                    problemas_encontrados.append("Registro sin CAPTCHA - vulnerable a spam de bots")
        
        # Verificar página de recuperación de contraseña
        response = self._realizar_peticion(f"{self.dominio}/wp-login.php?action=lostpassword")
        if response and response.status_code == 200:
            contenido = response.text.lower()
            if 'user_login' in contenido:
                # Verificar si revela información
                # Intentar con usuario inexistente
                test_response = self._realizar_peticion(
                    f"{self.dominio}/wp-login.php?action=lostpassword",
                    metodo='POST',
                    data={'user_login': 'usuario_inexistente_test_12345', 'redirect_to': '', 'wp-submit': 'Get New Password'},
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                if test_response and ('no existe' in test_response.text.lower() or 'invalid' in test_response.text.lower() or 'no user' in test_response.text.lower()):
                    problemas_encontrados.append("Recuperación de contraseña revela si el usuario existe")
        
        if problemas_encontrados:
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="Política de contraseñas débil o inexistente",
                severidad=Severidad.MEDIA,
                descripcion="El sitio no implementa una política robusta de contraseñas.",
                explicacion_simple="Es como dejar que la gente use '123456' como contraseña. Los atacantes pueden adivinar contraseñas fácilmente.",
                recomendacion="Instalar un plugin de seguridad que fuerce contraseñas fuertes. Añadir CAPTCHA al registro. Usar mensajes genéricos en recuperación de contraseña.",
                detalles="\n".join(problemas_encontrados)
            ))
    
    def verificar_hotlinking(self):
        """Verifica si las imágenes están protegidas contra hotlinking"""
        self._registrar_mensaje("🖼️ Verificando protección contra hotlinking...")
        
        # Buscar una imagen en el sitio
        response = self._realizar_peticion(self.dominio)
        if not response:
            return
        
        # Buscar URLs de imágenes en el contenido
        imagenes = re.findall(r'["\']([^"\']+\.(?:jpg|jpeg|png|gif|webp))["\']', response.text, re.IGNORECASE)
        
        if not imagenes:
            return
        
        # Tomar la primera imagen que sea del mismo dominio
        imagen_test = None
        parsed_dominio = urlparse(self.dominio)
        
        for img in imagenes:
            if img.startswith('/'):
                imagen_test = f"{self.dominio}{img}"
                break
            elif parsed_dominio.netloc in img:
                imagen_test = img if img.startswith('http') else f"{self.dominio}/{img}"
                break
        
        if not imagen_test:
            return
        
        # Intentar acceder a la imagen con un Referer diferente (simulando hotlinking)
        headers_hotlink = {
            'Referer': 'https://sitio-malicioso-ejemplo.com/',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        # Petición normal (desde el mismo sitio)
        response_normal = self._realizar_peticion(imagen_test)
        
        # Petición con referer externo (hotlinking)
        try:
            response_hotlink = self.session.get(imagen_test, headers=headers_hotlink, timeout=self.timeout, verify=False)
            
            if response_normal and response_hotlink:
                # Si ambas respuestas son 200 y tienen el mismo contenido, no hay protección
                if response_normal.status_code == 200 and response_hotlink.status_code == 200:
                    if len(response_normal.content) == len(response_hotlink.content):
                        self.vulnerabilidades.append(Vulnerabilidad(
                            nombre="Sin protección contra hotlinking de imágenes",
                            severidad=Severidad.BAJA,
                            descripcion="Las imágenes del sitio pueden ser enlazadas desde otros sitios web.",
                            explicacion_simple="Otros sitios pueden usar tus imágenes directamente, consumiendo tu ancho de banda y recursos del servidor sin tu permiso.",
                            recomendacion="Configurar reglas anti-hotlinking en .htaccess o usar un CDN con protección de hotlink.",
                            detalles=f"Imagen probada: {imagen_test}"
                        ))
                        self.info_sitio['hotlinking_protegido'] = False
                    else:
                        self.info_sitio['hotlinking_protegido'] = True
                elif response_hotlink.status_code in [403, 401]:
                    self.info_sitio['hotlinking_protegido'] = True
        except:
            pass
    
    def verificar_proteccion_csrf(self):
        """Verifica si los formularios tienen protección CSRF"""
        self._registrar_mensaje("🛡️ Verificando protección CSRF en formularios...")
        
        # Páginas a verificar
        paginas_formularios = [
            (f"{self.dominio}/wp-login.php", "Login"),
            (f"{self.dominio}/wp-comments-post.php", "Comentarios"),
            (f"{self.dominio}/?page_id=", "Páginas"),
            (f"{self.dominio}/contacto/", "Contacto"),
            (f"{self.dominio}/contact/", "Contact"),
        ]
        
        formularios_sin_csrf = []
        formularios_analizados = 0
        
        response_principal = self._realizar_peticion(self.dominio)
        if response_principal:
            soup = BeautifulSoup(response_principal.text, 'html.parser')
            
            # Buscar todos los formularios en la página principal
            formularios = soup.find_all('form')
            
            for form in formularios:
                formularios_analizados += 1
                action = form.get('action', '')
                method_attr = form.get('method', 'get')
                method = str(method_attr).lower() if method_attr else 'get'
                
                # Solo nos preocupan los formularios POST
                if method == 'post':
                    # Buscar campos de token CSRF
                    tiene_csrf = False
                    
                    # Patrones comunes de tokens CSRF
                    patrones_csrf = [
                        'nonce',
                        '_wpnonce',
                        'csrf',
                        '_token',
                        'authenticity_token',
                        'security',
                        'verify',
                        '_csrf_token'
                    ]
                    
                    inputs = form.find_all('input', {'type': 'hidden'})
                    for inp in inputs:
                        nombre_attr = inp.get('name', '')
                        nombre = str(nombre_attr).lower() if nombre_attr else ''
                        if any(patron in nombre for patron in patrones_csrf):
                            tiene_csrf = True
                            break
                    
                    if not tiene_csrf:
                        form_id_attr = form.get('id')
                        if form_id_attr:
                            form_id = str(form_id_attr)
                        else:
                            form_class = form.get('class')
                            if form_class and isinstance(form_class, list) and len(form_class) > 0:
                                form_id = str(form_class[0])
                            else:
                                form_id = 'sin-id'
                        formularios_sin_csrf.append(f"Formulario '{form_id}' -> {action or 'misma página'}")
        
        # Verificar formulario de comentarios específicamente
        response_post = self._realizar_peticion(f"{self.dominio}/?p=1")
        if response_post and response_post.status_code == 200:
            if 'comment' in response_post.text.lower():
                soup = BeautifulSoup(response_post.text, 'html.parser')
                form_comentarios = soup.find('form', {'id': 'commentform'}) or soup.find('form', {'class': 'comment-form'})
                
                if form_comentarios:
                    formularios_analizados += 1
                    tiene_nonce = form_comentarios.find('input', {'name': re.compile(r'nonce|_wpnonce', re.I)})
                    if not tiene_nonce:
                        formularios_sin_csrf.append("Formulario de comentarios sin nonce")
        
        if formularios_sin_csrf:
            self.vulnerabilidades.append(Vulnerabilidad(
                nombre="Formularios sin protección CSRF",
                severidad=Severidad.MEDIA,
                descripcion=f"Se encontraron {len(formularios_sin_csrf)} formularios POST sin tokens de protección CSRF visibles.",
                explicacion_simple="Sin protección CSRF, un atacante puede engañar a tus usuarios para que envíen formularios sin su conocimiento, como cambiar su email o hacer compras.",
                recomendacion="Implementar tokens CSRF (nonce en WordPress) en todos los formularios. Usar plugins de seguridad que añadan esta protección automáticamente.",
                detalles="\n".join(formularios_sin_csrf[:5])  # Limitar a 5
            ))
            self.info_sitio['formularios_sin_csrf'] = len(formularios_sin_csrf)
        
        self.info_sitio['formularios_analizados'] = formularios_analizados
    
    def _verificar_sitio_existe(self) -> Tuple[bool, str]:
        """Verifica si el sitio web existe y es accesible"""
        try:
            # Primero intentar resolver el dominio
            parsed = urlparse(self.dominio)
            hostname = parsed.netloc or parsed.path
            socket.gethostbyname(hostname)
            
            # Luego intentar conectar
            response = self._realizar_peticion(self.dominio)
            if response is None:
                return False, f"No se puede conectar con {self.dominio_original}. El sitio no responde."
            
            if response.status_code >= 400:
                return False, f"El sitio {self.dominio_original} devolvió error {response.status_code}."
            
            return True, ""
            
        except socket.gaierror:
            return False, f"El dominio '{self.dominio_original}' no existe o no se puede resolver."
        except socket.timeout:
            return False, f"Tiempo de espera agotado al conectar con {self.dominio_original}."
        except Exception as e:
            return False, f"Error al verificar el sitio: {str(e)}"
    
    def ejecutar_escaneo_completo(self) -> Tuple[List[Vulnerabilidad], Dict]:
        """Ejecuta todos los análisis de seguridad"""
        self._registrar_mensaje("🚀 Iniciando escaneo de seguridad...")
        
        # Primero verificar si el sitio existe
        self._registrar_mensaje("🔍 Verificando que el sitio web existe...")
        sitio_existe, mensaje_error = self._verificar_sitio_existe()
        if not sitio_existe:
            self._registrar_mensaje(f"❌ {mensaje_error}")
            return [], {'error': mensaje_error, 'sitio_no_existe': True}
        
        self._registrar_mensaje("✅ Sitio web accesible")
        
        # Verificar si es WordPress
        if not self.verificar_es_wordpress():
            self._registrar_mensaje("⚠️ No se detectó WordPress en este sitio")
            return [], {'error': 'No se detectó WordPress en este sitio'}
        
        self._registrar_mensaje("✅ Sitio WordPress detectado")
        
        # Ejecutar todas las verificaciones
        verificaciones = [
            self.detectar_version_wordpress,
            self.verificar_ssl,
            self.verificar_xmlrpc,
            self.verificar_enumeracion_usuarios,
            self.verificar_wp_config_backup,
            self.verificar_debug_mode,
            self.verificar_listado_directorios,
            self.verificar_plugins_vulnerables,
            self.verificar_temas,
            self.verificar_login_seguridad,
            self.verificar_rest_api,
            self.verificar_cabeceras_seguridad,
            self.verificar_archivo_robots,
            # Nuevas verificaciones de seguridad
            self.verificar_malware_conocido,
            self.verificar_permisos_archivos,
            self.verificar_politica_contrasenas,
            self.verificar_hotlinking,
            self.verificar_proteccion_csrf,
        ]
        
        for verificacion in verificaciones:
            try:
                verificacion()
            except Exception as e:
                self._registrar_mensaje(f"⚠️ Error en {verificacion.__name__}: {str(e)}")
        
        # Ordenar vulnerabilidades por severidad
        orden_severidad = {
            Severidad.CRITICA: 0,
            Severidad.ALTA: 1,
            Severidad.MEDIA: 2,
            Severidad.BAJA: 3,
            Severidad.INFO: 4
        }
        self.vulnerabilidades.sort(key=lambda x: orden_severidad[x.severidad])
        
        self._registrar_mensaje("✅ Escaneo completado")
        
        return self.vulnerabilidades, self.info_sitio
