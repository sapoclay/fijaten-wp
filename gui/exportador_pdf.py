"""
Fijaten-WP - Exportador PDF
Genera informes en formato PDF profesional
"""

import os
from datetime import datetime
from typing import List, Dict, Optional, TYPE_CHECKING, Any
from pathlib import Path

# Variables para almacenar los módulos de reportlab
colors: Any = None
A4: Any = None
cm: Any = None
mm: Any = None
getSampleStyleSheet: Any = None
ParagraphStyle: Any = None
SimpleDocTemplate: Any = None
Paragraph: Any = None
Spacer: Any = None
Table: Any = None
TableStyle: Any = None
Image: Any = None
PageBreak: Any = None
HRFlowable: Any = None
TA_CENTER: Any = None
TA_LEFT: Any = None
TA_JUSTIFY: Any = None
Drawing: Any = None
Circle: Any = None
Wedge: Any = None

# Intentar importar reportlab para PDF
REPORTLAB_DISPONIBLE = False
try:
    from reportlab.lib import colors as _colors
    from reportlab.lib.pagesizes import A4 as _A4, letter as _letter
    from reportlab.lib.styles import getSampleStyleSheet as _getSampleStyleSheet, ParagraphStyle as _ParagraphStyle
    from reportlab.lib.units import cm as _cm, mm as _mm
    from reportlab.platypus import (
        SimpleDocTemplate as _SimpleDocTemplate, 
        Paragraph as _Paragraph, 
        Spacer as _Spacer, 
        Table as _Table, 
        TableStyle as _TableStyle, 
        Image as _Image, 
        PageBreak as _PageBreak, 
        HRFlowable as _HRFlowable
    )
    from reportlab.lib.enums import TA_CENTER as _TA_CENTER, TA_LEFT as _TA_LEFT, TA_JUSTIFY as _TA_JUSTIFY
    from reportlab.graphics.shapes import Drawing as _Drawing, Circle as _Circle, Wedge as _Wedge
    
    # Asignar a las variables del módulo
    colors = _colors
    A4 = _A4
    cm = _cm
    mm = _mm
    getSampleStyleSheet = _getSampleStyleSheet
    ParagraphStyle = _ParagraphStyle
    SimpleDocTemplate = _SimpleDocTemplate
    Paragraph = _Paragraph
    Spacer = _Spacer
    Table = _Table
    TableStyle = _TableStyle
    Image = _Image
    PageBreak = _PageBreak
    HRFlowable = _HRFlowable
    TA_CENTER = _TA_CENTER
    TA_LEFT = _TA_LEFT
    TA_JUSTIFY = _TA_JUSTIFY
    Drawing = _Drawing
    Circle = _Circle
    Wedge = _Wedge
    
    REPORTLAB_DISPONIBLE = True
except ImportError:
    pass


class ExportadorPDF:
    """Clase para exportar informes a PDF"""
    
    def __init__(self):
        self.disponible = REPORTLAB_DISPONIBLE
        
    def esta_disponible(self) -> bool:
        """Verifica si la exportación a PDF está disponible"""
        return self.disponible
    
    def obtener_mensaje_instalacion(self) -> str:
        """Retorna mensaje para instalar dependencias"""
        return "Para exportar a PDF, instala: pip install reportlab"
    
    def exportar(self, ruta_archivo: str, dominio: str, 
                 vulnerabilidades: List, info_sitio: Dict,
                 puntuacion: int, conteo_severidad: Dict) -> bool:
        """
        Exporta el informe a PDF
        
        Args:
            ruta_archivo: Ruta donde guardar el PDF
            dominio: Dominio analizado
            vulnerabilidades: Lista de vulnerabilidades encontradas
            info_sitio: Información del sitio
            puntuacion: Puntuación de seguridad (0-100)
            conteo_severidad: Diccionario con conteo por severidad
            
        Returns:
            True si se exportó correctamente
        """
        if not self.disponible:
            raise ImportError(self.obtener_mensaje_instalacion())
        
        try:
            doc = SimpleDocTemplate(
                ruta_archivo,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            # Estilos
            styles = getSampleStyleSheet()
            
            # Estilos personalizados
            estilo_titulo = ParagraphStyle(
                'TituloFijaten',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=colors.HexColor('#2563eb')
            )
            
            estilo_subtitulo = ParagraphStyle(
                'SubtituloFijaten',
                parent=styles['Heading2'],
                fontSize=16,
                spaceBefore=20,
                spaceAfter=10,
                textColor=colors.HexColor('#1e40af')
            )
            
            estilo_normal = ParagraphStyle(
                'NormalFijaten',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=6,
                alignment=TA_JUSTIFY
            )
            
            estilo_critico = ParagraphStyle(
                'CriticoFijaten',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#dc2626'),
                spaceAfter=4
            )
            
            estilo_alto = ParagraphStyle(
                'AltoFijaten',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#ea580c'),
                spaceAfter=4
            )
            
            estilo_medio = ParagraphStyle(
                'MedioFijaten',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#ca8a04'),
                spaceAfter=4
            )
            
            estilo_bajo = ParagraphStyle(
                'BajoFijaten',
                parent=styles['Normal'],
                fontSize=10,
                textColor=colors.HexColor('#16a34a'),
                spaceAfter=4
            )
            
            # Contenido del PDF
            elementos = []
            
            # Título
            elementos.append(Paragraph("FIJATEN-WP", estilo_titulo))
            elementos.append(Paragraph("Informe de Seguridad WordPress", styles['Heading2']))
            elementos.append(Spacer(1, 20))
            
            # Información básica
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            info_tabla = [
                ["Dominio analizado:", dominio],
                ["Fecha del análisis:", fecha],
                ["Puntuación de seguridad:", f"{puntuacion}/100"],
            ]
            
            tabla_info = Table(info_tabla, colWidths=[5*cm, 10*cm])
            tabla_info.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
            ]))
            elementos.append(tabla_info)
            elementos.append(Spacer(1, 20))
            
            # Gráfico de puntuación
            elementos.append(self._crear_grafico_puntuacion(puntuacion))
            elementos.append(Spacer(1, 20))
            
            # Resumen de vulnerabilidades
            elementos.append(Paragraph("Resumen de Hallazgos", estilo_subtitulo))
            elementos.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563eb')))
            elementos.append(Spacer(1, 10))
            
            resumen_data = [
                ["Severidad", "Cantidad", "Descripción"],
                ["🔴 Críticas", str(conteo_severidad.get('Críticas', 0)), "Requieren acción inmediata"],
                ["🟠 Altas", str(conteo_severidad.get('Altas', 0)), "Deben corregirse pronto"],
                ["🟡 Medias", str(conteo_severidad.get('Medias', 0)), "Mejorar cuando sea posible"],
                ["🟢 Bajas", str(conteo_severidad.get('Bajas', 0)), "Mejoras menores"],
                ["ℹ️ Info", str(conteo_severidad.get('Info', 0)), "Información adicional"],
            ]
            
            tabla_resumen = Table(resumen_data, colWidths=[4*cm, 3*cm, 8*cm])
            tabla_resumen.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                ('TOPPADDING', (0, 0), (-1, -1), 8),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ]))
            elementos.append(tabla_resumen)
            elementos.append(Spacer(1, 20))
            
            # Detalle de vulnerabilidades
            if vulnerabilidades:
                elementos.append(PageBreak())
                elementos.append(Paragraph("Detalle de Vulnerabilidades", estilo_subtitulo))
                elementos.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563eb')))
                elementos.append(Spacer(1, 10))
                
                for i, vuln in enumerate(vulnerabilidades, 1):
                    # Determinar estilo según severidad
                    severidad_str = vuln.severidad.value if hasattr(vuln.severidad, 'value') else str(vuln.severidad)
                    
                    if 'CRÍTICA' in severidad_str.upper():
                        estilo_sev = estilo_critico
                        color_fondo = colors.HexColor('#fef2f2')
                    elif 'ALTA' in severidad_str.upper():
                        estilo_sev = estilo_alto
                        color_fondo = colors.HexColor('#fff7ed')
                    elif 'MEDIA' in severidad_str.upper():
                        estilo_sev = estilo_medio
                        color_fondo = colors.HexColor('#fefce8')
                    else:
                        estilo_sev = estilo_bajo
                        color_fondo = colors.HexColor('#f0fdf4')
                    
                    # Tabla para cada vulnerabilidad
                    vuln_data = [
                        [Paragraph(f"<b>{i}. {vuln.nombre}</b>", estilo_sev)],
                        [Paragraph(f"<b>Severidad:</b> {severidad_str}", estilo_normal)],
                        [Paragraph(f"<b>Descripción:</b> {self._escapar_html(vuln.descripcion)}", estilo_normal)],
                        [Paragraph(f"<b>Explicación:</b> {self._escapar_html(vuln.explicacion_simple)}", estilo_normal)],
                        [Paragraph(f"<b>Recomendación:</b> {self._escapar_html(vuln.recomendacion)}", estilo_normal)],
                    ]
                    
                    if vuln.detalles:
                        # Convertir saltos de línea a <br/> para el PDF
                        detalles_formateados = self._formatear_detalles(vuln.detalles)
                        vuln_data.append([Paragraph(f"<b>Detalles:</b><br/>{detalles_formateados}", estilo_normal)])
                    
                    tabla_vuln = Table(vuln_data, colWidths=[15*cm])
                    tabla_vuln.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, -1), color_fondo),
                        ('BOX', (0, 0), (-1, -1), 1, colors.grey),
                        ('LEFTPADDING', (0, 0), (-1, -1), 10),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                        ('TOPPADDING', (0, 0), (-1, -1), 8),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
                    ]))
                    
                    elementos.append(tabla_vuln)
                    elementos.append(Spacer(1, 15))
            
            # Información adicional del sitio
            if info_sitio:
                elementos.append(PageBreak())
                elementos.append(Paragraph("Información del Sitio", estilo_subtitulo))
                elementos.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#2563eb')))
                elementos.append(Spacer(1, 10))
                
                info_items = []
                for clave, valor in info_sitio.items():
                    if not clave.startswith('_') and valor and clave not in ['error', 'tecnologias_detectadas']:
                        clave_formateada = clave.replace('_', ' ').title()
                        if isinstance(valor, list):
                            valor = ', '.join(str(v) for v in valor[:5])
                            if len(info_sitio[clave]) > 5:
                                valor += f" (+{len(info_sitio[clave]) - 5} más)"
                        info_items.append([clave_formateada, str(valor)[:100]])
                
                if info_items:
                    tabla_sitio = Table(info_items, colWidths=[5*cm, 10*cm])
                    tabla_sitio.setStyle(TableStyle([
                        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, -1), 9),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.lightgrey),
                        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ]))
                    elementos.append(tabla_sitio)
            
            # Pie de página con marca de agua
            elementos.append(Spacer(1, 30))
            elementos.append(HRFlowable(width="100%", thickness=0.5, color=colors.grey))
            elementos.append(Spacer(1, 10))
            
            pie_texto = f"Informe generado por Fijaten-WP - {fecha}"
            estilo_pie = ParagraphStyle(
                'PieFijaten',
                parent=styles['Normal'],
                fontSize=8,
                textColor=colors.grey,
                alignment=TA_CENTER
            )
            elementos.append(Paragraph(pie_texto, estilo_pie))
            
            # Generar PDF
            doc.build(elementos)
            return True
            
        except Exception as e:
            raise Exception(f"Error al generar PDF: {str(e)}")
    
    def _escapar_html(self, texto: str) -> str:
        """Escapa caracteres especiales HTML y convierte saltos de línea"""
        if not texto:
            return ""
        # Escapar caracteres HTML especiales
        texto = texto.replace('&', '&amp;')
        texto = texto.replace('<', '&lt;')
        texto = texto.replace('>', '&gt;')
        # Convertir saltos de línea a <br/>
        texto = texto.replace('\n', '<br/>')
        return texto
    
    def _formatear_detalles(self, detalles: str) -> str:
        """Formatea los detalles para que se muestren correctamente en el PDF"""
        if not detalles:
            return ""
        
        # Escapar caracteres HTML especiales primero
        detalles = detalles.replace('&', '&amp;')
        detalles = detalles.replace('<', '&lt;')
        detalles = detalles.replace('>', '&gt;')
        
        # Convertir saltos de línea a <br/>
        detalles = detalles.replace('\n', '<br/>')
        
        # Convertir bullets • a puntos con sangría
        detalles = detalles.replace('• ', '<br/>&nbsp;&nbsp;&nbsp;• ')
        
        # Limpiar <br/> duplicados
        while '<br/><br/><br/>' in detalles:
            detalles = detalles.replace('<br/><br/><br/>', '<br/><br/>')
        
        return detalles
    
    def _crear_grafico_puntuacion(self, puntuacion: int):
        """Crea un gráfico visual de la puntuación"""
        # Determinar color según puntuación
        if puntuacion >= 80:
            color_principal = colors.HexColor('#16a34a')  # Verde
            estado = "EXCELENTE"
        elif puntuacion >= 60:
            color_principal = colors.HexColor('#ca8a04')  # Amarillo
            estado = "ACEPTABLE"
        elif puntuacion >= 40:
            color_principal = colors.HexColor('#ea580c')  # Naranja
            estado = "PREOCUPANTE"
        else:
            color_principal = colors.HexColor('#dc2626')  # Rojo
            estado = "CRÍTICO"
        
        # Crear dibujo
        drawing = Drawing(400, 120)
        
        # Fondo del medidor (gris)
        drawing.add(Wedge(100, 60, 50, 0, 180, fillColor=colors.lightgrey, strokeColor=None))
        
        # Parte coloreada según puntuación
        angulo = 180 * (puntuacion / 100)
        drawing.add(Wedge(100, 60, 50, 0, angulo, fillColor=color_principal, strokeColor=None))
        
        # Círculo central (blanco)
        drawing.add(Circle(100, 60, 30, fillColor=colors.white, strokeColor=None))
        
        return drawing


# Singleton
_exportador_pdf = None

def obtener_exportador_pdf() -> ExportadorPDF:
    """Obtiene la instancia única del exportador PDF"""
    global _exportador_pdf
    if _exportador_pdf is None:
        _exportador_pdf = ExportadorPDF()
    return _exportador_pdf
