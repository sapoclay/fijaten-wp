"""
Fijaten-WP - Diálogo de Escaneo Múltiple
Permite analizar varios sitios WordPress a la vez
"""

import customtkinter as ctk
from tkinter import filedialog, messagebox
import threading
from typing import Callable, List, Optional, Dict
from datetime import datetime
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from scanner.analizador_vulnerabilidades import AnalizadorWordPress
from scanner.generador_informes import GeneradorInformes
from gui.dialogo_opciones import obtener_verificaciones_activas


class DialogoEscaneoMultiple(ctk.CTkToplevel):
    """Diálogo para escanear múltiples sitios WordPress"""
    
    def __init__(self, parent, al_completar: Optional[Callable] = None):
        super().__init__(parent)
        
        self.parent = parent
        self.al_completar = al_completar
        self.dominios: List[str] = []
        self.resultados: Dict[str, dict] = {}
        self.escaneando = False
        self.cancelado = False
        self.hilo_actual = None
        
        # Configurar ventana
        self.title("🌐 Escaneo Múltiple - Fijaten-WP")
        self.geometry("700x600")
        self.minsize(600, 500)
        
        # Hacer modal
        self.transient(parent)
        self.grab_set()
        
        # Centrar ventana
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 700) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 600) // 2
        self.geometry(f"+{x}+{y}")
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Manejar cierre
        self.protocol("WM_DELETE_WINDOW", self._al_cerrar)
    
    def _crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        
        # ════════════════════════════════════════════════════════════
        # FRAME DE ENTRADA DE DOMINIOS
        # ════════════════════════════════════════════════════════════
        frame_entrada = ctk.CTkFrame(self)
        frame_entrada.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        frame_entrada.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame_entrada,
            text="📝 Añadir Dominios",
            font=ctk.CTkFont(size=16, weight="bold")
        ).grid(row=0, column=0, columnspan=3, sticky="w", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            frame_entrada,
            text="Introduce un dominio y pulsa 'Añadir', o carga desde archivo",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).grid(row=1, column=0, columnspan=3, sticky="w", padx=15, pady=(0, 10))
        
        # Entry para dominio
        self.entrada_dominio = ctk.CTkEntry(
            frame_entrada,
            placeholder_text="ejemplo.com o https://ejemplo.com",
            height=35
        )
        self.entrada_dominio.grid(row=2, column=0, sticky="ew", padx=(15, 10), pady=10)
        self.entrada_dominio.bind("<Return>", lambda e: self._anadir_dominio())
        
        # Botón añadir
        self.boton_anadir = ctk.CTkButton(
            frame_entrada,
            text="➕ Añadir",
            width=100,
            height=35,
            command=self._anadir_dominio
        )
        self.boton_anadir.grid(row=2, column=1, padx=5, pady=10)
        
        # Botón cargar archivo
        self.boton_cargar = ctk.CTkButton(
            frame_entrada,
            text="📂 Cargar Lista",
            width=120,
            height=35,
            fg_color="gray",
            hover_color="darkgray",
            command=self._cargar_archivo
        )
        self.boton_cargar.grid(row=2, column=2, padx=(5, 15), pady=10)
        
        # ════════════════════════════════════════════════════════════
        # LISTA DE DOMINIOS
        # ════════════════════════════════════════════════════════════
        frame_lista = ctk.CTkFrame(self)
        frame_lista.grid(row=1, column=0, sticky="ew", padx=20, pady=5)
        frame_lista.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(
            frame_lista,
            text="📋 Dominios en Cola",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))
        
        self.etiqueta_contador = ctk.CTkLabel(
            frame_lista,
            text="0 dominios",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        )
        self.etiqueta_contador.grid(row=0, column=1, sticky="e", padx=15, pady=(10, 5))
        
        # Frame con scroll para lista de dominios
        self.frame_scroll_dominios = ctk.CTkScrollableFrame(
            frame_lista,
            height=100
        )
        self.frame_scroll_dominios.grid(row=1, column=0, columnspan=2, sticky="ew", padx=15, pady=(5, 10))
        self.frame_scroll_dominios.grid_columnconfigure(0, weight=1)
        
        # Botón limpiar lista
        self.boton_limpiar = ctk.CTkButton(
            frame_lista,
            text="🗑️ Limpiar Lista",
            width=120,
            height=30,
            fg_color="gray",
            hover_color="darkgray",
            command=self._limpiar_lista
        )
        self.boton_limpiar.grid(row=2, column=0, columnspan=2, pady=(5, 10))
        
        # ════════════════════════════════════════════════════════════
        # ÁREA DE RESULTADOS
        # ════════════════════════════════════════════════════════════
        frame_resultados = ctk.CTkFrame(self)
        frame_resultados.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)
        frame_resultados.grid_columnconfigure(0, weight=1)
        frame_resultados.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_resultados,
            text="📊 Resultados",
            font=ctk.CTkFont(size=14, weight="bold")
        ).grid(row=0, column=0, sticky="w", padx=15, pady=(10, 5))
        
        self.texto_resultados = ctk.CTkTextbox(
            frame_resultados,
            font=ctk.CTkFont(family="Consolas", size=12),
            state="disabled"  # Solo lectura
        )
        self.texto_resultados.grid(row=1, column=0, sticky="nsew", padx=15, pady=(5, 15))
        self._escribir_resultados("Los resultados del escaneo aparecerán aquí...")
        
        # ════════════════════════════════════════════════════════════
        # BARRA DE PROGRESO Y ESTADO
        # ════════════════════════════════════════════════════════════
        frame_progreso = ctk.CTkFrame(self)
        frame_progreso.grid(row=3, column=0, sticky="ew", padx=20, pady=5)
        frame_progreso.grid_columnconfigure(0, weight=1)
        
        self.barra_progreso = ctk.CTkProgressBar(frame_progreso)
        self.barra_progreso.grid(row=0, column=0, sticky="ew", padx=15, pady=(10, 5))
        self.barra_progreso.set(0)
        
        self.etiqueta_progreso = ctk.CTkLabel(
            frame_progreso,
            text="Listo para escanear",
            font=ctk.CTkFont(size=12)
        )
        self.etiqueta_progreso.grid(row=1, column=0, sticky="w", padx=15, pady=(0, 10))
        
        # ════════════════════════════════════════════════════════════
        # BOTONES DE ACCIÓN
        # ════════════════════════════════════════════════════════════
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.grid(row=4, column=0, sticky="ew", padx=20, pady=(10, 20))
        
        self.boton_iniciar = ctk.CTkButton(
            frame_botones,
            text="🚀 Iniciar Escaneo",
            width=150,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._iniciar_escaneo
        )
        self.boton_iniciar.pack(side="left", padx=5)
        
        self.boton_cancelar = ctk.CTkButton(
            frame_botones,
            text="⛔ Cancelar",
            width=120,
            height=40,
            fg_color="red",
            hover_color="darkred",
            state="disabled",
            command=self._cancelar_escaneo
        )
        self.boton_cancelar.pack(side="left", padx=5)
        
        self.boton_guardar = ctk.CTkButton(
            frame_botones,
            text="💾 Guardar Informes",
            width=150,
            height=40,
            fg_color="gray",
            state="disabled",
            command=self._guardar_informes
        )
        self.boton_guardar.pack(side="left", padx=5)
        
        self.boton_cerrar = ctk.CTkButton(
            frame_botones,
            text="Cerrar",
            width=100,
            height=40,
            fg_color="gray",
            hover_color="darkgray",
            command=self._al_cerrar
        )
        self.boton_cerrar.pack(side="right", padx=5)
    
    def _anadir_dominio(self):
        """Añade un dominio a la lista"""
        dominio = self.entrada_dominio.get().strip()
        
        if not dominio:
            return
        
        # Normalizar dominio
        if not dominio.startswith(('http://', 'https://')):
            dominio = f"https://{dominio}"
        
        # Extraer solo el dominio
        dominio_limpio = dominio.replace('https://', '').replace('http://', '').rstrip('/')
        
        if dominio_limpio in self.dominios:
            messagebox.showwarning("Aviso", f"El dominio '{dominio_limpio}' ya está en la lista")
            return
        
        self.dominios.append(dominio_limpio)
        self._actualizar_lista_visual()
        self.entrada_dominio.delete(0, "end")
    
    def _cargar_archivo(self):
        """Carga dominios desde un archivo de texto"""
        ruta = filedialog.askopenfilename(
            title="Seleccionar archivo con dominios",
            filetypes=[
                ("Archivos de texto", "*.txt"),
                ("Todos los archivos", "*.*")
            ]
        )
        
        if ruta:
            try:
                with open(ruta, 'r', encoding='utf-8') as f:
                    lineas = f.readlines()
                
                nuevos = 0
                for linea in lineas:
                    dominio = linea.strip()
                    if dominio and not dominio.startswith('#'):
                        if not dominio.startswith(('http://', 'https://')):
                            dominio = dominio
                        dominio_limpio = dominio.replace('https://', '').replace('http://', '').rstrip('/')
                        if dominio_limpio and dominio_limpio not in self.dominios:
                            self.dominios.append(dominio_limpio)
                            nuevos += 1
                
                self._actualizar_lista_visual()
                messagebox.showinfo("Cargado", f"Se añadieron {nuevos} dominios nuevos")
                
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo cargar el archivo:\n{str(e)}")
    
    def _actualizar_lista_visual(self):
        """Actualiza la visualización de la lista de dominios"""
        # Limpiar frame
        for widget in self.frame_scroll_dominios.winfo_children():
            widget.destroy()
        
        # Crear widgets para cada dominio
        for i, dominio in enumerate(self.dominios):
            frame_item = ctk.CTkFrame(self.frame_scroll_dominios, fg_color="transparent")
            frame_item.grid(row=i, column=0, sticky="ew", pady=2)
            frame_item.grid_columnconfigure(0, weight=1)
            
            estado = self.resultados.get(dominio, {}).get('estado', 'pendiente')
            icono = "⏳" if estado == 'pendiente' else "✅" if estado == 'completado' else "❌"
            
            ctk.CTkLabel(
                frame_item,
                text=f"{icono} {dominio}",
                font=ctk.CTkFont(size=12)
            ).grid(row=0, column=0, sticky="w")
            
            boton_eliminar = ctk.CTkButton(
                frame_item,
                text="✖",
                width=25,
                height=25,
                fg_color="transparent",
                hover_color="red",
                text_color="gray",
                command=lambda d=dominio: self._eliminar_dominio(d)
            )
            boton_eliminar.grid(row=0, column=1, padx=5)
        
        # Actualizar contador
        self.etiqueta_contador.configure(text=f"{len(self.dominios)} dominios")
    
    def _eliminar_dominio(self, dominio: str):
        """Elimina un dominio de la lista"""
        if dominio in self.dominios:
            self.dominios.remove(dominio)
            self._actualizar_lista_visual()
    
    def _limpiar_lista(self):
        """Limpia toda la lista de dominios"""
        if self.dominios and messagebox.askyesno("Confirmar", "¿Limpiar toda la lista de dominios?"):
            self.dominios = []
            self.resultados = {}
            self._actualizar_lista_visual()
            self._escribir_resultados("Los resultados del escaneo aparecerán aquí...")
    
    def _escribir_resultados(self, texto: str, limpiar: bool = True):
        """Escribe texto en el área de resultados (solo lectura)"""
        self.texto_resultados.configure(state="normal")
        if limpiar:
            self.texto_resultados.delete("1.0", "end")
        self.texto_resultados.insert("end" if not limpiar else "1.0", texto)
        self.texto_resultados.see("end")
        self.texto_resultados.configure(state="disabled")
    
    def _iniciar_escaneo(self):
        """Inicia el escaneo de todos los dominios"""
        if not self.dominios:
            messagebox.showwarning("Aviso", "Añade al menos un dominio para escanear")
            return
        
        if self.escaneando:
            return
        
        self.escaneando = True
        self.cancelado = False
        self.resultados = {}
        
        # Configurar UI
        self.boton_iniciar.configure(state="disabled")
        self.boton_cancelar.configure(state="normal")
        self.boton_guardar.configure(state="disabled")
        self.boton_anadir.configure(state="disabled")
        self.boton_cargar.configure(state="disabled")
        self.boton_limpiar.configure(state="disabled")
        
        self._escribir_resultados("🔄 Iniciando escaneo múltiple...\n\n")
        
        # Iniciar hilo de escaneo
        self.hilo_actual = threading.Thread(target=self._ejecutar_escaneo_multiple)
        self.hilo_actual.daemon = True
        self.hilo_actual.start()
    
    def _ejecutar_escaneo_multiple(self):
        """Ejecuta el escaneo de múltiples dominios"""
        total = len(self.dominios)
        verificaciones = obtener_verificaciones_activas()
        
        for i, dominio in enumerate(self.dominios):
            if self.cancelado:
                self.after(0, lambda: self._agregar_resultado(
                    "\n⛔ Escaneo cancelado por el usuario\n"
                ))
                break
            
            # Actualizar progreso
            progreso = i / total
            self.after(0, lambda p=progreso, d=dominio, idx=i+1, t=total: self._actualizar_progreso(
                p, f"Escaneando {idx}/{t}: {d}"
            ))
            
            try:
                self.after(0, lambda d=dominio: self._agregar_resultado(
                    f"{'─' * 50}\n🔍 Escaneando: {d}\n"
                ))
                
                # Crear analizador
                analizador = AnalizadorWordPress(
                    dominio,
                    callback=lambda msg, d=dominio: self.after(0, lambda: self._actualizar_progreso(
                        progreso, f"{d}: {msg}"
                    )),
                    verificaciones_activas=verificaciones
                )
                
                # Ejecutar escaneo
                vulnerabilidades, info_sitio = analizador.ejecutar_escaneo_completo()
                
                # Generar informe
                generador = GeneradorInformes(dominio, vulnerabilidades, info_sitio)
                puntuacion = generador.calcular_puntuacion_seguridad()
                
                # Guardar resultado
                self.resultados[dominio] = {
                    'estado': 'completado',
                    'vulnerabilidades': vulnerabilidades,
                    'info_sitio': info_sitio,
                    'puntuacion': puntuacion,
                    'informe': generador.generar_informe_completo()
                }
                
                # Mostrar resumen
                num_vulns = len(vulnerabilidades)
                self.after(0, lambda d=dominio, n=num_vulns, p=puntuacion: self._agregar_resultado(
                    f"   ✅ Completado: {n} vulnerabilidades | Puntuación: {p}/100\n"
                ))
                
            except Exception as e:
                self.resultados[dominio] = {
                    'estado': 'error',
                    'error': str(e)
                }
                self.after(0, lambda d=dominio, err=str(e): self._agregar_resultado(
                    f"   ❌ Error: {err}\n"
                ))
            
            # Actualizar lista visual
            self.after(0, self._actualizar_lista_visual)
        
        # Finalizar
        self.after(0, self._finalizar_escaneo_multiple)
    
    def _actualizar_progreso(self, valor: float, mensaje: str):
        """Actualiza la barra de progreso y mensaje"""
        self.barra_progreso.set(valor)
        self.etiqueta_progreso.configure(text=mensaje)
    
    def _agregar_resultado(self, texto: str):
        """Agrega texto al área de resultados"""
        self._escribir_resultados(texto, limpiar=False)
    
    def _cancelar_escaneo(self):
        """Cancela el escaneo en curso"""
        if self.escaneando:
            self.cancelado = True
            self.etiqueta_progreso.configure(text="Cancelando...")
    
    def _finalizar_escaneo_multiple(self):
        """Finaliza el escaneo múltiple"""
        self.escaneando = False
        
        # Restaurar UI
        self.boton_iniciar.configure(state="normal")
        self.boton_cancelar.configure(state="disabled")
        self.boton_anadir.configure(state="normal")
        self.boton_cargar.configure(state="normal")
        self.boton_limpiar.configure(state="normal")
        
        # Calcular resumen
        completados = sum(1 for r in self.resultados.values() if r.get('estado') == 'completado')
        errores = sum(1 for r in self.resultados.values() if r.get('estado') == 'error')
        total_vulns = sum(len(r.get('vulnerabilidades', [])) for r in self.resultados.values())
        
        resumen = f"""
{'═' * 50}
📊 RESUMEN DEL ESCANEO MÚLTIPLE
{'═' * 50}

   ✅ Sitios analizados correctamente: {completados}
   ❌ Sitios con errores: {errores}
   🔒 Total de vulnerabilidades encontradas: {total_vulns}

{'═' * 50}
"""
        self._agregar_resultado(resumen)
        
        # Actualizar progreso
        self.barra_progreso.set(1)
        self.etiqueta_progreso.configure(text=f"Completado: {completados} sitios analizados")
        
        # Habilitar guardar si hay resultados
        if completados > 0:
            self.boton_guardar.configure(state="normal", fg_color=["#3B8ED0", "#1F6AA5"])
        
        # Notificar callback si existe
        if self.al_completar:
            self.al_completar(self.resultados)
        
        # Enviar notificación de escritorio
        self._enviar_notificacion(completados, total_vulns)
    
    def _enviar_notificacion(self, sitios: int, vulnerabilidades: int):
        """Envía notificación de escritorio"""
        try:
            from gui.notificaciones import NotificadorEscritorio
            notificador = NotificadorEscritorio()
            notificador.notificar(
                titulo="Escaneo Múltiple Completado",
                mensaje=f"Se analizaron {sitios} sitios.\n{vulnerabilidades} vulnerabilidades encontradas.",
                tipo="info"
            )
        except Exception:
            pass
    
    def _guardar_informes(self):
        """Guarda todos los informes en una carpeta"""
        if not self.resultados:
            return
        
        # Seleccionar carpeta
        carpeta = filedialog.askdirectory(title="Seleccionar carpeta para guardar informes")
        
        if carpeta:
            try:
                fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
                guardados = 0
                
                for dominio, resultado in self.resultados.items():
                    if resultado.get('estado') == 'completado' and resultado.get('informe'):
                        dominio_limpio = "".join(c if c.isalnum() else "_" for c in dominio)
                        nombre = f"informe_{dominio_limpio}_{fecha}.txt"
                        ruta = os.path.join(carpeta, nombre)
                        
                        with open(ruta, 'w', encoding='utf-8') as f:
                            f.write(resultado['informe'])
                        guardados += 1
                
                messagebox.showinfo("Guardado", f"Se guardaron {guardados} informes en:\n{carpeta}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar informes:\n{str(e)}")
    
    def _al_cerrar(self):
        """Maneja el cierre del diálogo"""
        if self.escaneando:
            if not messagebox.askyesno("Confirmar", "Hay un escaneo en curso. ¿Cancelar y cerrar?"):
                return
            self.cancelado = True
        
        self.grab_release()
        self.destroy()
