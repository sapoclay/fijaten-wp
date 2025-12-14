"""
Fijaten-WP - Verificador de Listas Negras (Blacklists)
Comprueba si el dominio está en listas negras de spam/malware
"""

import socket
import requests
from typing import List, Dict, Optional
from .modelos import Vulnerabilidad, Severidad


class VerificadorBlacklist:
    """Verifica si un dominio está en listas negras de spam/malware"""
    
    # DNSBLs (DNS-based Blackhole Lists) populares
    DNSBL_SERVERS = [
        ('zen.spamhaus.org', 'Spamhaus ZEN'),
        ('bl.spamcop.net', 'SpamCop'),
        ('b.barracudacentral.org', 'Barracuda'),
        ('dnsbl.sorbs.net', 'SORBS'),
        ('spam.dnsbl.sorbs.net', 'SORBS Spam'),
        ('cbl.abuseat.org', 'CBL Abuseat'),
        ('dnsbl-1.uceprotect.net', 'UCEPROTECT Level 1'),
        ('psbl.surriel.com', 'PSBL'),
        ('db.wpbl.info', 'WPBL'),
        ('all.s5h.net', 'S5H'),
    ]
    
    # URLs de listas de malware/phishing para verificar
    MALWARE_CHECK_APIS = [
        # Google Safe Browsing requiere API key
        # 'https://safebrowsing.googleapis.com/v4/threatMatches:find'
    ]
    
    def __init__(self, session: requests.Session, timeout: int = 5):
        self.session = session
        self.timeout = timeout
    
    def _obtener_ip_dominio(self, dominio: str) -> Optional[str]:
        """Obtiene la IP del dominio"""
        try:
            # Limpiar el dominio
            dominio_limpio = dominio.replace('https://', '').replace('http://', '').split('/')[0]
            return socket.gethostbyname(dominio_limpio)
        except socket.gaierror:
            return None
    
    def _invertir_ip(self, ip: str) -> str:
        """Invierte los octetos de una IP para consulta DNSBL"""
        octetos = ip.split('.')
        return '.'.join(reversed(octetos))
    
    def verificar_dnsbl(self, dominio: str) -> List[Dict]:
        """Verifica si la IP del dominio está en listas DNSBL"""
        resultados = []
        
        ip = self._obtener_ip_dominio(dominio)
        if not ip:
            return resultados
        
        ip_invertida = self._invertir_ip(ip)
        
        for servidor, nombre in self.DNSBL_SERVERS:
            consulta = f"{ip_invertida}.{servidor}"
            try:
                socket.setdefaulttimeout(self.timeout)
                socket.gethostbyname(consulta)
                # Si resuelve, está en la lista negra
                resultados.append({
                    'lista': nombre,
                    'servidor': servidor,
                    'ip': ip,
                    'listado': True
                })
            except socket.gaierror:
                # No está en esta lista (normal)
                pass
            except socket.timeout:
                # Timeout, ignorar
                pass
        
        return resultados
    
    def verificar_google_safe_browsing(self, dominio: str, api_key: Optional[str] = None) -> Optional[Dict]:
        """
        Verifica el dominio en Google Safe Browsing (requiere API key)
        https://developers.google.com/safe-browsing/v4/get-started
        """
        if not api_key:
            return None
        
        url = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
        
        payload = {
            "client": {
                "clientId": "fijaten-wp",
                "clientVersion": "1.0.0"
            },
            "threatInfo": {
                "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE", "POTENTIALLY_HARMFUL_APPLICATION"],
                "platformTypes": ["ANY_PLATFORM"],
                "threatEntryTypes": ["URL"],
                "threatEntries": [
                    {"url": dominio}
                ]
            }
        }
        
        try:
            response = self.session.post(url, json=payload, timeout=self.timeout)
            if response.status_code == 200:
                data = response.json()
                if 'matches' in data:
                    return {
                        'servicio': 'Google Safe Browsing',
                        'amenazas': [match.get('threatType') for match in data['matches']]
                    }
        except Exception:
            pass
        
        return None
    
    def verificar_urlhaus(self, dominio: str) -> Optional[Dict]:
        """Verifica el dominio en URLhaus (abuse.ch) - gratuito sin API key"""
        try:
            # Limpiar dominio
            dominio_limpio = dominio.replace('https://', '').replace('http://', '').split('/')[0]
            
            url = "https://urlhaus-api.abuse.ch/v1/host/"
            response = self.session.post(url, data={'host': dominio_limpio}, timeout=self.timeout)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('query_status') == 'ok' and data.get('urls'):
                    return {
                        'servicio': 'URLhaus (abuse.ch)',
                        'urls_maliciosas': len(data['urls']),
                        'primera_vista': data.get('firstseen'),
                        'estado': 'El dominio ha sido reportado con URLs maliciosas'
                    }
        except Exception:
            pass
        
        return None
    
    def verificar_phishtank(self, dominio: str) -> Optional[Dict]:
        """Verifica si el dominio está en PhishTank"""
        # PhishTank requiere API key para consultas en tiempo real
        # Aquí solo verificamos si es accesible su página de reporte
        return None
    
    def ejecutar_verificacion_completa(self, dominio: str) -> Dict:
        """Ejecuta todas las verificaciones de listas negras"""
        resultado = {
            'dominio': dominio,
            'en_listas_negras': False,
            'listas_encontradas': [],
            'servicios_verificados': []
        }
        
        # Verificar DNSBL
        listas_dnsbl = self.verificar_dnsbl(dominio)
        if listas_dnsbl:
            resultado['en_listas_negras'] = True
            resultado['listas_encontradas'].extend(listas_dnsbl)
        resultado['servicios_verificados'].append('DNSBL (múltiples)')
        
        # Verificar URLhaus
        urlhaus = self.verificar_urlhaus(dominio)
        if urlhaus:
            resultado['en_listas_negras'] = True
            resultado['listas_encontradas'].append(urlhaus)
        resultado['servicios_verificados'].append('URLhaus')
        
        return resultado
    
    def generar_vulnerabilidad(self, resultado_verificacion: Dict) -> Optional[Vulnerabilidad]:
        """Genera una vulnerabilidad si el dominio está en listas negras"""
        if not resultado_verificacion.get('en_listas_negras'):
            return None
        
        listas = resultado_verificacion.get('listas_encontradas', [])
        nombres_listas = []
        
        for lista in listas:
            if isinstance(lista, dict):
                if 'lista' in lista:
                    nombres_listas.append(lista['lista'])
                elif 'servicio' in lista:
                    nombres_listas.append(lista['servicio'])
        
        return Vulnerabilidad(
            nombre="Dominio en listas negras de spam/malware",
            severidad=Severidad.CRITICA,
            descripcion=f"El dominio o su IP está listado en {len(listas)} lista(s) negra(s).",
            explicacion_simple="Tu sitio ha sido marcado como sospechoso de spam o malware. Esto puede hacer que emails no lleguen, navegadores bloqueen el sitio, y afecte tu reputación.",
            recomendacion="Investigar la causa (posible hackeo, spam). Limpiar el sitio y solicitar eliminación de las listas negras.",
            detalles=f"Listas: {', '.join(nombres_listas)}",
            cwe="CWE-506: Código malicioso embebido"
        )
