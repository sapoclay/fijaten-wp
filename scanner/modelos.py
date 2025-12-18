"""
Fijaten-WP - Modelos de datos
Clases y estructuras de datos compartidas
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


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
    cwe: str = ""  # Identificador CWE (Common Weakness Enumeration)
    componente: str = ""  # Nombre del plugin/tema/componente afectado (para enlaces CPE)


@dataclass
class InfoPlugin:
    """Información de un plugin detectado"""
    nombre: str
    version: Optional[str] = None
    slug: str = ""
    vulnerable: bool = False
    cves: List[str] = field(default_factory=list)


@dataclass
class InfoTema:
    """Información de un tema detectado"""
    nombre: str
    version: Optional[str] = None
    activo: bool = False


@dataclass 
class InfoDNS:
    """Información DNS del dominio"""
    registros_a: List[str] = field(default_factory=list)
    registros_mx: List[str] = field(default_factory=list)
    registros_ns: List[str] = field(default_factory=list)
    registros_txt: List[str] = field(default_factory=list)


@dataclass
class InfoWHOIS:
    """Información WHOIS del dominio"""
    registrador: Optional[str] = None
    fecha_creacion: Optional[str] = None
    fecha_expiracion: Optional[str] = None
    nameservers: List[str] = field(default_factory=list)
