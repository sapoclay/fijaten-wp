"""
Fijaten-WP - Historial de Escaneos
Guarda y compara escaneos anteriores del mismo sitio
"""

import json
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
import hashlib


class HistorialEscaneos:
    """Gestiona el historial de escaneos realizados"""
    
    def __init__(self, directorio_datos: Optional[str] = None):
        """
        Inicializa el gestor de historial
        
        Args:
            directorio_datos: Directorio donde guardar los datos (por defecto: ~/.fijaten-wp/)
        """
        if directorio_datos:
            self.directorio = Path(directorio_datos)
        else:
            self.directorio = Path.home() / ".fijaten-wp" / "historial"
        
        # Crear directorio si no existe
        self.directorio.mkdir(parents=True, exist_ok=True)
        
        # Archivo índice
        self.archivo_indice = self.directorio / "indice.json"
        self.indice = self._cargar_indice()
    
    def _cargar_indice(self) -> Dict:
        """Carga el índice de escaneos"""
        if self.archivo_indice.exists():
            try:
                with open(self.archivo_indice, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"escaneos": [], "version": "1.0"}
    
    def _guardar_indice(self):
        """Guarda el índice de escaneos"""
        with open(self.archivo_indice, 'w', encoding='utf-8') as f:
            json.dump(self.indice, f, indent=2, ensure_ascii=False)
    
    def _normalizar_dominio(self, dominio: str) -> str:
        """Normaliza el nombre del dominio para usarlo como identificador"""
        dominio = dominio.lower()
        dominio = dominio.replace("https://", "").replace("http://", "")
        dominio = dominio.replace("www.", "")
        dominio = dominio.rstrip("/")
        return dominio
    
    def _generar_id_escaneo(self, dominio: str, fecha: datetime) -> str:
        """Genera un ID único para el escaneo"""
        texto = f"{dominio}_{fecha.isoformat()}"
        return hashlib.md5(texto.encode()).hexdigest()[:12]
    
    def guardar_escaneo(self, dominio: str, vulnerabilidades: List, 
                        info_sitio: Dict, puntuacion: int) -> str:
        """
        Guarda un escaneo en el historial
        
        Args:
            dominio: Dominio escaneado
            vulnerabilidades: Lista de vulnerabilidades encontradas
            info_sitio: Información del sitio
            puntuacion: Puntuación de seguridad
            
        DEvuelve:
            ID del escaneo guardado
        """
        fecha = datetime.now()
        dominio_normalizado = self._normalizar_dominio(dominio)
        id_escaneo = self._generar_id_escaneo(dominio_normalizado, fecha)
        
        # Serializar vulnerabilidades
        vulns_serializadas = []
        for vuln in vulnerabilidades:
            vulns_serializadas.append({
                "nombre": vuln.nombre,
                "severidad": vuln.severidad.value if hasattr(vuln.severidad, 'value') else str(vuln.severidad),
                "descripcion": vuln.descripcion,
                "explicacion_simple": vuln.explicacion_simple,
                "recomendacion": vuln.recomendacion,
                "detalles": vuln.detalles
            })
        
        # Datos del escaneo
        datos_escaneo = {
            "id": id_escaneo,
            "dominio": dominio,
            "dominio_normalizado": dominio_normalizado,
            "fecha": fecha.isoformat(),
            "fecha_legible": fecha.strftime("%d/%m/%Y %H:%M"),
            "puntuacion": puntuacion,
            "total_vulnerabilidades": len(vulnerabilidades),
            "vulnerabilidades": vulns_serializadas,
            "info_sitio": self._limpiar_info_sitio(info_sitio),
            "resumen": {
                "criticas": sum(1 for v in vulns_serializadas if 'CRÍTICA' in v['severidad'].upper()),
                "altas": sum(1 for v in vulns_serializadas if 'ALTA' in v['severidad'].upper()),
                "medias": sum(1 for v in vulns_serializadas if 'MEDIA' in v['severidad'].upper()),
                "bajas": sum(1 for v in vulns_serializadas if 'BAJA' in v['severidad'].upper()),
                "info": sum(1 for v in vulns_serializadas if 'INFO' in v['severidad'].upper()),
            }
        }
        
        # Guardar archivo del escaneo
        archivo_escaneo = self.directorio / f"{id_escaneo}.json"
        with open(archivo_escaneo, 'w', encoding='utf-8') as f:
            json.dump(datos_escaneo, f, indent=2, ensure_ascii=False)
        
        # Actualizar índice
        entrada_indice = {
            "id": id_escaneo,
            "dominio": dominio,
            "dominio_normalizado": dominio_normalizado,
            "fecha": fecha.isoformat(),
            "fecha_legible": fecha.strftime("%d/%m/%Y %H:%M"),
            "puntuacion": puntuacion,
            "total_vulnerabilidades": len(vulnerabilidades)
        }
        
        self.indice["escaneos"].insert(0, entrada_indice)
        
        # Limitar a últimos 100 escaneos en el índice
        if len(self.indice["escaneos"]) > 100:
            escaneos_antiguos = self.indice["escaneos"][100:]
            self.indice["escaneos"] = self.indice["escaneos"][:100]
            # Eliminar archivos antiguos
            for escaneo in escaneos_antiguos:
                archivo_antiguo = self.directorio / f"{escaneo['id']}.json"
                if archivo_antiguo.exists():
                    archivo_antiguo.unlink()
        
        self._guardar_indice()
        return id_escaneo
    
    def _limpiar_info_sitio(self, info_sitio: Dict) -> Dict:
        """Limpia la información del sitio para serialización"""
        resultado = {}
        for clave, valor in info_sitio.items():
            if clave.startswith('_'):
                continue
            if isinstance(valor, (str, int, float, bool)):
                resultado[clave] = valor
            elif isinstance(valor, list):
                resultado[clave] = [str(v) for v in valor[:20]]
            elif isinstance(valor, dict):
                resultado[clave] = self._limpiar_info_sitio(valor)
        return resultado
    
    def obtener_historial_dominio(self, dominio: str) -> List[Dict]:
        """
        Obtiene el historial de escaneos de un dominio específico
        
        Args:
            dominio: Dominio a buscar
            
        Devuelve:
            Lista de escaneos del dominio (ordenados por fecha, más reciente primero)
        """
        dominio_normalizado = self._normalizar_dominio(dominio)
        return [
            e for e in self.indice["escaneos"]
            if e["dominio_normalizado"] == dominio_normalizado
        ]
    
    def obtener_todos_escaneos(self) -> List[Dict]:
        """
        Obtiene todos los escaneos del historial
        
        Devuelve:
            Lista de todos los escaneos (ordenados por fecha)
        """
        return self.indice["escaneos"]
    
    def obtener_escaneo(self, id_escaneo: str) -> Optional[Dict]:
        """
        Obtiene los detalles completos de un escaneo
        
        Args:
            id_escaneo: ID del escaneo
            
        Devuelve:
            Diccionario con los datos del escaneo o None si no existe
        """
        archivo_escaneo = self.directorio / f"{id_escaneo}.json"
        if archivo_escaneo.exists():
            try:
                with open(archivo_escaneo, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return None
    
    def comparar_escaneos(self, id_escaneo1: str, id_escaneo2: str) -> Dict:
        """
        Compara dos escaneos y muestra las diferencias
        
        Args:
            id_escaneo1: ID del primer escaneo (más antiguo)
            id_escaneo2: ID del segundo escaneo (más reciente)
            
        Devuelve:
            Diccionario con la comparación
        """
        escaneo1 = self.obtener_escaneo(id_escaneo1)
        escaneo2 = self.obtener_escaneo(id_escaneo2)
        
        if not escaneo1 or not escaneo2:
            return {"error": "No se encontraron los escaneos especificados"}
        
        # Nombres de vulnerabilidades en cada escaneo
        vulns1 = set(v["nombre"] for v in escaneo1["vulnerabilidades"])
        vulns2 = set(v["nombre"] for v in escaneo2["vulnerabilidades"])
        
        # Calcular diferencias
        nuevas = vulns2 - vulns1  # Vulnerabilidades nuevas
        resueltas = vulns1 - vulns2  # Vulnerabilidades resueltas
        persistentes = vulns1 & vulns2  # Vulnerabilidades que persisten
        
        cambio_puntuacion = escaneo2["puntuacion"] - escaneo1["puntuacion"]
        
        return {
            "escaneo_antiguo": {
                "id": id_escaneo1,
                "fecha": escaneo1["fecha_legible"],
                "puntuacion": escaneo1["puntuacion"],
                "total_vulnerabilidades": escaneo1["total_vulnerabilidades"]
            },
            "escaneo_reciente": {
                "id": id_escaneo2,
                "fecha": escaneo2["fecha_legible"],
                "puntuacion": escaneo2["puntuacion"],
                "total_vulnerabilidades": escaneo2["total_vulnerabilidades"]
            },
            "cambio_puntuacion": cambio_puntuacion,
            "mejora": cambio_puntuacion > 0,
            "vulnerabilidades_nuevas": list(nuevas),
            "vulnerabilidades_resueltas": list(resueltas),
            "vulnerabilidades_persistentes": list(persistentes),
            "resumen": self._generar_resumen_comparacion(
                escaneo1, escaneo2, nuevas, resueltas, persistentes, cambio_puntuacion
            )
        }
    
    def _generar_resumen_comparacion(self, escaneo1: Dict, escaneo2: Dict,
                                      nuevas: set, resueltas: set, 
                                      persistentes: set, cambio_puntuacion: int) -> str:
        """Genera un resumen textual de la comparación"""
        lineas = []
        lineas.append("=" * 60)
        lineas.append("COMPARACIÓN DE ESCANEOS")
        lineas.append("=" * 60)
        lineas.append("")
        lineas.append(f"📅 Escaneo anterior: {escaneo1['fecha_legible']}")
        lineas.append(f"   Puntuación: {escaneo1['puntuacion']}/100 | Vulnerabilidades: {escaneo1['total_vulnerabilidades']}")
        lineas.append("")
        lineas.append(f"📅 Escaneo reciente: {escaneo2['fecha_legible']}")
        lineas.append(f"   Puntuación: {escaneo2['puntuacion']}/100 | Vulnerabilidades: {escaneo2['total_vulnerabilidades']}")
        lineas.append("")
        lineas.append("-" * 60)
        
        # Cambio de puntuación
        if cambio_puntuacion > 0:
            lineas.append(f"📈 MEJORA: +{cambio_puntuacion} puntos de seguridad")
        elif cambio_puntuacion < 0:
            lineas.append(f"📉 EMPEORAMIENTO: {cambio_puntuacion} puntos de seguridad")
        else:
            lineas.append("➡️ Sin cambio en la puntuación")
        
        lineas.append("")
        
        # Vulnerabilidades resueltas
        if resueltas:
            lineas.append(f"✅ VULNERABILIDADES RESUELTAS ({len(resueltas)}):")
            for v in sorted(resueltas):
                lineas.append(f"   • {v}")
            lineas.append("")
        
        # Vulnerabilidades nuevas
        if nuevas:
            lineas.append(f"⚠️ NUEVAS VULNERABILIDADES ({len(nuevas)}):")
            for v in sorted(nuevas):
                lineas.append(f"   • {v}")
            lineas.append("")
        
        # Vulnerabilidades persistentes
        if persistentes:
            lineas.append(f"⏳ VULNERABILIDADES PENDIENTES ({len(persistentes)}):")
            for v in sorted(persistentes):
                lineas.append(f"   • {v}")
            lineas.append("")
        
        lineas.append("=" * 60)
        
        return "\n".join(lineas)
    
    def eliminar_escaneo(self, id_escaneo: str) -> bool:
        """
        Elimina un escaneo del historial
        
        Args:
            id_escaneo: ID del escaneo a eliminar
            
        Devuelve:
            True si se eliminó correctamente
        """
        # Eliminar archivo
        archivo_escaneo = self.directorio / f"{id_escaneo}.json"
        if archivo_escaneo.exists():
            archivo_escaneo.unlink()
        
        # Actualizar índice
        self.indice["escaneos"] = [
            e for e in self.indice["escaneos"]
            if e["id"] != id_escaneo
        ]
        self._guardar_indice()
        return True
    
    def limpiar_historial(self) -> int:
        """
        Elimina todo el historial
        
        Devuelve:
            Número de escaneos eliminados
        """
        cantidad = len(self.indice["escaneos"])
        
        # Eliminar todos los archivos
        for archivo in self.directorio.glob("*.json"):
            if archivo.name != "indice.json":
                archivo.unlink()
        
        # Limpiar índice
        self.indice["escaneos"] = []
        self._guardar_indice()
        
        return cantidad
    
    def obtener_estadisticas_dominio(self, dominio: str) -> Dict:
        """
        Obtiene estadísticas del historial de un dominio
        
        Args:
            dominio: Dominio a analizar
            
        Devuelve:
            Estadísticas del dominio
        """
        historial = self.obtener_historial_dominio(dominio)
        
        if not historial:
            return {"error": "No hay historial para este dominio"}
        
        puntuaciones = [e["puntuacion"] for e in historial]
        
        return {
            "dominio": dominio,
            "total_escaneos": len(historial),
            "primer_escaneo": historial[-1]["fecha_legible"],
            "ultimo_escaneo": historial[0]["fecha_legible"],
            "puntuacion_actual": puntuaciones[0],
            "puntuacion_promedio": round(sum(puntuaciones) / len(puntuaciones), 1),
            "puntuacion_maxima": max(puntuaciones),
            "puntuacion_minima": min(puntuaciones),
            "tendencia": self._calcular_tendencia(puntuaciones)
        }
    
    def _calcular_tendencia(self, puntuaciones: List[int]) -> str:
        """Calcula la tendencia de las puntuaciones"""
        if len(puntuaciones) < 2:
            return "➡️ Sin suficientes datos"
        
        # Comparar primeros 3 con últimos 3 (o los que haya)
        n = min(3, len(puntuaciones) // 2)
        if n < 1:
            n = 1
        
        promedio_reciente = sum(puntuaciones[:n]) / n
        promedio_antiguo = sum(puntuaciones[-n:]) / n
        
        diferencia = promedio_reciente - promedio_antiguo
        
        if diferencia > 5:
            return "📈 Mejorando"
        elif diferencia < -5:
            return "📉 Empeorando"
        else:
            return "➡️ Estable"


# Module-level instance cache
_historial = None

def obtener_historial() -> HistorialEscaneos:
    """Obtiene la instancia única del historial"""
    global _historial
    if _historial is None:
        _historial = HistorialEscaneos()
    return _historial
