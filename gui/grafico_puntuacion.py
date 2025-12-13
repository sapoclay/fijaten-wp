"""
Fijaten-WP - Gráfico de Puntuación
Widget de visualización circular de la puntuación de seguridad
"""

import customtkinter as ctk
import math
from typing import Optional


class GraficoPuntuacion(ctk.CTkCanvas):
    """Widget que muestra un gráfico circular de la puntuación de seguridad"""
    
    def __init__(self, parent, tamanio: int = 200, **kwargs):
        """
        Inicializa el gráfico de puntuación
        
        Args:
            parent: Widget padre
            tamanio: Tamaño del gráfico en píxeles
        """
        # Configurar fondo transparente
        super().__init__(
            parent, 
            width=tamanio, 
            height=tamanio,
            highlightthickness=0,
            **kwargs
        )
        
        self.tamanio = tamanio
        self.puntuacion = 0
        self.animando = False
        self.puntuacion_objetivo = 0
        
        # Colores para el tema
        self._actualizar_colores()
        
        # Dibujar estado inicial
        self._dibujar(0)
        
        # Vincular cambio de tema
        self.bind("<Configure>", lambda e: self._dibujar(int(self.puntuacion)))
    
    def _actualizar_colores(self):
        """Actualiza los colores según el tema actual"""
        modo = ctk.get_appearance_mode()
        if modo == "Dark":
            self.color_fondo = "#1a1a2e"
            self.color_anillo_fondo = "#2d2d44"
            self.color_texto = "#ffffff"
            self.color_texto_secundario = "#a0a0a0"
        else:
            self.color_fondo = "#f8fafc"
            self.color_anillo_fondo = "#e2e8f0"
            self.color_texto = "#1e293b"
            self.color_texto_secundario = "#64748b"
    
    def _obtener_color_puntuacion(self, puntuacion: int) -> str:
        """Obtiene el color según la puntuación"""
        if puntuacion >= 80:
            return "#16a34a"  # Verde
        elif puntuacion >= 60:
            return "#ca8a04"  # Amarillo/Dorado
        elif puntuacion >= 40:
            return "#ea580c"  # Naranja
        else:
            return "#dc2626"  # Rojo
    
    def _obtener_estado(self, puntuacion: int) -> str:
        """Obtiene el texto de estado según la puntuación"""
        if puntuacion >= 90:
            return "EXCELENTE"
        elif puntuacion >= 80:
            return "MUY BUENO"
        elif puntuacion >= 70:
            return "BUENO"
        elif puntuacion >= 60:
            return "ACEPTABLE"
        elif puntuacion >= 40:
            return "MEJORABLE"
        elif puntuacion >= 20:
            return "DEFICIENTE"
        else:
            return "CRÍTICO"
    
    def _dibujar(self, puntuacion: int):
        """Dibuja el gráfico con la puntuación indicada"""
        self._actualizar_colores()
        self.delete("all")
        
        centro_x = self.tamanio / 2
        centro_y = self.tamanio / 2
        radio_externo = self.tamanio / 2 - 10
        radio_interno = radio_externo - 20
        
        # Fondo del canvas
        self.configure(bg=self.color_fondo)
        
        # Dibujar anillo de fondo (gris)
        self._dibujar_arco(
            centro_x, centro_y, 
            radio_externo, radio_interno,
            0, 360,
            self.color_anillo_fondo
        )
        
        # Dibujar arco de progreso
        if puntuacion > 0:
            color = self._obtener_color_puntuacion(puntuacion)
            angulo = (puntuacion / 100) * 360
            self._dibujar_arco(
                centro_x, centro_y,
                radio_externo, radio_interno,
                90, 90 - angulo,  # Empezar desde arriba, ir en sentido horario
                color
            )
        
        # Texto de puntuación en el centro
        color_puntuacion = self._obtener_color_puntuacion(puntuacion)
        self.create_text(
            centro_x, centro_y - 10,
            text=str(int(puntuacion)),
            font=("Helvetica", int(self.tamanio / 5), "bold"),
            fill=color_puntuacion
        )
        
        # Texto "/100"
        self.create_text(
            centro_x, centro_y + 20,
            text="/100",
            font=("Helvetica", int(self.tamanio / 12)),
            fill=self.color_texto_secundario
        )
        
        # Texto de estado
        estado = self._obtener_estado(int(puntuacion))
        self.create_text(
            centro_x, centro_y + 45,
            text=estado,
            font=("Helvetica", int(self.tamanio / 18), "bold"),
            fill=color_puntuacion
        )
    
    def _dibujar_arco(self, cx: float, cy: float, 
                      r_ext: float, r_int: float,
                      angulo_inicio: float, angulo_fin: float,
                      color: str):
        """Dibuja un arco gordo"""
        # Número de segmentos para suavizar el arco
        segmentos = max(36, int(abs(angulo_inicio - angulo_fin) / 2))
        
        if angulo_inicio > angulo_fin:
            # Sentido horario
            paso = (angulo_inicio - angulo_fin) / segmentos
            angulos = [angulo_inicio - i * paso for i in range(segmentos + 1)]
        else:
            # Sentido antihorario
            paso = (angulo_fin - angulo_inicio) / segmentos
            angulos = [angulo_inicio + i * paso for i in range(segmentos + 1)]
        
        # Crear polígono para el arco
        puntos_externos = []
        puntos_internos = []
        
        for angulo in angulos:
            rad = math.radians(angulo)
            # Punto externo
            px_ext = cx + r_ext * math.cos(rad)
            py_ext = cy - r_ext * math.sin(rad)
            puntos_externos.append((px_ext, py_ext))
            # Punto interno
            px_int = cx + r_int * math.cos(rad)
            py_int = cy - r_int * math.sin(rad)
            puntos_internos.append((px_int, py_int))
        
        # Combinar puntos para formar el polígono
        puntos = puntos_externos + puntos_internos[::-1]
        
        if len(puntos) >= 3:
            coords = []
            for p in puntos:
                coords.extend(p)
            self.create_polygon(coords, fill=color, outline="", smooth=True)
    
    def establecer_puntuacion(self, puntuacion: int, animar: bool = True):
        """
        Establece la puntuación a mostrar
        
        Args:
            puntuacion: Valor de 0 a 100
            animar: Si True, anima la transición
        """
        puntuacion = max(0, min(100, puntuacion))
        
        if animar and not self.animando:
            self.puntuacion_objetivo = puntuacion
            self._animar()
        else:
            self.puntuacion = puntuacion
            self._dibujar(puntuacion)
    
    def _animar(self):
        """Anima la transición de puntuación"""
        self.animando = True
        
        diferencia = self.puntuacion_objetivo - self.puntuacion
        
        if abs(diferencia) < 1:
            self.puntuacion = self.puntuacion_objetivo
            self._dibujar(int(self.puntuacion))
            self.animando = False
            return
        
        # Velocidad de animación (más rápido al principio)
        velocidad = max(1, abs(diferencia) / 10)
        
        if diferencia > 0:
            self.puntuacion += velocidad
        else:
            self.puntuacion -= velocidad
        
        self._dibujar(int(self.puntuacion))
        
        # Continuar animación
        self.after(20, self._animar)
    
    def reiniciar(self):
        """Reinicia el gráfico a 0"""
        self.puntuacion = 0
        self.puntuacion_objetivo = 0
        self.animando = False
        self._dibujar(0)


class FrameGraficoPuntuacion(ctk.CTkFrame):
    """Frame que contiene el gráfico de puntuación con título"""
    
    def __init__(self, parent, tamanio: int = 180, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.grid_columnconfigure(0, weight=1)
        
        # Título
        self.label_titulo = ctk.CTkLabel(
            self,
            text="📊 Puntuación de seguridad",
            font=("", 14, "bold")
        )
        self.label_titulo.grid(row=0, column=0, pady=(10, 5))
        
        # Gráfico
        self.grafico = GraficoPuntuacion(self, tamanio=tamanio)
        self.grafico.grid(row=1, column=0, padx=10, pady=10)
        
        # Info adicional
        self.label_info = ctk.CTkLabel(
            self,
            text="",
            font=("", 11),
            text_color="gray"
        )
        self.label_info.grid(row=2, column=0, pady=(0, 10))
    
    def establecer_puntuacion(self, puntuacion: int, vulnerabilidades: int = 0,
                               animar: bool = True):
        """
        Establece la puntuación y muestra información adicional
        
        Args:
            puntuacion: Puntuación de 0 a 100
            vulnerabilidades: Número de vulnerabilidades encontradas
            animar: Si animar la transición
        """
        self.grafico.establecer_puntuacion(puntuacion, animar)
        
        if vulnerabilidades > 0:
            self.label_info.configure(text=f"🔍 {vulnerabilidades} vulnerabilidades encontradas")
        else:
            self.label_info.configure(text="✅ Sin vulnerabilidades conocidas detectadas")
    
    def reiniciar(self):
        """Reinicia el gráfico"""
        self.grafico.reiniciar()
        self.label_info.configure(text="")
