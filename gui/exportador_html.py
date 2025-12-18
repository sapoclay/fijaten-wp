"""
Fijaten-WP - Exportador HTML
Genera informes visuales en formato HTML con gráficos y estilos
"""

from datetime import datetime
from typing import List, Dict
import html


class ExportadorHTML:
    
    """Clase para exportar informes a HTML"""
    
    def __init__(self):
        pass
    
    def exportar(self, ruta_archivo: str, dominio: str,
                 vulnerabilidades: List, info_sitio: Dict,
                 puntuacion: int, conteo_severidad: Dict) -> bool:
        """
        Exporta el informe a HTML
        
        Args:
            ruta_archivo: Ruta donde guardar el HTML
            dominio: Dominio analizado
            vulnerabilidades: Lista de vulnerabilidades encontradas
            info_sitio: Información del sitio
            puntuacion: Puntuación de seguridad (0-100)
            conteo_severidad: Diccionario con conteo por severidad
            
        Devuelve:
            True si se exportó correctamente
        """
        try:
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            

            # Determinar color y estado según puntuación
            if puntuacion >= 80:
                color_puntuacion = "#16a34a"
                estado = "EXCELENTE"
            elif puntuacion >= 60:
                color_puntuacion = "#ca8a04"
                estado = "ACEPTABLE"
            elif puntuacion >= 40:
                color_puntuacion = "#ea580c"
                estado = "PREOCUPANTE"
            else:
                color_puntuacion = "#dc2626"
                estado = "CRÍTICO"
                
            
            # Generar HTML de vulnerabilidades
            html_vulnerabilidades = self._generar_html_vulnerabilidades(vulnerabilidades)
            
            # Generar HTML de información del sitio
            html_info_sitio = self._generar_html_info_sitio(info_sitio)
            
            contenido_html = f'''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Informe Fijaten-WP - {html.escape(dominio)}</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
        body {{ font-family: 'Inter', sans-serif; }}
        .score-ring {{
            background: conic-gradient(
                {color_puntuacion} 0deg {puntuacion * 3.6}deg,
                #e5e7eb {puntuacion * 3.6}deg 360deg
            );
        }}
        @media print {{
            .no-print {{ display: none; }}
            .page-break {{ page-break-before: always; }}
        }}
    </style>
</head>
<body class="bg-gray-50 min-h-screen">
    <!-- Header -->
    <header class="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-8 px-4">
        <div class="max-w-6xl mx-auto">
            <div class="flex items-center justify-between">
                <div>
                    <h1 class="text-3xl font-bold">🔒 FIJATEN-WP</h1>
                    <p class="text-blue-200 mt-1">Informe de Seguridad WordPress</p>
                </div>
                <div class="text-right">
                    <p class="text-sm text-blue-200">Fecha del análisis</p>
                    <p class="text-lg font-semibold">{fecha}</p>
                </div>
            </div>
        </div>
    </header>

    <main class="max-w-6xl mx-auto py-8 px-4">
        <!-- Información del sitio -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">🌐 Sitio Analizado</h2>
            <p class="text-2xl font-bold text-blue-600">{html.escape(dominio)}</p>
        </div>

        <!-- Puntuación y Resumen -->
        <div class="grid md:grid-cols-2 gap-8 mb-8">
            <!-- Puntuación circular -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h2 class="text-xl font-semibold text-gray-800 mb-6 text-center">📊 Puntuación de Seguridad</h2>
                <div class="flex flex-col items-center">
                    <div class="score-ring w-48 h-48 rounded-full flex items-center justify-center p-4">
                        <div class="bg-white w-full h-full rounded-full flex flex-col items-center justify-center">
                            <span class="text-5xl font-bold" style="color: {color_puntuacion}">{puntuacion}</span>
                            <span class="text-gray-500 text-sm">/100</span>
                        </div>
                    </div>
                    <div class="mt-4 px-4 py-2 rounded-full text-white font-semibold" style="background-color: {color_puntuacion}">
                        {estado}
                    </div>
                </div>
            </div>

            <!-- Gráfico de severidades -->
            <div class="bg-white rounded-xl shadow-lg p-6">
                <h2 class="text-xl font-semibold text-gray-800 mb-6 text-center">📈 Distribución de Hallazgos</h2>
                <div class="h-64">
                    <canvas id="severityChart"></canvas>
                </div>
            </div>
        </div>

        <!-- Resumen de vulnerabilidades -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">📋 Resumen de Hallazgos</h2>
            <div class="grid grid-cols-2 md:grid-cols-5 gap-4">
                <div class="bg-red-50 border-l-4 border-red-500 p-4 rounded">
                    <p class="text-3xl font-bold text-red-600">{conteo_severidad.get('Críticas', 0)}</p>
                    <p class="text-sm text-red-800">Críticas</p>
                </div>
                <div class="bg-orange-50 border-l-4 border-orange-500 p-4 rounded">
                    <p class="text-3xl font-bold text-orange-600">{conteo_severidad.get('Altas', 0)}</p>
                    <p class="text-sm text-orange-800">Altas</p>
                </div>
                <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4 rounded">
                    <p class="text-3xl font-bold text-yellow-600">{conteo_severidad.get('Medias', 0)}</p>
                    <p class="text-sm text-yellow-800">Medias</p>
                </div>
                <div class="bg-green-50 border-l-4 border-green-500 p-4 rounded">
                    <p class="text-3xl font-bold text-green-600">{conteo_severidad.get('Bajas', 0)}</p>
                    <p class="text-sm text-green-800">Bajas</p>
                </div>
                <div class="bg-blue-50 border-l-4 border-blue-500 p-4 rounded">
                    <p class="text-3xl font-bold text-blue-600">{conteo_severidad.get('Info', 0)}</p>
                    <p class="text-sm text-blue-800">Info</p>
                </div>
            </div>
        </div>

        <!-- Detalle de vulnerabilidades -->
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8 page-break">
            <h2 class="text-xl font-semibold text-gray-800 mb-6">🔍 Detalle de Vulnerabilidades</h2>
            {html_vulnerabilidades}
        </div>

        <!-- Información adicional del sitio -->
        {html_info_sitio}

    </main>

    <!-- Footer -->
    <footer class="bg-gray-800 text-gray-400 py-6 px-4 mt-8">
        <div class="max-w-6xl mx-auto text-center">
            <p>Informe generado por <span class="text-white font-semibold">Fijaten-WP</span></p>
            <p class="text-sm mt-1">{fecha}</p>
        </div>
    </footer>

    <!-- Botón de imprimir -->
    <button onclick="window.print()" 
            class="no-print fixed bottom-8 right-8 bg-blue-600 text-white px-6 py-3 rounded-full shadow-lg hover:bg-blue-700 transition flex items-center gap-2">
        🖨️ Imprimir
    </button>

    <script>
        // Gráfico de severidades
        const ctx = document.getElementById('severityChart').getContext('2d');
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: ['Críticas', 'Altas', 'Medias', 'Bajas', 'Info'],
                datasets: [{{
                    data: [{conteo_severidad.get('Críticas', 0)}, {conteo_severidad.get('Altas', 0)}, {conteo_severidad.get('Medias', 0)}, {conteo_severidad.get('Bajas', 0)}, {conteo_severidad.get('Info', 0)}],
                    backgroundColor: ['#dc2626', '#ea580c', '#ca8a04', '#16a34a', '#2563eb'],
                    borderWidth: 0
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom'
                    }}
                }}
            }}
        }});
    </script>
</body>
</html>'''
            
            # Guardar archivo
            with open(ruta_archivo, 'w', encoding='utf-8') as f:
                f.write(contenido_html)
            
            return True
            
        except Exception as e:
            raise Exception(f"Error al generar HTML: {str(e)}")
    
    def _generar_html_vulnerabilidades(self, vulnerabilidades: List) -> str:
        
        """Genera el HTML para la sección de vulnerabilidades"""
        if not vulnerabilidades:
            return '''
            <div class="text-center py-12 text-gray-500">
                <p class="text-5xl mb-4">✅</p>
                <p class="text-xl">¡No se encontraron vulnerabilidades!</p>
            </div>
            '''
        
        html_content = '<div class="space-y-4">'
        
        for i, vuln in enumerate(vulnerabilidades, 1):
            severidad_str = vuln.severidad.value if hasattr(vuln.severidad, 'value') else str(vuln.severidad)
            
            # Determinar colores según severidad
            if 'CRÍTICA' in severidad_str.upper():
                color_bg = "bg-red-50"
                color_border = "border-red-500"
                color_badge = "bg-red-500"
                icono = "🔴"
            elif 'ALTA' in severidad_str.upper():
                color_bg = "bg-orange-50"
                color_border = "border-orange-500"
                color_badge = "bg-orange-500"
                icono = "🟠"
            elif 'MEDIA' in severidad_str.upper():
                color_bg = "bg-yellow-50"
                color_border = "border-yellow-500"
                color_badge = "bg-yellow-500"
                icono = "🟡"
            else:
                color_bg = "bg-green-50"
                color_border = "border-green-500"
                color_badge = "bg-green-500"
                icono = "🟢"
            
            html_content += f'''
            <div class="{color_bg} border-l-4 {color_border} rounded-lg p-4">
                <div class="flex items-start justify-between">
                    <div class="flex-1">
                        <div class="flex items-center gap-2 mb-2">
                            <span class="text-lg">{icono}</span>
                            <h3 class="font-semibold text-gray-800">{i}. {html.escape(vuln.nombre)}</h3>
                            <span class="{color_badge} text-white text-xs px-2 py-1 rounded">{html.escape(severidad_str)}</span>
                        </div>
                        <p class="text-gray-600 mb-3">{html.escape(vuln.descripcion)}</p>
                        
                        <div class="bg-white bg-opacity-50 rounded p-3 mb-3">
                            <p class="text-sm font-medium text-gray-700 mb-1">🤔 ¿Qué significa?</p>
                            <p class="text-sm text-gray-600">{html.escape(vuln.explicacion_simple)}</p>
                        </div>
                        
                        <div class="bg-white bg-opacity-50 rounded p-3">
                            <p class="text-sm font-medium text-gray-700 mb-1">💡 Recomendación</p>
                            <p class="text-sm text-gray-600">{html.escape(vuln.recomendacion)}</p>
                        </div>
                        
                        {"<details class='mt-3'><summary class='text-sm text-gray-500 cursor-pointer'>Ver detalles técnicos</summary><pre class='mt-2 text-xs bg-gray-100 p-2 rounded overflow-x-auto'>" + html.escape(vuln.detalles) + "</pre></details>" if vuln.detalles else ""}
                    </div>
                </div>
            </div>
            '''
        
        html_content += '</div>'
        return html_content
    
    def _generar_html_info_sitio(self, info_sitio: Dict) -> str:
        """Genera el HTML para la información del sitio"""
        if not info_sitio:
            return ''
        
        # Filtrar información relevante
        items = []
        # Claves a omitir en la tabla genérica
        claves_omitir = {'error', 'tecnologias_detectadas', 'no_es_wordpress', 
                         'plugins_detectados', 'plugins_con_versiones'}
        
        for clave, valor in info_sitio.items():
            if not clave.startswith('_') and valor and clave not in claves_omitir:
                clave_formateada = clave.replace('_', ' ').title()
                if isinstance(valor, list):
                    # Formatear lista de tuplas para plugins
                    if valor and isinstance(valor[0], tuple):
                        valor_str = ', '.join(
                            f"{v[0]} v{v[1]}" if v[1] else f"{v[0]}" 
                            for v in valor[:10]
                        )
                    else:
                        valor_str = ', '.join(str(v) for v in valor[:10])
                    if len(valor) > 10:
                        valor_str += f" (+{len(valor) - 10} más)"
                elif isinstance(valor, dict):
                    continue  # Saltar diccionarios anidados
                else:
                    valor_str = str(valor)
                items.append((clave_formateada, valor_str))
        
        # Añadir plugins con versiones de forma especial
        plugins_con_versiones = info_sitio.get('plugins_con_versiones', [])
        if plugins_con_versiones:
            plugins_formateados = []
            for plugin, version in plugins_con_versiones[:10]:
                if version:
                    plugins_formateados.append(f"{plugin} v{version}")
                else:
                    plugins_formateados.append(f"{plugin} (versión desconocida)")
            valor_str = ', '.join(plugins_formateados)
            if len(plugins_con_versiones) > 10:
                valor_str += f" (+{len(plugins_con_versiones) - 10} más)"
            items.append(('Plugins Detectados', valor_str))
        
        if not items:
            return ''
        
        html_content = '''
        <div class="bg-white rounded-xl shadow-lg p-6 mb-8">
            <h2 class="text-xl font-semibold text-gray-800 mb-4">ℹ️ Información del Sitio</h2>
            <div class="overflow-x-auto">
                <table class="w-full text-left">
                    <tbody>
        '''
        
        for clave, valor in items:
            html_content += f'''
                        <tr class="border-b border-gray-100">
                            <td class="py-3 pr-4 font-medium text-gray-700 whitespace-nowrap">{html.escape(clave)}</td>
                            <td class="py-3 text-gray-600">{html.escape(valor[:200])}</td>
                        </tr>
            '''
        
        html_content += '''
                    </tbody>
                </table>
            </div>
        </div>
        '''
        
        return html_content


# Module-level instance cache
_exportador_html = None

def obtener_exportador_html() -> ExportadorHTML:
    """Obtiene la instancia única del exportador HTML"""
    global _exportador_html
    if _exportador_html is None:
        _exportador_html = ExportadorHTML()
    return _exportador_html
