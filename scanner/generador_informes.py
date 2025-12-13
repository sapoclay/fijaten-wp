"""
Módulo para generar informes de vulnerabilidades
"""

from typing import List, Dict
from datetime import datetime
from .analizador_vulnerabilidades import Vulnerabilidad, Severidad

class GeneradorInformes:
    """Generador de informes de seguridad para WordPress"""
    
    def __init__(self, dominio: str, vulnerabilidades: List[Vulnerabilidad], info_sitio: Dict):
        self.dominio = dominio
        self.vulnerabilidades = vulnerabilidades
        self.info_sitio = info_sitio
        self.fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    def calcular_puntuacion_seguridad(self) -> int:
        """Calcula una puntuación de seguridad del 0 al 100"""
        puntuacion = 100
        
        for vuln in self.vulnerabilidades:
            if vuln.severidad == Severidad.CRITICA:
                puntuacion -= 25
            elif vuln.severidad == Severidad.ALTA:
                puntuacion -= 15
            elif vuln.severidad == Severidad.MEDIA:
                puntuacion -= 8
            elif vuln.severidad == Severidad.BAJA:
                puntuacion -= 3
        
        return max(0, min(100, puntuacion))
    
    def obtener_nivel_de_riesgo(self, puntuacion: int) -> str:
        """Obtiene el nivel de riesgo basado en la puntuación"""
        if puntuacion >= 90:
            return "🟢 EXCELENTE"
        elif puntuacion >= 75:
            return "🟢 BUENO"
        elif puntuacion >= 60:
            return "🟡 ACEPTABLE"
        elif puntuacion >= 40:
            return "🟠 PREOCUPANTE"
        else:
            return "🔴 CRÍTICO"
    
    def contar_vulnerabilidades_por_severidad(self) -> Dict[str, int]:
        """Cuenta vulnerabilidades por severidad"""
        conteo = {
            "Críticas": 0,
            "Altas": 0,
            "Medias": 0,
            "Bajas": 0,
            "Info": 0
        }
        
        for vuln in self.vulnerabilidades:
            if vuln.severidad == Severidad.CRITICA:
                conteo["Críticas"] += 1
            elif vuln.severidad == Severidad.ALTA:
                conteo["Altas"] += 1
            elif vuln.severidad == Severidad.MEDIA:
                conteo["Medias"] += 1
            elif vuln.severidad == Severidad.BAJA:
                conteo["Bajas"] += 1
            else:
                conteo["Info"] += 1
        
        return conteo
    
    def generar_resumen_ejecutivo(self) -> str:
        """Genera un resumen para usuarios no técnicos"""
        puntuacion = self.calcular_puntuacion_seguridad()
        nivel = self.obtener_nivel_de_riesgo(puntuacion)
        conteo = self.contar_vulnerabilidades_por_severidad()
        
        resumen = f"""
╔══════════════════════════════════════════════════════════════════╗
║                    RESUMEN EJECUTIVO                             ║
╚══════════════════════════════════════════════════════════════════╝

📊 PUNTUACIÓN DE SEGURIDAD: {puntuacion}/100
📈 NIVEL DE RIESGO: {nivel}

📋 RESUMEN DE HALLAZGOS:
   🔴 Problemas Críticos: {conteo['Críticas']}
   🟠 Problemas Altos: {conteo['Altas']}
   🟡 Problemas Medios: {conteo['Medias']}
   🟢 Problemas Bajos: {conteo['Bajas']}

"""
        
        if conteo['Críticas'] > 0:
            resumen += """
⚠️ ¡ATENCIÓN URGENTE REQUERIDA!
   Se encontraron problemas críticos que requieren acción inmediata.
   Estos problemas podrían permitir a atacantes acceder a tu sitio.
"""
        elif conteo['Altas'] > 0:
            resumen += """
⚠️ ACCIÓN RECOMENDADA
   Se encontraron problemas importantes que deberían corregirse pronto.
   Aunque no son inmediatamente peligrosos, aumentan el riesgo.
"""
        elif conteo['Medias'] > 0:
            resumen += """
ℹ️ MEJORAS SUGERIDAS
   Tu sitio tiene buena seguridad básica, pero hay espacio para mejorar.
   Considera implementar las recomendaciones cuando sea posible.
"""
        else:
            resumen += """
✅ ¡EXCELENTE TRABAJO!
   Tu sitio WordPress tiene una buena configuración de seguridad.
   Mantén las actualizaciones al día y revisa periódicamente.
"""
        
        return resumen
    
    def generar_explicacion_simple(self) -> str:
        """Genera explicaciones simples para cada vulnerabilidad"""
        if not self.vulnerabilidades:
            return "\n✅ No se encontraron vulnerabilidades significativas.\n"
        
        texto = """
╔══════════════════════════════════════════════════════════════════╗
║              EXPLICACIÓN SIMPLE DE CADA PROBLEMA                 ║
║                  (Para usuarios no técnicos)                     ║
╚══════════════════════════════════════════════════════════════════╝
"""
        
        for i, vuln in enumerate(self.vulnerabilidades, 1):
            texto += f"""
┌─────────────────────────────────────────────────────────────────┐
│ {i}. {vuln.nombre}
│ Gravedad: {vuln.severidad.value}
├─────────────────────────────────────────────────────────────────┤
│ 🤔 ¿QUÉ SIGNIFICA ESTO?
│ {vuln.explicacion_simple}
│
│ 💡 ¿QUÉ DEBO HACER?
│ {vuln.recomendacion}
└─────────────────────────────────────────────────────────────────┘
"""
        
        return texto
    
    def generar_informe_tecnico(self) -> str:
        """Genera un informe técnico detallado"""
        texto = """
╔══════════════════════════════════════════════════════════════════╗
║                    INFORME TÉCNICO DETALLADO                     ║
╚══════════════════════════════════════════════════════════════════╝
"""
        
        # Información del sitio
        texto += f"""
📌 INFORMACIÓN DEL SITIO
{'─' * 65}
   Dominio: {self.dominio}
   Fecha de análisis: {self.fecha}
"""
        
        if self.info_sitio.get('version_wordpress'):
            texto += f"   Versión WordPress: {self.info_sitio['version_wordpress']}\n"
        if self.info_sitio.get('tema_activo'):
            tema_info = self.info_sitio['tema_activo']
            if self.info_sitio.get('tema_version'):
                tema_info += f" v{self.info_sitio['tema_version']}"
            texto += f"   Tema activo: {tema_info}\n"
        if self.info_sitio.get('plugins_detectados'):
            texto += f"   Plugins detectados: {len(self.info_sitio['plugins_detectados'])}\n"
            for plugin in self.info_sitio['plugins_detectados'][:10]:
                texto += f"      • {plugin}\n"
        
        texto += f"\n{'─' * 65}\n"
        
        # Vulnerabilidades técnicas
        texto += "\n📋 VULNERABILIDADES DETECTADAS\n"
        texto += f"{'─' * 65}\n"
        
        for vuln in self.vulnerabilidades:
            texto += f"""
╔═ {vuln.severidad.value} ═══════════════════════════════════════════════════
║ {vuln.nombre}
╠══════════════════════════════════════════════════════════════════
║ Descripción: {vuln.descripcion}
║ 
║ Detalles técnicos: {vuln.detalles if vuln.detalles else 'N/A'}
║ 
║ Recomendación: {vuln.recomendacion}
╚══════════════════════════════════════════════════════════════════
"""
        
        return texto
    
    def generar_recomendaciones_prioritarias(self) -> str:
        """Genera lista de recomendaciones priorizadas"""
        texto = """
╔══════════════════════════════════════════════════════════════════╗
║                  PLAN DE ACCIÓN RECOMENDADO                      ║
║               (Ordenado por prioridad)                           ║
╚══════════════════════════════════════════════════════════════════╝
"""
        
        prioridad = 1
        
        # Primero críticas
        criticas = [v for v in self.vulnerabilidades if v.severidad == Severidad.CRITICA]
        if criticas:
            texto += "\n🔴 ACCIONES URGENTES (Hacer inmediatamente):\n"
            for vuln in criticas:
                texto += f"   {prioridad}. {vuln.recomendacion}\n"
                prioridad += 1
        
        # Luego altas
        altas = [v for v in self.vulnerabilidades if v.severidad == Severidad.ALTA]
        if altas:
            texto += "\n🟠 ACCIONES IMPORTANTES (Hacer esta semana):\n"
            for vuln in altas:
                texto += f"   {prioridad}. {vuln.recomendacion}\n"
                prioridad += 1
        
        # Medias
        medias = [v for v in self.vulnerabilidades if v.severidad == Severidad.MEDIA]
        if medias:
            texto += "\n🟡 MEJORAS RECOMENDADAS (Hacer este mes):\n"
            for vuln in medias:
                texto += f"   {prioridad}. {vuln.recomendacion}\n"
                prioridad += 1
        
        # Bajas
        bajas = [v for v in self.vulnerabilidades if v.severidad == Severidad.BAJA]
        if bajas:
            texto += "\n🟢 MEJORAS OPCIONALES (Cuando sea posible):\n"
            for vuln in bajas:
                texto += f"   {prioridad}. {vuln.recomendacion}\n"
                prioridad += 1
        
        if not self.vulnerabilidades:
            texto += "\n✅ ¡No hay acciones urgentes requeridas!\n"
            texto += "   Mantén tu WordPress actualizado y haz revisiones periódicas.\n"
        
        return texto
    
    def generar_informe_completo(self) -> str:
        """Genera el informe completo combinando todas las secciones"""
        separador = "\n" + "═" * 70 + "\n"
        
        informe = f"""
████████████████████████████████████████████████████████████████████
█                                                                  █
█         INFORME DE SEGURIDAD WORDPRESS                           █
█                                                                  █
████████████████████████████████████████████████████████████████████

🌐 Sitio analizado: {self.dominio}
📅 Fecha del análisis: {self.fecha}

"""
        
        informe += self.generar_resumen_ejecutivo()
        informe += separador
        informe += self.generar_recomendaciones_prioritarias()
        informe += separador
        informe += self.generar_explicacion_simple()
        informe += separador
        informe += self.generar_informe_tecnico()
        
        informe += """

════════════════════════════════════════════════════════════════════
                         FIN DEL INFORME
════════════════════════════════════════════════════════════════════

⚠️ AVISO LEGAL:
Este análisis es una evaluación automatizada y no garantiza la 
detección de todas las vulnerabilidades. Se recomienda complementar
con auditorías de seguridad profesionales para sitios críticos.

💡 CONSEJOS GENERALES DE SEGURIDAD:
• Mantén WordPress, temas y plugins siempre actualizados
• Usa contraseñas fuertes y únicas
• Implementa autenticación de dos factores
• Realiza copias de seguridad regulares
• Usa un plugin de seguridad (Wordfence, Sucuri, etc.)
• Limita los intentos de inicio de sesión
• Cambia el prefijo de la base de datos por defecto

"""
        
        return informe
