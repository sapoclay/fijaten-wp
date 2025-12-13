"""
Fijaten-WP - Verificador de CVEs
Consulta bases de datos de vulnerabilidades conocidas para plugins y temas
Incluye enlaces a NVD, MITRE y búsqueda de CPEs
"""

import requests
import re
import urllib3
from typing import List, Dict, Optional, Tuple
from .modelos import Vulnerabilidad, Severidad

# Suprimir warnings de SSL para peticiones sin verificación
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class VerificadorCVE:
    """Verifica vulnerabilidades conocidas (CVEs) en plugins y temas"""
    
    # URLs oficiales para consultar CVEs
    URL_NVD = "https://nvd.nist.gov/vuln/detail/"
    URL_MITRE = "https://cve.mitre.org/cgi-bin/cvename.cgi?name="
    URL_NVD_SEARCH = "https://nvd.nist.gov/vuln/search#/nvd/home"
    URL_NVD_API = "https://services.nvd.nist.gov/rest/json/cves/2.0"
    URL_WPSCAN = "https://wpscan.com/?s="
    URL_PATCHSTACK = "https://patchstack.com/database/?s="
    URL_EXPLOIT_DB = "https://www.exploit-db.com/search?q="
    
    # Base de datos local de plugins vulnerables conocidos
    PLUGINS_VULNERABLES = {
        'contact-form-7': {
            'versiones_afectadas': ['<5.3.2'],
            'cve': 'CVE-2020-35489',
            'descripcion': 'Vulnerabilidad de carga de archivos sin restricción',
            'severidad': Severidad.CRITICA,
            'cvss': 10.0,
            'cpe': 'cpe:2.3:a:rocklobster:contact_form_7:*:*:*:*:*:wordpress:*:*'
        },
        'elementor': {
            'versiones_afectadas': ['<3.1.4'],
            'cve': 'CVE-2021-24226',
            'descripcion': 'Vulnerabilidad XSS almacenado',
            'severidad': Severidad.ALTA,
            'cvss': 6.1,
            'cpe': 'cpe:2.3:a:elementor:elementor:*:*:*:*:*:wordpress:*:*'
        },
        'wpforms-lite': {
            'versiones_afectadas': ['<1.6.6'],
            'cve': 'CVE-2021-24145',
            'descripcion': 'Vulnerabilidad CSRF',
            'severidad': Severidad.MEDIA,
            'cvss': 4.3,
            'cpe': 'cpe:2.3:a:wpforms:wpforms:*:*:*:*:lite:wordpress:*:*'
        },
        'yoast-seo': {
            'versiones_afectadas': ['<15.1'],
            'cve': 'CVE-2021-25032',
            'descripcion': 'Vulnerabilidad de inyección SQL',
            'severidad': Severidad.CRITICA,
            'cvss': 9.8,
            'cpe': 'cpe:2.3:a:yoast:yoast_seo:*:*:*:*:*:wordpress:*:*'
        },
        'woocommerce': {
            'versiones_afectadas': ['<5.5.1'],
            'cve': 'CVE-2021-32789',
            'descripcion': 'Vulnerabilidad de inyección SQL',
            'severidad': Severidad.CRITICA,
            'cvss': 7.5,
            'cpe': 'cpe:2.3:a:woocommerce:woocommerce:*:*:*:*:*:wordpress:*:*'
        },
        'wordfence': {
            'versiones_afectadas': ['<7.5.3'],
            'cve': 'CVE-2021-24290',
            'descripcion': 'Bypass de autenticación',
            'severidad': Severidad.ALTA,
            'cvss': 7.5,
            'cpe': 'cpe:2.3:a:wordfence:wordfence:*:*:*:*:*:wordpress:*:*'
        },
        'all-in-one-wp-migration': {
            'versiones_afectadas': ['<7.41'],
            'cve': 'CVE-2021-24130',
            'descripcion': 'Vulnerabilidad de path traversal',
            'severidad': Severidad.ALTA,
            'cvss': 6.5,
            'cpe': 'cpe:2.3:a:servmask:all-in-one_wp_migration:*:*:*:*:*:wordpress:*:*'
        },
        'duplicator': {
            'versiones_afectadas': ['<1.4.7'],
            'cve': 'CVE-2020-11738',
            'descripcion': 'Lectura arbitraria de archivos',
            'severidad': Severidad.CRITICA,
            'cvss': 7.5,
            'cpe': 'cpe:2.3:a:snapcreek:duplicator:*:*:*:*:*:wordpress:*:*'
        },
        'updraftplus': {
            'versiones_afectadas': ['<1.22.3'],
            'cve': 'CVE-2022-0633',
            'descripcion': 'Descarga de backups sin autenticación',
            'severidad': Severidad.CRITICA,
            'cvss': 8.5,
            'cpe': 'cpe:2.3:a:updraftplus:updraftplus:*:*:*:*:*:wordpress:*:*'
        },
        'wp-file-manager': {
            'versiones_afectadas': ['<6.9'],
            'cve': 'CVE-2020-25213',
            'descripcion': 'Ejecución remota de código',
            'severidad': Severidad.CRITICA,
            'cvss': 10.0,
            'cpe': 'cpe:2.3:a:developer:file_manager:*:*:*:*:*:wordpress:*:*'
        },
        'revslider': {
            'versiones_afectadas': ['<6.2.23'],
            'cve': 'CVE-2021-24349',
            'descripcion': 'Inyección SQL sin autenticación',
            'severidad': Severidad.CRITICA,
            'cvss': 9.8,
            'cpe': 'cpe:2.3:a:themepunch:slider_revolution:*:*:*:*:*:wordpress:*:*'
        },
        'jetpack': {
            'versiones_afectadas': ['<9.8'],
            'cve': 'CVE-2021-24374',
            'descripcion': 'Vulnerabilidad XSS',
            'severidad': Severidad.MEDIA,
            'cvss': 5.4,
            'cpe': 'cpe:2.3:a:automattic:jetpack:*:*:*:*:*:wordpress:*:*'
        },
    }
    
    # Temas vulnerables conocidos
    TEMAS_VULNERABLES = {
        'flavor': {
            'versiones_afectadas': ['<1.1.1'],
            'cve': 'CVE-2021-24569',
            'descripcion': 'Inyección SQL sin autenticación',
            'severidad': Severidad.CRITICA,
            'cvss': 9.8,
            'cpe': 'cpe:2.3:a:flavor_theme_project:flavor:*:*:*:*:*:wordpress:*:*'
        },
        'flavor-flavor': {
            'versiones_afectadas': ['<1.5.6'],
            'cve': 'CVE-2020-11515',
            'descripcion': 'Redirección abierta',
            'severidad': Severidad.MEDIA,
            'cvss': 6.1,
            'cpe': None
        },
    }
    
    def __init__(self, session: requests.Session, timeout: int = 10):
        self.session = session
        self.timeout = timeout
    
    def generar_enlace_cve(self, cve_id: str) -> Dict[str, str]:
        """Genera enlaces a páginas oficiales para un CVE"""
        cve_id = cve_id.upper().strip()
        return {
            'nvd': f"{self.URL_NVD}{cve_id}",
            'mitre': f"{self.URL_MITRE}{cve_id}",
            'cve_id': cve_id
        }
    
    def generar_enlace_cpe(self, cpe: Optional[str], nombre_producto: str = "") -> Dict[str, str]:
        """Genera enlaces útiles para buscar vulnerabilidades de un producto"""
        enlaces = {}
        
        if nombre_producto:
            # Normalizar nombre del producto para búsqueda
            nombre_busqueda = nombre_producto.replace('-', '+').replace('_', '+')
            
            # Enlace a WPScan (base de datos especializada en WordPress)
            enlaces['wpscan'] = f"{self.URL_WPSCAN}{nombre_busqueda}"
            
            # Enlace a Patchstack (otra base de datos de WordPress)
            enlaces['patchstack'] = f"{self.URL_PATCHSTACK}{nombre_producto}"
            
            # Enlace a búsqueda en NVD por nombre del producto (con comillas para búsqueda exacta)
            enlaces['nvd_search'] = f"{self.URL_NVD_SEARCH}?keyword=%22{nombre_producto}%22&resultType={nombre_producto}"
            
            # Enlace a Exploit-DB
            enlaces['exploit_db'] = f"{self.URL_EXPLOIT_DB}wordpress+{nombre_busqueda}"
        
        return enlaces
    
    def buscar_cpe_wordpress(self, nombre_componente: str, tipo: str = 'plugin') -> Optional[str]:
        """
        Genera un CPE para un componente de WordPress
        Formato CPE 2.3: cpe:2.3:a:vendor:product:version:*:*:*:*:wordpress:*:*
        """
        nombre_normalizado = nombre_componente.lower().replace('-', '_').replace(' ', '_')
        # CPE genérico para plugins/temas de WordPress
        return f"cpe:2.3:a:*:{nombre_normalizado}:*:*:*:*:*:wordpress:*:*"
    
    def consultar_nvd_api(self, cve_id: str) -> Optional[Dict]:
        """
        Consulta la API pública de NVD para obtener información detallada de un CVE
        Nota: La API pública tiene límite de peticiones (5 por cada 30 segundos sin API key)
        """
        try:
            url = f"{self.URL_NVD_API}?cveId={cve_id}"
            headers = {
                'User-Agent': 'Fijaten-WP Security Scanner/1.0'
            }
            
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('vulnerabilities') and len(data['vulnerabilities']) > 0:
                    vuln_data = data['vulnerabilities'][0]['cve']
                    
                    # Extraer información relevante
                    resultado = {
                        'cve_id': vuln_data.get('id'),
                        'descripcion': '',
                        'cvss_v3': None,
                        'cvss_v2': None,
                        'cpes': [],
                        'referencias': [],
                        'publicado': vuln_data.get('published'),
                        'modificado': vuln_data.get('lastModified')
                    }
                    
                    # Descripción
                    descripciones = vuln_data.get('descriptions', [])
                    for desc in descripciones:
                        if desc.get('lang') == 'es':
                            resultado['descripcion'] = desc.get('value', '')
                            break
                        elif desc.get('lang') == 'en':
                            resultado['descripcion'] = desc.get('value', '')
                    
                    # Métricas CVSS
                    metrics = vuln_data.get('metrics', {})
                    if 'cvssMetricV31' in metrics:
                        resultado['cvss_v3'] = metrics['cvssMetricV31'][0]['cvssData']['baseScore']
                    elif 'cvssMetricV30' in metrics:
                        resultado['cvss_v3'] = metrics['cvssMetricV30'][0]['cvssData']['baseScore']
                    if 'cvssMetricV2' in metrics:
                        resultado['cvss_v2'] = metrics['cvssMetricV2'][0]['cvssData']['baseScore']
                    
                    # CPEs afectados
                    configurations = vuln_data.get('configurations', [])
                    for config in configurations:
                        for node in config.get('nodes', []):
                            for cpe_match in node.get('cpeMatch', []):
                                if cpe_match.get('vulnerable'):
                                    resultado['cpes'].append(cpe_match.get('criteria'))
                    
                    # Referencias
                    referencias = vuln_data.get('references', [])
                    for ref in referencias[:5]:  # Limitar a 5 referencias
                        resultado['referencias'].append({
                            'url': ref.get('url'),
                            'fuente': ref.get('source')
                        })
                    
                    return resultado
                    
        except Exception:
            pass
        
        return None

    def _comparar_versiones(self, version_actual: str, version_afectada: str) -> bool:
        """Compara si la versión actual es vulnerable según el patrón"""
        if not version_actual:
            return False
        
        try:
            # Parsear el patrón (ej: '<5.3.2', '<=3.0', '>=2.0,<3.0')
            if version_afectada.startswith('<'):
                version_limite = version_afectada.lstrip('<').lstrip('=')
                partes_actual = [int(x) for x in version_actual.split('.')[:3]]
                partes_limite = [int(x) for x in version_limite.split('.')[:3]]
                
                # Rellenar con ceros
                while len(partes_actual) < 3:
                    partes_actual.append(0)
                while len(partes_limite) < 3:
                    partes_limite.append(0)
                
                return partes_actual < partes_limite
        except (ValueError, AttributeError):
            pass
        
        return False
    
    def verificar_plugin(self, nombre_plugin: str, version: Optional[str]) -> Optional[Dict]:
        """Verifica si un plugin específico tiene vulnerabilidades conocidas"""
        nombre_normalizado = nombre_plugin.lower().replace('_', '-')
        
        if nombre_normalizado in self.PLUGINS_VULNERABLES:
            info_vuln = self.PLUGINS_VULNERABLES[nombre_normalizado]
            cve_id = info_vuln['cve']
            enlaces = self.generar_enlace_cve(cve_id)
            cpe = info_vuln.get('cpe')
            
            # Generar enlaces de búsqueda útiles
            enlaces_busqueda = self.generar_enlace_cpe(cpe, nombre_plugin)
            
            resultado_base = {
                'plugin': nombre_plugin,
                'cve': cve_id,
                'descripcion': info_vuln['descripcion'],
                'severidad': info_vuln['severidad'],
                'cvss': info_vuln.get('cvss', 0.0),
                'enlaces': enlaces,
                'url_nvd': enlaces['nvd'],
                'url_mitre': enlaces['mitre'],
                'cpe': cpe,
                'url_wpscan': enlaces_busqueda.get('wpscan', ''),
                'url_patchstack': enlaces_busqueda.get('patchstack', ''),
                'url_nvd_search': enlaces_busqueda.get('nvd_search', ''),
                'url_exploit_db': enlaces_busqueda.get('exploit_db', '')
            }
            
            # Si no hay versión, asumimos que podría ser vulnerable
            if not version:
                resultado_base.update({
                    'version_detectada': 'desconocida',
                    'nota': 'No se pudo determinar la versión - verificar manualmente'
                })
                return resultado_base
            
            # Verificar si la versión es vulnerable
            for version_afectada in info_vuln['versiones_afectadas']:
                if self._comparar_versiones(version, version_afectada):
                    resultado_base.update({
                        'version_detectada': version,
                        'version_segura': version_afectada.lstrip('<').lstrip('=')
                    })
                    return resultado_base
        
        return None
    
    def verificar_tema(self, nombre_tema: str, version: Optional[str]) -> Optional[Dict]:
        """Verifica si un tema tiene vulnerabilidades conocidas"""
        nombre_normalizado = nombre_tema.lower().replace('_', '-')
        
        if nombre_normalizado in self.TEMAS_VULNERABLES:
            info_vuln = self.TEMAS_VULNERABLES[nombre_normalizado]
            cve_id = info_vuln['cve']
            enlaces = self.generar_enlace_cve(cve_id)
            cpe = info_vuln.get('cpe')
            
            # Generar enlaces de búsqueda útiles
            enlaces_busqueda = self.generar_enlace_cpe(cpe, nombre_tema)
            
            resultado_base = {
                'tema': nombre_tema,
                'cve': cve_id,
                'descripcion': info_vuln['descripcion'],
                'severidad': info_vuln['severidad'],
                'cvss': info_vuln.get('cvss', 0.0),
                'enlaces': enlaces,
                'url_nvd': enlaces['nvd'],
                'url_mitre': enlaces['mitre'],
                'cpe': cpe,
                'url_wpscan': enlaces_busqueda.get('wpscan', ''),
                'url_patchstack': enlaces_busqueda.get('patchstack', ''),
                'url_nvd_search': enlaces_busqueda.get('nvd_search', ''),
                'url_exploit_db': enlaces_busqueda.get('exploit_db', '')
            }
            
            if not version:
                resultado_base['version_detectada'] = 'desconocida'
                return resultado_base
            
            for version_afectada in info_vuln['versiones_afectadas']:
                if self._comparar_versiones(version, version_afectada):
                    resultado_base['version_detectada'] = version
                    return resultado_base
        
        return None
    
    def consultar_wpscan_api(self, plugins: List[Tuple[str, str]], api_key: Optional[str] = None) -> List[Dict]:
        """
        Consulta la API de WPScan para vulnerabilidades (requiere API key gratuita)
        https://wpscan.com/api
        """
        vulnerabilidades = []
        
        if not api_key:
            # Sin API key, usar solo base de datos local
            for nombre, version in plugins:
                resultado = self.verificar_plugin(nombre, version)
                if resultado:
                    vulnerabilidades.append(resultado)
            return vulnerabilidades
        
        # Con API key, consultar WPScan
        headers = {'Authorization': f'Token token={api_key}'}
        
        for nombre, version in plugins:
            try:
                url = f"https://wpscan.com/api/v3/plugins/{nombre}"
                response = self.session.get(url, headers=headers, timeout=self.timeout)
                
                if response.status_code == 200:
                    data = response.json()
                    if nombre in data and 'vulnerabilities' in data[nombre]:
                        for vuln in data[nombre]['vulnerabilities']:
                            vulnerabilidades.append({
                                'plugin': nombre,
                                'cve': vuln.get('references', {}).get('cve', ['N/A'])[0],
                                'descripcion': vuln.get('title', 'Vulnerabilidad conocida'),
                                'severidad': Severidad.ALTA,
                                'version_detectada': version
                            })
            except Exception:
                # Fallar silenciosamente y continuar con el siguiente
                pass
        
        return vulnerabilidades
    
    def generar_vulnerabilidades(self, plugins_detectados: List[Tuple[str, Optional[str]]], 
                                  tema_activo: Optional[Tuple[str, Optional[str]]] = None) -> List[Vulnerabilidad]:
        """Genera lista de vulnerabilidades encontradas con enlaces a fuentes oficiales"""
        vulnerabilidades = []
        
        # Verificar plugins
        for nombre, version in plugins_detectados:
            resultado = self.verificar_plugin(nombre, version)
            if resultado:
                # Construir detalles con enlaces
                cvss_score = resultado.get('cvss', 0.0)
                cvss_texto = self._formatear_cvss(cvss_score)
                
                detalles = f"Versión detectada: {resultado['version_detectada']}\n"
                detalles += f"\n📊 PUNTUACIÓN CVSS: {cvss_texto}\n\n"
                detalles += "📎 ENLACES OFICIALES DEL CVE:\n"
                detalles += f"  • NVD: {resultado.get('url_nvd', 'N/A')}\n"
                detalles += f"  • MITRE: {resultado.get('url_mitre', 'N/A')}\n"
                
                # Añadir enlaces de búsqueda más útiles
                nombre_plugin = resultado['plugin']
                detalles += f"\n🔍 BUSCAR MÁS VULNERABILIDADES DE '{nombre_plugin.upper()}':\n"
                if resultado.get('url_wpscan'):
                    detalles += f"  • WPScan: {resultado['url_wpscan']}\n"
                if resultado.get('url_patchstack'):
                    detalles += f"  • Patchstack: {resultado['url_patchstack']}\n"
                if resultado.get('url_nvd_search'):
                    detalles += f"  • NVD Search: {resultado['url_nvd_search']}\n"
                
                vulnerabilidades.append(Vulnerabilidad(
                    nombre=f"CVE conocido en plugin: {resultado['plugin']}",
                    severidad=resultado['severidad'],
                    descripcion=f"{resultado['cve']} (CVSS: {cvss_score}): {resultado['descripcion']}",
                    explicacion_simple=f"El plugin {resultado['plugin']} tiene una vulnerabilidad de seguridad conocida ({resultado['cve']}) con puntuación CVSS {cvss_score}/10. Consulta los enlaces en los detalles para más información.",
                    recomendacion=f"Actualizar {resultado['plugin']} a la versión más reciente inmediatamente. Consulta {resultado.get('url_nvd', '')} para información detallada.",
                    detalles=detalles,
                    cwe=f"{resultado['cve']}"
                ))
        
        # Verificar tema
        if tema_activo:
            nombre_tema, version_tema = tema_activo
            resultado = self.verificar_tema(nombre_tema, version_tema)
            if resultado:
                # Construir detalles con enlaces
                cvss_score = resultado.get('cvss', 0.0)
                cvss_texto = self._formatear_cvss(cvss_score)
                
                detalles = f"Versión detectada: {resultado['version_detectada']}\n"
                detalles += f"\n📊 PUNTUACIÓN CVSS: {cvss_texto}\n\n"
                detalles += "📎 ENLACES OFICIALES DEL CVE:\n"
                detalles += f"  • NVD: {resultado.get('url_nvd', 'N/A')}\n"
                detalles += f"  • MITRE: {resultado.get('url_mitre', 'N/A')}\n"
                
                # Añadir enlaces de búsqueda más útiles
                nombre_tema_display = resultado['tema']
                detalles += f"\n🔍 BUSCAR MÁS VULNERABILIDADES DE '{nombre_tema_display.upper()}':\n"
                if resultado.get('url_wpscan'):
                    detalles += f"  • WPScan: {resultado['url_wpscan']}\n"
                if resultado.get('url_patchstack'):
                    detalles += f"  • Patchstack: {resultado['url_patchstack']}\n"
                if resultado.get('url_nvd_search'):
                    detalles += f"  • NVD Search: {resultado['url_nvd_search']}\n"
                
                vulnerabilidades.append(Vulnerabilidad(
                    nombre=f"CVE conocido en tema: {resultado['tema']}",
                    severidad=resultado['severidad'],
                    descripcion=f"{resultado['cve']} (CVSS: {cvss_score}): {resultado['descripcion']}",
                    explicacion_simple=f"El tema {resultado['tema']} tiene una vulnerabilidad de seguridad conocida ({resultado['cve']}) con puntuación CVSS {cvss_score}/10. Consulta los enlaces en los detalles para más información.",
                    recomendacion=f"Actualizar el tema a la versión más reciente o cambiar a otro tema. Consulta {resultado.get('url_nvd', '')} para información detallada.",
                    detalles=detalles,
                    cwe=f"{resultado['cve']}"
                ))
        
        return vulnerabilidades
    
    def _formatear_cvss(self, cvss: float) -> str:
        """Formatea la puntuación CVSS con indicador de severidad"""
        if cvss >= 9.0:
            return f"{cvss}/10 🔴 (Crítica)"
        elif cvss >= 7.0:
            return f"{cvss}/10 🟠 (Alta)"
        elif cvss >= 4.0:
            return f"{cvss}/10 🟡 (Media)"
        elif cvss > 0:
            return f"{cvss}/10 🟢 (Baja)"
        else:
            return "No disponible"
