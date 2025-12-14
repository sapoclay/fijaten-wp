"""
Fijaten-WP - Detector de WAF (Web Application Firewall)
Detecta si el sitio está protegido por un firewall de aplicación web
"""

import requests
import re
from typing import Dict, Optional, List
from .modelos import Vulnerabilidad, Severidad


class DetectorWAF:
    """Detecta la presencia de WAF (Web Application Firewall)"""
    
    # Firmas de WAF conocidas
    FIRMAS_WAF = {
        'cloudflare': {
            'cabeceras': ['cf-ray', 'cf-cache-status', 'cf-request-id'],
            'cookies': ['__cfduid', '__cf_bm', 'cf_clearance'],
            'servidor': ['cloudflare'],
            'cuerpo': ['attention required! | cloudflare', 'cloudflare ray id'],
        },
        'sucuri': {
            'cabeceras': ['x-sucuri-id', 'x-sucuri-cache'],
            'cookies': ['sucuri_cloudproxy'],
            'servidor': ['sucuri'],
            'cuerpo': ['sucuri website firewall', 'access denied - sucuri'],
        },
        'wordfence': {
            'cabeceras': [],
            'cookies': ['wfwaf-authcookie'],
            'servidor': [],
            'cuerpo': ['blocked by wordfence', 'your access to this site has been limited', 'wordfence'],
        },
        'modsecurity': {
            'cabeceras': ['x-mod-security'],
            'cookies': [],
            'servidor': ['mod_security', 'modsecurity'],
            'cuerpo': ['mod_security', 'not acceptable', 'this request was blocked'],
        },
        'akamai': {
            'cabeceras': ['x-akamai-transformed', 'akamai-origin-hop'],
            'cookies': ['akamai_vcs'],
            'servidor': ['akamaighost'],
            'cuerpo': ['access denied', 'reference'],
        },
        'imperva': {
            'cabeceras': ['x-cdn', 'x-iinfo'],
            'cookies': ['incap_ses', 'visid_incap', 'nlbi_'],
            'servidor': ['incapsula'],
            'cuerpo': ['incapsula incident', 'powered by incapsula', '_incapsula_resource'],
        },
        'aws_waf': {
            'cabeceras': ['x-amzn-requestid', 'x-amz-cf-id'],
            'cookies': ['awsalb', 'awsalbcors'],
            'servidor': ['awselb'],
            'cuerpo': ['request blocked', 'aws'],
        },
        'f5_big_ip': {
            'cabeceras': ['x-cnection', 'x-wa-info'],
            'cookies': ['bigipserver', 'ts', 'f5_cspm'],
            'servidor': ['bigip', 'f5'],
            'cuerpo': ['the requested url was rejected'],
        },
        'barracuda': {
            'cabeceras': ['barra_counter_session'],
            'cookies': ['barra_counter_session', 'bni_persistence'],
            'servidor': ['barracuda'],
            'cuerpo': ['barracuda networks'],
        },
        'fortinet': {
            'cabeceras': [],
            'cookies': ['fortiwafsid'],
            'servidor': ['fortiweb'],
            'cuerpo': ['fortigate', 'fortinet', '.fgd_icon'],
        },
        'shield_security': {
            'cabeceras': [],
            'cookies': ['icwp_wpsf'],
            'servidor': [],
            'cuerpo': ['shield security', 'wp simple firewall'],
        },
        'all_in_one_security': {
            'cabeceras': [],
            'cookies': ['aios_', 'aiowps_'],
            'servidor': [],
            'cuerpo': ['all in one wp security'],
        },
        'ithemes_security': {
            'cabeceras': [],
            'cookies': ['itsec-hb-login-'],
            'servidor': [],
            'cuerpo': ['ithemes security'],
        },
    }
    
    # Payloads de prueba que normalmente disparan WAFs
    PAYLOADS_PRUEBA = [
        "?test=<script>alert('xss')</script>",
        "?id=1' OR '1'='1",
        "?file=../../../etc/passwd",
        "?cmd=;cat /etc/passwd",
    ]
    
    def __init__(self, session: requests.Session, timeout: int = 10):
        self.session = session
        self.timeout = timeout
    
    def _analizar_respuesta(self, response: requests.Response) -> List[str]:
        """Analiza una respuesta HTTP buscando firmas de WAF"""
        wafs_detectados = []
        
        if not response:
            return wafs_detectados
        
        cabeceras = {k.lower(): v.lower() for k, v in response.headers.items()}
        cookies = {k.lower(): v.lower() for k, v in response.cookies.items()}
        servidor = cabeceras.get('server', '').lower()
        cuerpo = response.text.lower()[:5000]  # Solo primeros 5000 caracteres
        
        for waf, firmas in self.FIRMAS_WAF.items():
            detectado = False
            
            # Verificar cabeceras
            for cabecera in firmas['cabeceras']:
                if cabecera.lower() in cabeceras:
                    detectado = True
                    break
            
            # Verificar cookies
            if not detectado:
                for cookie in firmas['cookies']:
                    if any(cookie.lower() in c for c in cookies.keys()):
                        detectado = True
                        break
            
            # Verificar servidor
            if not detectado:
                for srv in firmas['servidor']:
                    if srv.lower() in servidor:
                        detectado = True
                        break
            
            # Verificar cuerpo de respuesta
            if not detectado:
                for patron in firmas['cuerpo']:
                    if patron.lower() in cuerpo:
                        detectado = True
                        break
            
            if detectado:
                wafs_detectados.append(waf)
        
        return wafs_detectados
    
    def detectar_waf_basico(self, dominio: str) -> Dict:
        """Detecta WAF mediante análisis de respuesta normal"""
        resultado = {
            'waf_detectado': False,
            'wafs': [],
            'metodo': 'análisis pasivo'
        }
        
        try:
            response = self.session.get(dominio, timeout=self.timeout, verify=False)
            wafs = self._analizar_respuesta(response)
            
            if wafs:
                resultado['waf_detectado'] = True
                resultado['wafs'] = list(set(wafs))
        except Exception:
            pass
        
        return resultado
    
    def detectar_waf_activo(self, dominio: str) -> Dict:
        """
        Detecta WAF enviando payloads que normalmente son bloqueados
        NOTA: Este método es más agresivo y podría ser bloqueado
        """
        resultado = {
            'waf_detectado': False,
            'wafs': [],
            'metodo': 'análisis activo',
            'respuestas_bloqueadas': 0
        }
        
        wafs_encontrados = set()
        
        for payload in self.PAYLOADS_PRUEBA[:2]:  # Limitar a 2 pruebas
            try:
                url = f"{dominio.rstrip('/')}/{payload}"
                response = self.session.get(url, timeout=self.timeout, verify=False)
                
                # Códigos típicos de bloqueo de WAF
                if response.status_code in [403, 406, 429, 503]:
                    resultado['respuestas_bloqueadas'] += 1
                    wafs = self._analizar_respuesta(response)
                    wafs_encontrados.update(wafs)
                    
            except requests.exceptions.RequestException:
                # Conexión bloqueada = posible WAF
                resultado['respuestas_bloqueadas'] += 1
        
        if resultado['respuestas_bloqueadas'] > 0 or wafs_encontrados:
            resultado['waf_detectado'] = True
            resultado['wafs'] = list(wafs_encontrados) if wafs_encontrados else ['WAF desconocido']
        
        return resultado
    
    def obtener_info_waf(self, waf_nombre: str) -> Dict:
        """Obtiene información sobre un WAF específico"""
        info_wafs = {
            'cloudflare': {
                'nombre_completo': 'Cloudflare WAF',
                'tipo': 'CDN + WAF',
                'caracteristicas': ['Protección DDoS', 'SSL gratis', 'Caché global'],
                'es_plugin_wp': False
            },
            'sucuri': {
                'nombre_completo': 'Sucuri Website Firewall',
                'tipo': 'WAF Cloud',
                'caracteristicas': ['Limpieza de malware', 'Protección DDoS', 'CDN'],
                'es_plugin_wp': False
            },
            'wordfence': {
                'nombre_completo': 'Wordfence Security',
                'tipo': 'Plugin WordPress WAF',
                'caracteristicas': ['Firewall endpoint', 'Escáner malware', 'Login security'],
                'es_plugin_wp': True
            },
            'modsecurity': {
                'nombre_completo': 'ModSecurity',
                'tipo': 'WAF Servidor',
                'caracteristicas': ['Open source', 'Reglas OWASP', 'Nivel servidor'],
                'es_plugin_wp': False
            },
            'imperva': {
                'nombre_completo': 'Imperva Incapsula',
                'tipo': 'CDN + WAF Enterprise',
                'caracteristicas': ['WAF avanzado', 'Bot management', 'DDoS protection'],
                'es_plugin_wp': False
            },
            'shield_security': {
                'nombre_completo': 'Shield Security',
                'tipo': 'Plugin WordPress WAF',
                'caracteristicas': ['Firewall', 'Login protection', 'Audit trail'],
                'es_plugin_wp': True
            },
        }
        
        return info_wafs.get(waf_nombre.lower(), {
            'nombre_completo': waf_nombre,
            'tipo': 'WAF',
            'caracteristicas': [],
            'es_plugin_wp': False
        })
    
    def ejecutar_deteccion_completa(self, dominio: str) -> Dict:
        """Ejecuta detección completa de WAF"""
        # Primero análisis pasivo (no intrusivo)
        resultado_pasivo = self.detectar_waf_basico(dominio)
        
        # Solo hacer análisis activo si no se detectó nada
        if not resultado_pasivo['waf_detectado']:
            resultado_activo = self.detectar_waf_activo(dominio)
            if resultado_activo['waf_detectado']:
                return resultado_activo
        
        return resultado_pasivo
    
    def generar_vulnerabilidad_sin_waf(self) -> Vulnerabilidad:
        """Genera vulnerabilidad si no se detecta WAF"""
        return Vulnerabilidad(
            nombre="Sin WAF (Web Application Firewall) detectado",
            severidad=Severidad.MEDIA,
            descripcion="No se detectó ningún firewall de aplicación web protegiendo el sitio.",
            explicacion_simple="Tu sitio no tiene un 'guardia de seguridad' que bloquee ataques automáticos como inyecciones SQL o XSS. Esto te hace más vulnerable.",
            recomendacion="Instalar un WAF como Wordfence, Sucuri, o usar un CDN con WAF integrado como Cloudflare.",
            detalles="Un WAF puede bloquear el 90% de los ataques automatizados comunes.",
            cwe="CWE-693: Fallo en mecanismo de protección"
        )
    
    def generar_info_waf_detectado(self, resultado: Dict) -> Dict:
        """Genera información sobre el WAF detectado para el informe"""
        if not resultado.get('waf_detectado'):
            return {'protegido': False}
        
        wafs = resultado.get('wafs', [])
        info_wafs = []
        
        for waf in wafs:
            info = self.obtener_info_waf(waf)
            info_wafs.append(info)
        
        return {
            'protegido': True,
            'wafs_detectados': wafs,
            'info_detallada': info_wafs,
            'metodo_deteccion': resultado.get('metodo', 'desconocido')
        }
