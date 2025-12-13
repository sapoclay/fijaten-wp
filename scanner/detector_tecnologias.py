"""
Fijaten-WP - Detector de Tecnologías Web
Identifica el CMS, framework o tecnología utilizada por un sitio web
"""

import requests
import re
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup


class DetectorTecnologias:
    """Detecta la tecnología o CMS utilizado por un sitio web"""
    
    def __init__(self, session: requests.Session, timeout: int = 10):
        self.session = session
        self.timeout = timeout
    
    # Patrones de detección para diferentes CMS y tecnologías
    TECNOLOGIAS = {
        # CMS populares
        'WordPress': {
            'indicadores_html': ['/wp-content/', '/wp-includes/', '/wp-admin/', 'wp-json', 'WordPress'],
            'meta_generator': [r'WordPress\s*[\d.]*'],
            'cabeceras': ['x-powered-by: WordPress'],
            'rutas': ['/wp-login.php', '/wp-admin/'],
            'icono': '📝',
        },
        'Joomla': {
            'indicadores_html': ['/components/', '/modules/', '/templates/', 'Joomla!', '/media/jui/'],
            'meta_generator': [r'Joomla!?\s*[\d.]*'],
            'cabeceras': [],
            'rutas': ['/administrator/', '/components/'],
            'icono': '🔷',
        },
        'Drupal': {
            'indicadores_html': ['/sites/default/', '/sites/all/', 'Drupal', 'drupal.js', '/core/misc/drupal.js'],
            'meta_generator': [r'Drupal\s*[\d.]*'],
            'cabeceras': ['x-drupal-cache', 'x-generator: Drupal'],
            'rutas': ['/core/install.php', '/user/login'],
            'icono': '💧',
        },
        'Magento': {
            'indicadores_html': ['/skin/frontend/', '/js/mage/', 'Mage.Cookies', '/static/frontend/', 'Magento'],
            'meta_generator': [r'Magento'],
            'cabeceras': ['x-magento'],
            'rutas': ['/admin/', '/downloader/'],
            'icono': '🛒',
        },
        'PrestaShop': {
            'indicadores_html': ['/themes/default/', 'prestashop', '/modules/ps_', 'PrestaShop'],
            'meta_generator': [r'PrestaShop'],
            'cabeceras': [],
            'rutas': ['/admin/', '/modules/'],
            'icono': '🛍️',
        },
        'Shopify': {
            'indicadores_html': ['cdn.shopify.com', 'shopify', 'Shopify.theme', 'myshopify.com'],
            'meta_generator': [r'Shopify'],
            'cabeceras': ['x-shopify-stage'],
            'rutas': [],
            'icono': '🛒',
        },
        'Wix': {
            'indicadores_html': ['wix.com', 'wixstatic.com', '_wix_browser_sess', 'X-Wix'],
            'meta_generator': [r'Wix\.com'],
            'cabeceras': ['x-wix'],
            'rutas': [],
            'icono': '🎨',
        },
        'Squarespace': {
            'indicadores_html': ['squarespace.com', 'static.squarespace.com', 'squarespace-cdn'],
            'meta_generator': [r'Squarespace'],
            'cabeceras': [],
            'rutas': [],
            'icono': '◼️',
        },
        'Blogger': {
            'indicadores_html': ['blogger.com', 'blogspot.com', 'blogger.googleusercontent.com'],
            'meta_generator': [r'Blogger'],
            'cabeceras': [],
            'rutas': [],
            'icono': '📰',
        },
        'Ghost': {
            'indicadores_html': ['ghost.io', 'ghost-url', 'content/themes/casper'],
            'meta_generator': [r'Ghost\s*[\d.]*'],
            'cabeceras': ['x-ghost-cache-status'],
            'rutas': ['/ghost/'],
            'icono': '👻',
        },
        'Webflow': {
            'indicadores_html': ['webflow.com', 'wf-page', 'w-nav', 'webflow'],
            'meta_generator': [r'Webflow'],
            'cabeceras': [],
            'rutas': [],
            'icono': '🌊',
        },
        
        # Frameworks y lenguajes
        'Laravel': {
            'indicadores_html': ['laravel', 'csrf-token'],
            'meta_generator': [],
            'cabeceras': ['x-powered-by: Laravel'],
            'cookies': ['laravel_session', 'XSRF-TOKEN'],
            'rutas': [],
            'icono': '🔴',
        },
        'Django': {
            'indicadores_html': ['csrfmiddlewaretoken', 'django'],
            'meta_generator': [],
            'cabeceras': [],
            'cookies': ['csrftoken', 'sessionid'],
            'rutas': ['/admin/'],
            'icono': '🐍',
        },
        'Ruby on Rails': {
            'indicadores_html': ['rails', 'csrf-token', 'authenticity_token'],
            'meta_generator': [],
            'cabeceras': ['x-powered-by: Phusion Passenger', 'x-runtime'],
            'cookies': ['_session_id'],
            'rutas': [],
            'icono': '💎',
        },
        'ASP.NET': {
            'indicadores_html': ['__VIEWSTATE', '__EVENTVALIDATION', 'aspnetForm'],
            'meta_generator': [],
            'cabeceras': ['x-powered-by: ASP.NET', 'x-aspnet-version'],
            'cookies': ['ASP.NET_SessionId', '.ASPXAUTH'],
            'rutas': [],
            'icono': '🔷',
        },
        'Node.js/Express': {
            'indicadores_html': [],
            'meta_generator': [],
            'cabeceras': ['x-powered-by: Express'],
            'cookies': ['connect.sid'],
            'rutas': [],
            'icono': '🟢',
        },
        'Next.js': {
            'indicadores_html': ['__NEXT_DATA__', '_next/static', 'next.js'],
            'meta_generator': [],
            'cabeceras': ['x-nextjs-page', 'x-powered-by: Next.js'],
            'rutas': ['/_next/'],
            'icono': '▲',
        },
        'Nuxt.js': {
            'indicadores_html': ['__NUXT__', '_nuxt/', 'nuxt'],
            'meta_generator': [],
            'cabeceras': [],
            'rutas': ['/_nuxt/'],
            'icono': '💚',
        },
        'React': {
            'indicadores_html': ['react', 'data-reactroot', 'data-reactid', '__REACT_DEVTOOLS'],
            'meta_generator': [],
            'cabeceras': [],
            'rutas': [],
            'icono': '⚛️',
        },
        'Vue.js': {
            'indicadores_html': ['vue', 'data-v-', 'v-cloak', '__VUE__'],
            'meta_generator': [],
            'cabeceras': [],
            'rutas': [],
            'icono': '💚',
        },
        'Angular': {
            'indicadores_html': ['ng-version', 'ng-app', 'angular', '_ngcontent'],
            'meta_generator': [],
            'cabeceras': [],
            'rutas': [],
            'icono': '🔴',
        },
        
        # Servidores y plataformas
        'PHP': {
            'indicadores_html': ['.php'],
            'meta_generator': [],
            'cabeceras': ['x-powered-by: PHP'],
            'rutas': [],
            'icono': '🐘',
        },
        'Nginx': {
            'indicadores_html': [],
            'meta_generator': [],
            'cabeceras': ['server: nginx'],
            'rutas': [],
            'icono': '🟩',
        },
        'Apache': {
            'indicadores_html': [],
            'meta_generator': [],
            'cabeceras': ['server: Apache'],
            'rutas': [],
            'icono': '🪶',
        },
        'IIS': {
            'indicadores_html': [],
            'meta_generator': [],
            'cabeceras': ['server: Microsoft-IIS'],
            'rutas': [],
            'icono': '🪟',
        },
    }
    
    def detectar_tecnologia(self, dominio: str) -> Dict:
        """
        Detecta las tecnologías utilizadas por un sitio web
        
        Returns:
            Dict con información sobre las tecnologías detectadas
        """
        resultado = {
            'cms': None,
            'framework': None,
            'lenguaje': None,
            'servidor': None,
            'frontend': [],
            'otras': [],
            'detalles': []
        }
        
        try:
            response = self.session.get(dominio, timeout=self.timeout, verify=False)
            contenido = response.text.lower()
            cabeceras = {k.lower(): v.lower() for k, v in response.headers.items()}
            cookies = {k.lower(): v for k, v in response.cookies.items()}
            
            # Buscar meta generator
            soup = BeautifulSoup(response.text, 'html.parser')
            meta_generator = ""
            meta = soup.find('meta', attrs={'name': 'generator'})
            if meta:
                content = meta.get('content', '')
                if content:
                    # Puede ser string o lista, aseguramos que sea string
                    if isinstance(content, list):
                        content = content[0] if content else ''
                    meta_generator = str(content).lower()
            
            tecnologias_encontradas = []
            
            for nombre, patrones in self.TECNOLOGIAS.items():
                confianza = 0
                motivos = []
                
                # Verificar indicadores en HTML
                for indicador in patrones.get('indicadores_html', []):
                    if indicador.lower() in contenido:
                        confianza += 30
                        motivos.append(f"Indicador HTML: {indicador}")
                        break
                
                # Verificar meta generator
                for patron in patrones.get('meta_generator', []):
                    if re.search(patron, meta_generator, re.IGNORECASE):
                        confianza += 50
                        motivos.append("Meta generator")
                        break
                
                # Verificar cabeceras
                for cab in patrones.get('cabeceras', []):
                    cab_lower = cab.lower()
                    if ':' in cab_lower:
                        key, value = cab_lower.split(':', 1)
                        if key.strip() in cabeceras and value.strip() in cabeceras[key.strip()]:
                            confianza += 40
                            motivos.append(f"Cabecera: {cab}")
                    else:
                        for k in cabeceras:
                            if cab_lower in k or cab_lower in cabeceras[k]:
                                confianza += 40
                                motivos.append(f"Cabecera: {k}")
                                break
                
                # Verificar cookies
                for cookie in patrones.get('cookies', []):
                    if cookie.lower() in cookies:
                        confianza += 35
                        motivos.append(f"Cookie: {cookie}")
                        break
                
                if confianza >= 30:
                    tecnologias_encontradas.append({
                        'nombre': nombre,
                        'confianza': min(confianza, 100),
                        'motivos': motivos,
                        'icono': patrones.get('icono', '🔧')
                    })
            
            # Ordenar por confianza
            tecnologias_encontradas.sort(key=lambda x: x['confianza'], reverse=True)
            
            # Clasificar tecnologías
            cms_list = ['WordPress', 'Joomla', 'Drupal', 'Magento', 'PrestaShop', 
                       'Shopify', 'Wix', 'Squarespace', 'Blogger', 'Ghost', 'Webflow']
            framework_list = ['Laravel', 'Django', 'Ruby on Rails', 'ASP.NET', 
                            'Node.js/Express', 'Next.js', 'Nuxt.js']
            frontend_list = ['React', 'Vue.js', 'Angular']
            servidor_list = ['Nginx', 'Apache', 'IIS']
            lenguaje_list = ['PHP']
            
            for tech in tecnologias_encontradas:
                nombre = tech['nombre']
                detalle = f"{tech['icono']} {nombre} (confianza: {tech['confianza']}%)"
                
                if nombre in cms_list and not resultado['cms']:
                    resultado['cms'] = tech
                elif nombre in framework_list and not resultado['framework']:
                    resultado['framework'] = tech
                elif nombre in frontend_list:
                    resultado['frontend'].append(tech)
                elif nombre in servidor_list and not resultado['servidor']:
                    resultado['servidor'] = tech
                elif nombre in lenguaje_list and not resultado['lenguaje']:
                    resultado['lenguaje'] = tech
                else:
                    resultado['otras'].append(tech)
                
                resultado['detalles'].append(detalle)
            
            # Detectar servidor desde cabeceras si no se encontró
            if not resultado['servidor'] and 'server' in cabeceras:
                servidor = cabeceras['server']
                resultado['servidor'] = {
                    'nombre': servidor.split('/')[0].title(),
                    'confianza': 100,
                    'icono': '🖥️'
                }
                resultado['detalles'].append(f"🖥️ Servidor: {servidor}")
            
        except Exception as e:
            resultado['error'] = str(e)
        
        return resultado
    
    def generar_resumen(self, resultado: Dict) -> str:
        """Genera un resumen legible de las tecnologías detectadas"""
        lineas = []
        
        if resultado.get('cms'):
            cms = resultado['cms']
            lineas.append(f"📦 CMS: {cms['icono']} {cms['nombre']}")
        
        if resultado.get('framework'):
            fw = resultado['framework']
            lineas.append(f"🛠️ Framework: {fw['icono']} {fw['nombre']}")
        
        if resultado.get('lenguaje'):
            lang = resultado['lenguaje']
            lineas.append(f"💻 Lenguaje: {lang['icono']} {lang['nombre']}")
        
        if resultado.get('frontend'):
            frontends = [f"{f['icono']} {f['nombre']}" for f in resultado['frontend']]
            lineas.append(f"🎨 Frontend: {', '.join(frontends)}")
        
        if resultado.get('servidor'):
            srv = resultado['servidor']
            lineas.append(f"🖥️ Servidor: {srv.get('icono', '🖥️')} {srv['nombre']}")
        
        if resultado.get('otras'):
            otras = [f"{o['icono']} {o['nombre']}" for o in resultado['otras']]
            lineas.append(f"🔧 Otras: {', '.join(otras)}")
        
        if not lineas:
            lineas.append("❓ No se pudieron identificar tecnologías conocidas")
        
        return '\n'.join(lineas)
