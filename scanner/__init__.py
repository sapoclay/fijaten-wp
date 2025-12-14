# Fijaten-WP - Módulo de Análisis de Vulnerabilidades

# Centralizar la supresión de warnings de SSL (peticiones con verify=False)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .modelos import Severidad, Vulnerabilidad
from .analizador_vulnerabilidades import AnalizadorWordPress
from .generador_informes import GeneradorInformes
from .verificador_cve import VerificadorCVE
from .verificador_blacklist import VerificadorBlacklist
from .analizador_dns import AnalizadorDNS
from .detector_waf import DetectorWAF

__all__ = [
    'AnalizadorWordPress',
    'Severidad',
    'Vulnerabilidad',
    'GeneradorInformes',
    'VerificadorCVE',
    'VerificadorBlacklist',
    'AnalizadorDNS',
    'DetectorWAF'
]
