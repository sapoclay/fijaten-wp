"""
Fijaten-WP - Ventana Principal
Ventana principal de la aplicación
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from datetime import datetime
import os
import sys
from pathlib import Path

# Añadir directorio padre al path
sys.path.insert(0, str(Path(__file__).parent.parent))

from configuracion import (
    APP_NAME, WINDOW_TITLE, WINDOW_SIZE, WINDOW_MIN_SIZE,
    THEME_MODE, THEME_COLOR, MESSAGES
)
from scanner.analizador_vulnerabilidades import AnalizadorWordPress
from scanner.generador_informes import GeneradorInformes
from gui.componentes import FrameCabecera, FrameEntrada, FrameResultados, FramePie
from gui.barra_menu import BarraMenu
from gui.dialogo_acerca import DialogoAcerca
from gui.dialogo_opciones import DialogoOpciones, obtener_verificaciones_activas
from gui.dialogo_escaneo_multiple import DialogoEscaneoMultiple
from gui.dialogo_historial import DialogoHistorial
from gui.gestor_temas import obtener_gestor_temas
from gui.notificaciones import notificar_escaneo_completado
from gui.historial_escaneos import obtener_historial
from gui.exportador_pdf import obtener_exportador_pdf
from gui.exportador_html import obtener_exportador_html
from gui.grafico_puntuacion import FrameGraficoPuntuacion

# Inicializar gestor de temas (aplica el tema guardado)
gestor_temas = obtener_gestor_temas()


class VentanaPrincipal(ctk.CTk):
    """Ventana principal de Fijaten-WP"""
    
    def __init__(self):
        super().__init__()
        
        # Configuración de la ventana principal
        self.title(WINDOW_TITLE)
        self.geometry(WINDOW_SIZE)
        self.minsize(*WINDOW_MIN_SIZE)
        
        # Variables de estado
        self.escaneando = False
        self.vulnerabilidades = []
        self.info_sitio = {}
        self.informe_completo = ""
        self.dominio_actual = ""
        self.puntuacion_actual = 0
        self.conteo_severidad = {}
        
        # Obtener gestores
        self.historial = obtener_historial()
        self.exportador_pdf = obtener_exportador_pdf()
        self.exportador_html = obtener_exportador_html()
        
        # Crear menú
        self.barra_menu = BarraMenu(
            self,
            on_exit=self.salir,
            on_about=self.mostrar_acerca_de,
            on_options=self.mostrar_opciones,
            on_escaneo_multiple=self.mostrar_escaneo_multiple,
            on_exportar_pdf=self.exportar_pdf,
            on_exportar_html=self.exportar_html,
            on_historial=self.mostrar_historial,
            on_guardar=self.guardar_informe
        )
        
        # Crear la interfaz
        self._crear_interfaz()
        
        # Manejar cierre de ventana
        self.protocol("WM_DELETE_WINDOW", self.salir)
    
    def _crear_interfaz(self):
        """Crea todos los elementos de la interfaz"""
        
        # Frame principal con grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # ═══════════════════════════════════════════════════════════
        # CABECERA
        # ═══════════════════════════════════════════════════════════
        self.frame_cabecera = FrameCabecera(
            self,
            titulo=f"🔒 {APP_NAME}",
            subtitulo="Analiza la seguridad de cualquier sitio WordPress"
        )
        self.frame_cabecera.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        # ═══════════════════════════════════════════════════════════
        # PANEL DE ENTRADA
        # ═══════════════════════════════════════════════════════════
        self.frame_entrada = FrameEntrada(self, al_analizar=self.iniciar_escaneo)
        self.frame_entrada.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        
        # ═══════════════════════════════════════════════════════════
        # ÁREA DE RESULTADOS
        # ═══════════════════════════════════════════════════════════
        self.frame_resultados = FrameResultados(self, mensaje_inicial=MESSAGES["welcome"])
        self.frame_resultados.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        
        # ═══════════════════════════════════════════════════════════
        # BARRA DE ESTADO Y ACCIONES
        # ═══════════════════════════════════════════════════════════
        self.frame_pie = FramePie(
            self,
            al_guardar=self.guardar_informe,
            al_limpiar=self.limpiar_resultados
        )
        self.frame_pie.grid(row=3, column=0, sticky="ew", padx=20, pady=(5, 15))
    
    # ═══════════════════════════════════════════════════════════════════
    # MENÚ
    # ═══════════════════════════════════════════════════════════════════
    
    def salir(self):
        """Sale de la aplicación"""
        if self.escaneando:
            if not messagebox.askyesno(
                "Confirmar salida",
                "Hay un análisis en curso. ¿Deseas salir de todos modos?"
            ):
                return
        self.destroy()
    
    def mostrar_acerca_de(self):
        """Muestra el diálogo Acerca de"""
        DialogoAcerca(self)
    
    def mostrar_opciones(self):
        """Muestra el diálogo de opciones de escaneo"""
        DialogoOpciones(self)
    
    def mostrar_escaneo_multiple(self):
        """Muestra el diálogo de escaneo múltiple"""
        DialogoEscaneoMultiple(self)
    
    # ═══════════════════════════════════════════════════════════════════
    # ESCANEO
    # ═══════════════════════════════════════════════════════════════════
    
    def actualizar_estado(self, mensaje: str):
        """Actualiza el mensaje de estado y la barra de progreso detallada"""
        self.frame_pie.establecer_estado(mensaje)
        
        # Extraer información de progreso si está en formato [x/y]
        import re
        match = re.match(r'\[(\d+)/(\d+)\]\s*(.+)', mensaje)
        if match:
            actual = int(match.group(1))
            total = int(match.group(2))
            descripcion = match.group(3)
            self.after(0, lambda: self.frame_pie.establecer_verificacion_actual(
                descripcion, actual, total
            ))
        
        self.update_idletasks()
    
    def iniciar_escaneo(self):
        """Inicia el escaneo en un hilo separado"""
        dominio = self.frame_entrada.obtener_dominio()
        
        if not dominio:
            messagebox.showwarning("Aviso", MESSAGES["no_domain"])
            return
        
        if self.escaneando:
            messagebox.showinfo("Info", MESSAGES["scan_in_progress"])
            return
        
        # Guardar dominio para notificación
        self.dominio_actual = dominio
        
        # Limpiar resultados anteriores
        self.limpiar_resultados(mostrar_mensaje=False)
        
        # Deshabilitar botón y mostrar progreso
        self.escaneando = True
        self.frame_entrada.establecer_escaneando(True)
        self.frame_pie.establecer_progreso(0)
        self.frame_pie.iniciar_progreso()
        
        # Ejecutar en hilo separado
        hilo = threading.Thread(target=self._ejecutar_escaneo, args=(dominio,))
        hilo.daemon = True
        hilo.start()
    
    def _ejecutar_escaneo(self, dominio: str):
        """Ejecuta el escaneo de vulnerabilidades"""
        try:
            # Obtener verificaciones activas de las opciones
            verificaciones_activas = obtener_verificaciones_activas()
            
            # Crear analizador con las verificaciones seleccionadas
            analizador = AnalizadorWordPress(
                dominio, 
                callback=self.actualizar_estado,
                verificaciones_activas=verificaciones_activas
            )
            
            # Ejecutar escaneo
            self.vulnerabilidades, self.info_sitio = analizador.ejecutar_escaneo_completo()
            
            # Verificar si hubo error
            if 'error' in self.info_sitio:
                # Verificar si hay tecnologías detectadas (sitio no WordPress)
                if self.info_sitio.get('no_es_wordpress') and 'informe_tecnologias' in self.info_sitio:
                    self.after(0, lambda: self._mostrar_tecnologias_detectadas(self.info_sitio))
                else:
                    self.after(0, lambda: self._mostrar_error(self.info_sitio['error']))
                return
            
            # Generar informe
            generador = GeneradorInformes(dominio, self.vulnerabilidades, self.info_sitio)
            self.informe_completo = generador.generar_informe_completo()
            
            # Guardar puntuación y conteo para exportación
            self.puntuacion_actual = generador.calcular_puntuacion_seguridad()
            self.conteo_severidad = generador.contar_vulnerabilidades_por_severidad()
            self.dominio_actual = dominio
            
            # Guardar en historial
            self.historial.guardar_escaneo(
                dominio, 
                self.vulnerabilidades, 
                self.info_sitio, 
                self.puntuacion_actual
            )
            
            # Mostrar resultados en la UI
            self.after(0, lambda: self._mostrar_resultados(generador))
            
            # Enviar notificación de escritorio
            self.after(0, lambda: notificar_escaneo_completado(
                dominio, 
                len(self.vulnerabilidades), 
                self.puntuacion_actual
            ))
            
        except Exception as e:
            self.after(0, lambda: self._mostrar_error(f"Error durante el análisis: {str(e)}"))
        finally:
            self.after(0, self._finalizar_escaneo)
    
    def _mostrar_resultados(self, generador: GeneradorInformes):
        """Muestra los resultados en la interfaz"""
        resumen = generador.generar_resumen_ejecutivo()
        puntuacion = generador.calcular_puntuacion_seguridad()
        
        contenido_resumen = f"""
████████████████████████████████████████████████████████████████████
█                ANÁLISIS COMPLETADO                                █
████████████████████████████████████████████████████████████████████

🌐 Sitio analizado: {generador.dominio}
📅 Fecha: {generador.fecha}

{resumen}

{'─' * 70}

ℹ️  Revisa las otras pestañas para más detalles:
    • Detalles: Explicación simple de cada problema
    • Técnico: Información técnica completa  
    • Plan de Acción: Qué hacer y en qué orden
"""
        
        self.frame_resultados.establecer_contenido(
            resumen=contenido_resumen,
            detalles=generador.generar_explicacion_simple(),
            tecnico=generador.generar_informe_tecnico(),
            acciones=generador.generar_recomendaciones_prioritarias()
        )
        
        # Habilitar botón de guardar
        self.frame_pie.habilitar_guardar(True)
        
        # Mostrar mensaje de éxito
        total_vulns = len(self.vulnerabilidades)
        self.frame_pie.establecer_estado(
            f"✅ Análisis completado. Se encontraron {total_vulns} vulnerabilidades. Puntuación: {puntuacion}/100"
        )
    
    def _mostrar_error(self, mensaje: str):
        """Muestra un mensaje de error"""
        contenido_error = f"""
╔══════════════════════════════════════════════════════════════════╗
║                         ⚠️ ERROR                                  ║
╚══════════════════════════════════════════════════════════════════╝

{mensaje}

Posibles causas:
• El dominio no es válido o no existe
• El sitio no está accesible
• El sitio no es WordPress
• Problemas de conexión a internet

Sugerencias:
• Verifica que el dominio esté escrito correctamente
• Asegúrate de que el sitio esté funcionando
• Intenta con o sin 'www.' en el dominio
• Prueba con 'https://' explícitamente
"""
        # Usar el método de FrameResultados que maneja solo lectura
        self.frame_resultados.mostrar_mensaje(contenido_error)
        self.frame_pie.establecer_estado(f"❌ Error: {mensaje}")
    
    def _mostrar_tecnologias_detectadas(self, info_sitio: dict):
        """Muestra las tecnologías detectadas cuando el sitio no es WordPress"""
        informe = info_sitio.get('informe_tecnologias', '')
        tecnologias = info_sitio.get('tecnologias_detectadas', {})
        
        # Contar total de tecnologías detectadas
        total_detectadas = sum(len(v) if isinstance(v, list) else (1 if v else 0) 
                              for v in tecnologias.values())
        
        contenido = f"""
╔══════════════════════════════════════════════════════════════════╗
║              🔍 ANÁLISIS DE TECNOLOGÍAS WEB                       ║
╚══════════════════════════════════════════════════════════════════╝

⚠️  Este sitio NO utiliza WordPress, pero hemos detectado las
    siguientes tecnologías:

{informe}

{'─' * 70}

ℹ️  NOTA: Fijaten-WP está diseñado específicamente para analizar
    vulnerabilidades en sitios WordPress. Para este tipo de sitio,
    recomendamos utilizar herramientas de análisis especializadas
    en las tecnologías detectadas.

💡 Sugerencias:
    • Para sitios Joomla: utilizar herramientas como joomscan
    • Para sitios Drupal: utilizar droopescan
    • Para aplicaciones React/Vue: revisar cabeceras de seguridad
    • Para sitios con Shopify/WooCommerce: revisar configuración SSL
"""
        
        # Mostrar en todas las pestañas
        self.frame_resultados.establecer_contenido(
            resumen=contenido,
            detalles=f"""
🔍 EXPLICACIÓN SIMPLE
{'─' * 50}

Hemos analizado el sitio web y NO es WordPress.

{informe}

¿Qué significa esto?
Fijaten-WP está especializado en encontrar problemas de seguridad
en sitios WordPress. Como este sitio usa otras tecnologías,
te recomendamos buscar herramientas específicas para analizarlo.
""",
            tecnico=f"""
📋 INFORMACIÓN TÉCNICA
{'─' * 50}

{informe}

Datos técnicos detectados:
{self._formatear_tecnologias_tecnico(tecnologias)}
""",
            acciones=f"""
📋 RECOMENDACIONES
{'─' * 50}

Como este sitio no es WordPress, considera:

1. Buscar escáneres de seguridad específicos para las
   tecnologías detectadas.

2. Revisar las cabeceras de seguridad HTTP del sitio.

3. Verificar que el certificado SSL esté correctamente
   configurado.

4. Comprobar que el sitio no esté en listas negras de
   malware o spam.

5. Si administras el sitio, mantén actualizadas todas
   las tecnologías y dependencias.
"""
        )
        
        # Mostrar estado informativo
        self.frame_pie.establecer_estado(
            f"ℹ️ Sitio no WordPress. {total_detectadas} tecnologías detectadas."
        )
        self.frame_pie.establecer_progreso(1)
    
    def _formatear_tecnologias_tecnico(self, tecnologias: dict) -> str:
        """Formatea las tecnologías para la vista técnica"""
        lineas = []
        
        # CMS
        if tecnologias.get('cms'):
            cms = tecnologias['cms']
            lineas.append(f"\n📦 CMS/Plataforma: {cms.get('icono', '')} {cms.get('nombre', 'Desconocido')}")
            lineas.append(f"   Confianza: {cms.get('confianza', 0)}%")
        
        # Framework
        if tecnologias.get('framework'):
            fw = tecnologias['framework']
            lineas.append(f"\n🛠️ Framework: {fw.get('icono', '')} {fw.get('nombre', 'Desconocido')}")
            lineas.append(f"   Confianza: {fw.get('confianza', 0)}%")
        
        # Lenguaje
        if tecnologias.get('lenguaje'):
            lang = tecnologias['lenguaje']
            lineas.append(f"\n💻 Lenguaje: {lang.get('icono', '')} {lang.get('nombre', 'Desconocido')}")
            lineas.append(f"   Confianza: {lang.get('confianza', 0)}%")
        
        # Frontend
        if tecnologias.get('frontend'):
            lineas.append("\n🎨 Frontend:")
            for f in tecnologias['frontend']:
                lineas.append(f"   • {f.get('icono', '')} {f.get('nombre', 'Desconocido')} ({f.get('confianza', 0)}%)")
        
        # Servidor
        if tecnologias.get('servidor'):
            srv = tecnologias['servidor']
            lineas.append(f"\n🖥️ Servidor: {srv.get('icono', '')} {srv.get('nombre', 'Desconocido')}")
        
        # Otras
        if tecnologias.get('otras'):
            lineas.append("\n🔧 Otras tecnologías:")
            for o in tecnologias['otras']:
                lineas.append(f"   • {o.get('icono', '')} {o.get('nombre', 'Desconocido')} ({o.get('confianza', 0)}%)")
        
        # Detalles adicionales
        if tecnologias.get('detalles'):
            lineas.append("\n📋 Detalles de detección:")
            for d in tecnologias['detalles']:
                lineas.append(f"   {d}")
        
        return '\n'.join(lineas) if lineas else "No se detectaron tecnologías específicas."
    
    def _finalizar_escaneo(self):
        """Restaura la interfaz después del escaneo"""
        self.escaneando = False
        self.frame_entrada.establecer_escaneando(False)
        self.frame_pie.detener_progreso()
        self.frame_pie.establecer_progreso(1 if self.vulnerabilidades or 'error' not in self.info_sitio else 0)
    
    def limpiar_resultados(self, mostrar_mensaje: bool = True):
        """Limpia los resultados y restablece la interfaz"""
        self.vulnerabilidades = []
        self.info_sitio = {}
        self.informe_completo = ""
        self.dominio_actual = ""
        self.puntuacion_actual = 0
        self.conteo_severidad = {}
        
        if mostrar_mensaje:
            self.frame_resultados.mostrar_mensaje(f"\n{MESSAGES['cleaned']}")
            self.frame_pie.establecer_estado(MESSAGES["ready"])
        else:
            self.frame_resultados.mostrar_mensaje(f"\n{MESSAGES['analyzing']}")
        
        self.frame_pie.habilitar_guardar(False)
        self.frame_pie.establecer_progreso(0)
    
    def guardar_informe(self):
        """Guarda el informe en un archivo"""
        if not self.informe_completo:
            messagebox.showwarning("Aviso", MESSAGES["no_report"])
            return
        
        # Obtener nombre de archivo por defecto
        dominio = self.frame_entrada.obtener_dominio()
        dominio_limpio = "".join(c if c.isalnum() else "_" for c in dominio)
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_default = f"informe_fijaten_{dominio_limpio}_{fecha}.txt"
        
        # Diálogo para guardar
        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile=nombre_default,
            filetypes=[
                ("Archivo de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if ruta_archivo:
            try:
                with open(ruta_archivo, 'w', encoding='utf-8') as f:
                    f.write(self.informe_completo)
                messagebox.showinfo("Éxito", f"Informe guardado en:\n{ruta_archivo}")
                self.frame_pie.establecer_estado(f"✅ Informe guardado: {os.path.basename(ruta_archivo)}")
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo guardar el informe:\n{str(e)}")
    
    # ═══════════════════════════════════════════════════════════════════
    # EXPORTACIÓN
    # ═══════════════════════════════════════════════════════════════════
    
    def exportar_pdf(self):
        """Exporta el informe a PDF"""
        if not self.vulnerabilidades and not self.dominio_actual:
            messagebox.showwarning("Aviso", "No hay resultados para exportar.\nRealiza un escaneo primero.")
            return
        
        # Verificar si reportlab está instalado
        if not self.exportador_pdf.esta_disponible():
            respuesta = messagebox.askyesno(
                "Dependencia Requerida",
                "Para exportar a PDF necesitas instalar 'reportlab'.\n\n"
                "¿Deseas ver las instrucciones de instalación?"
            )
            if respuesta:
                messagebox.showinfo(
                    "Instrucciones",
                    "Ejecuta el siguiente comando:\n\n"
                    "pip install reportlab\n\n"
                    "Después reinicia la aplicación."
                )
            return
        
        # Nombre de archivo
        dominio_limpio = "".join(c if c.isalnum() else "_" for c in self.dominio_actual)
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_default = f"informe_fijaten_{dominio_limpio}_{fecha}.pdf"
        
        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            initialfile=nombre_default,
            filetypes=[("Archivo PDF", "*.pdf")]
        )
        
        if ruta_archivo:
            try:
                self.frame_pie.establecer_estado("📄 Generando PDF...")
                self.update()
                
                self.exportador_pdf.exportar(
                    ruta_archivo,
                    self.dominio_actual,
                    self.vulnerabilidades,
                    self.info_sitio,
                    self.puntuacion_actual,
                    self.conteo_severidad
                )
                
                messagebox.showinfo("Éxito", f"PDF exportado correctamente:\n{ruta_archivo}")
                self.frame_pie.establecer_estado(f"✅ PDF exportado: {os.path.basename(ruta_archivo)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar a PDF:\n{str(e)}")
                self.frame_pie.establecer_estado("❌ Error al exportar PDF")
    
    def exportar_html(self):
        """Exporta el informe a HTML"""
        if not self.vulnerabilidades and not self.dominio_actual:
            messagebox.showwarning("Aviso", "No hay resultados para exportar.\nRealiza un escaneo primero.")
            return
        
        # Nombre de archivo
        dominio_limpio = "".join(c if c.isalnum() else "_" for c in self.dominio_actual)
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_default = f"informe_fijaten_{dominio_limpio}_{fecha}.html"
        
        ruta_archivo = filedialog.asksaveasfilename(
            defaultextension=".html",
            initialfile=nombre_default,
            filetypes=[("Archivo HTML", "*.html")]
        )
        
        if ruta_archivo:
            try:
                self.frame_pie.establecer_estado("🌐 Generando HTML...")
                self.update()
                
                self.exportador_html.exportar(
                    ruta_archivo,
                    self.dominio_actual,
                    self.vulnerabilidades,
                    self.info_sitio,
                    self.puntuacion_actual,
                    self.conteo_severidad
                )
                
                messagebox.showinfo("Éxito", f"HTML exportado correctamente:\n{ruta_archivo}")
                self.frame_pie.establecer_estado(f"✅ HTML exportado: {os.path.basename(ruta_archivo)}")
                
                # Preguntar si abrir en navegador
                if messagebox.askyesno("Abrir", "¿Deseas abrir el informe en el navegador?"):
                    import webbrowser
                    webbrowser.open(f"file://{ruta_archivo}")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo exportar a HTML:\n{str(e)}")
                self.frame_pie.establecer_estado("❌ Error al exportar HTML")
    
    def mostrar_historial(self):
        """Muestra el diálogo de historial de escaneos"""
        dominio_actual = self.frame_entrada.obtener_dominio()
        DialogoHistorial(self, dominio_actual=dominio_actual)
