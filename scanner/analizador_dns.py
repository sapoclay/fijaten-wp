"""
Fijaten-WP - Analizador DNS/WHOIS
Obtiene información adicional del dominio
"""

import socket
import re
import requests
from typing import Dict, Optional, List
from .modelos import Vulnerabilidad, Severidad, InfoDNS, InfoWHOIS

class AnalizadorDNS:
    """Analiza la configuración DNS y WHOIS de un dominio"""
    
    def __init__(self, session: requests.Session, timeout: int = 10):
        self.session = session
        self.timeout = timeout
    
    def _limpiar_dominio(self, dominio: str) -> str:
        """Limpia el dominio de protocolo y path"""
        dominio = dominio.replace('https://', '').replace('http://', '')
        dominio = dominio.split('/')[0]
        dominio = dominio.split(':')[0]  # Quitar puerto si existe
        return dominio
    
    def obtener_registros_dns(self, dominio: str) -> InfoDNS:
        """Obtiene los registros DNS básicos del dominio"""
        dominio_limpio = self._limpiar_dominio(dominio)
        info = InfoDNS()
        
        # Registro A (IPv4)
        try:
            ips = socket.gethostbyname_ex(dominio_limpio)
            info.registros_a = ips[2] if ips else []
        except socket.gaierror:
            pass
        
        # Para registros MX, NS, TXT necesitamos dnspython o una API
        # Usamos una API pública gratuita como alternativa
        try:
            # API de dns.google.com (gratuita)
            response = self.session.get(
                f"https://dns.google/resolve?name={dominio_limpio}&type=MX",
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if 'Answer' in data:
                    info.registros_mx = [ans.get('data', '') for ans in data['Answer']]
        except Exception:
            pass
        
        try:
            response = self.session.get(
                f"https://dns.google/resolve?name={dominio_limpio}&type=NS",
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if 'Answer' in data:
                    info.registros_ns = [ans.get('data', '').rstrip('.') for ans in data['Answer']]
        except Exception:
            pass
        
        try:
            response = self.session.get(
                f"https://dns.google/resolve?name={dominio_limpio}&type=TXT",
                timeout=self.timeout
            )
            if response.status_code == 200:
                data = response.json()
                if 'Answer' in data:
                    info.registros_txt = [ans.get('data', '').strip('"') for ans in data['Answer']]
        except Exception:
            pass
        
        return info
    
    def obtener_info_whois(self, dominio: str) -> InfoWHOIS:
        """Obtiene información WHOIS del dominio usando APIs públicas"""
        dominio_limpio = self._limpiar_dominio(dominio)
        info = InfoWHOIS()
        
        # Usar API pública de whois (hay varias opciones)
        apis_whois = [
            f"https://www.whoisxmlapi.com/whoisserver/WhoisService?domainName={dominio_limpio}&outputFormat=JSON",
            # Esta API requiere registro pero tiene tier gratuito
        ]
        
        # Intentar obtener WHOIS básico mediante socket (puerto 43)
        try:
            # Determinar servidor WHOIS según TLD
            tld = dominio_limpio.split('.')[-1].lower()
            servidores_whois = {
                'com': 'whois.verisign-grs.com',
                'net': 'whois.verisign-grs.com',
                'org': 'whois.pir.org',
                'es': 'whois.nic.es',
                'io': 'whois.nic.io',
                'dev': 'whois.nic.google',
                'app': 'whois.nic.google',
            }
            
            servidor = servidores_whois.get(tld, f'whois.nic.{tld}')
            
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            sock.connect((servidor, 43))
            sock.send((dominio_limpio + "\r\n").encode())
            
            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
            sock.close()
            
            whois_text = response.decode('utf-8', errors='ignore')
            
            # Parsear información básica
            # Registrador
            match = re.search(r'Registrar:\s*(.+)', whois_text, re.IGNORECASE)
            if match:
                info.registrador = match.group(1).strip()
            
            # Fecha de creación
            match = re.search(r'Creation Date:\s*(.+)', whois_text, re.IGNORECASE)
            if not match:
                match = re.search(r'Created:\s*(.+)', whois_text, re.IGNORECASE)
            if match:
                info.fecha_creacion = match.group(1).strip()[:10]
            
            # Fecha de expiración
            match = re.search(r'Expir\w+ Date:\s*(.+)', whois_text, re.IGNORECASE)
            if not match:
                match = re.search(r'Expiry Date:\s*(.+)', whois_text, re.IGNORECASE)
            if match:
                info.fecha_expiracion = match.group(1).strip()[:10]
            
            # Nameservers
            matches = re.findall(r'Name Server:\s*(.+)', whois_text, re.IGNORECASE)
            if matches:
                info.nameservers = [ns.strip().lower() for ns in matches[:4]]
                
        except Exception:
            pass
        
        return info
    
    def detectar_cdn_waf(self, dominio: str, info_dns: InfoDNS) -> Dict:
        """Detecta si el dominio usa CDN o WAF basándose en DNS"""
        resultado = {
            'usa_cdn': False,
            'cdn_detectado': None,
            'usa_waf': False,
            'waf_detectado': None
        }
        
        # Patrones de CDN/WAF conocidos en nameservers e IPs
        patrones_cdn = {
            'cloudflare': ['cloudflare', 'cf-'],
            'akamai': ['akamai', 'akam'],
            'fastly': ['fastly'],
            'cloudfront': ['cloudfront', 'amazonaws'],
            'sucuri': ['sucuri'],
            'incapsula': ['incapsula', 'imperva'],
            'stackpath': ['stackpath', 'highwinds'],
            'keycdn': ['keycdn'],
            'bunny': ['bunnycdn', 'b-cdn'],
        }
        
        # Verificar en nameservers
        for ns in info_dns.registros_ns:
            ns_lower = ns.lower()
            for cdn, patrones in patrones_cdn.items():
                if any(patron in ns_lower for patron in patrones):
                    resultado['usa_cdn'] = True
                    resultado['cdn_detectado'] = cdn.title()
                    if cdn in ['cloudflare', 'sucuri', 'incapsula']:
                        resultado['usa_waf'] = True
                        resultado['waf_detectado'] = cdn.title()
                    break
        
        # Verificar en registros TXT (algunos CDN añaden registros)
        for txt in info_dns.registros_txt:
            txt_lower = txt.lower()
            for cdn, patrones in patrones_cdn.items():
                if any(patron in txt_lower for patron in patrones):
                    resultado['usa_cdn'] = True
                    resultado['cdn_detectado'] = cdn.title()
                    break
        
        return resultado
    
    def analizar_seguridad_dns(self, dominio: str) -> Dict:
        """Analiza aspectos de seguridad relacionados con DNS"""
        dominio_limpio = self._limpiar_dominio(dominio)
        info_dns = self.obtener_registros_dns(dominio)
        
        problemas = []
        info = {
            'registros': info_dns,
            'problemas': [],
            'recomendaciones': []
        }
        
        # Verificar SPF en registros TXT
        tiene_spf = any('v=spf1' in txt.lower() for txt in info_dns.registros_txt)
        if not tiene_spf:
            problemas.append("Sin registro SPF - emails pueden ser rechazados o marcados como spam")
            info['recomendaciones'].append("Añadir registro SPF para autenticar emails del dominio")
        
        # Verificar DMARC
        try:
            response = self.session.get(
                f"https://dns.google/resolve?name=_dmarc.{dominio_limpio}&type=TXT",
                timeout=self.timeout
            )
            tiene_dmarc = False
            if response.status_code == 200:
                data = response.json()
                if 'Answer' in data:
                    tiene_dmarc = any('v=dmarc1' in ans.get('data', '').lower() for ans in data['Answer'])
            
            if not tiene_dmarc:
                problemas.append("Sin registro DMARC - vulnerable a suplantación de email")
                info['recomendaciones'].append("Configurar DMARC para proteger contra phishing")
        except Exception:
            pass
        
        # Verificar DNSSEC (simplificado)
        try:
            response = self.session.get(
                f"https://dns.google/resolve?name={dominio_limpio}&type=DNSKEY",
                timeout=self.timeout
            )
            tiene_dnssec = False
            if response.status_code == 200:
                data = response.json()
                tiene_dnssec = 'Answer' in data and len(data['Answer']) > 0
            
            if not tiene_dnssec:
                info['recomendaciones'].append("Considerar habilitar DNSSEC para mayor seguridad DNS")
        except Exception:
            pass
        
        info['problemas'] = problemas
        return info
    
    def generar_vulnerabilidades(self, dominio: str) -> List[Vulnerabilidad]:
        """Genera vulnerabilidades basadas en el análisis DNS"""
        vulnerabilidades = []
        
        analisis = self.analizar_seguridad_dns(dominio)
        
        if analisis['problemas']:
            vulnerabilidades.append(Vulnerabilidad(
                nombre="Configuración DNS de seguridad incompleta",
                severidad=Severidad.MEDIA,
                descripcion="Faltan registros DNS importantes para la seguridad del email.",
                explicacion_simple="Sin SPF y DMARC, los atacantes pueden enviar emails haciéndose pasar por tu dominio (phishing).",
                recomendacion="Configurar registros SPF, DKIM y DMARC en tu DNS.",
                detalles="\n".join(analisis['problemas']),
                cwe="CWE-290: Bypass de autenticación por suplantación"
            ))
        
        return vulnerabilidades
    
    def obtener_resumen(self, dominio: str) -> Dict:
        """Obtiene un resumen completo de la información DNS/WHOIS"""
        info_dns = self.obtener_registros_dns(dominio)
        info_whois = self.obtener_info_whois(dominio)
        cdn_waf = self.detectar_cdn_waf(dominio, info_dns)
        seguridad = self.analizar_seguridad_dns(dominio)
        
        return {
            'dns': {
                'ips': info_dns.registros_a,
                'nameservers': info_dns.registros_ns,
                'mx': info_dns.registros_mx,
            },
            'whois': {
                'registrador': info_whois.registrador,
                'creacion': info_whois.fecha_creacion,
                'expiracion': info_whois.fecha_expiracion,
            },
            'cdn_waf': cdn_waf,
            'seguridad_dns': seguridad
        }
