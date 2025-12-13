"""
Fijaten-WP - Diálogo de Opciones
Permite activar/desactivar las verificaciones del escáner
"""

import customtkinter as ctk
from tkinter import messagebox
import json
from pathlib import Path
from typing import Dict, Callable, Optional

# Ruta del archivo de configuración de opciones
CONFIG_FILE = Path(__file__).parent.parent / "opciones_escaneo.json"


# Definición de todas las opciones disponibles
OPCIONES_DISPONIBLES = {
    # Análisis básicos
    "detectar_version_wordpress": {
        "nombre": "Detectar versión de WordPress",
        "categoria": "Análisis Básicos",
        "descripcion": "Detecta si la versión de WordPress está expuesta",
        "activo": True
    },
    "verificar_ssl": {
        "nombre": "Verificar SSL/HTTPS",
        "categoria": "Análisis Básicos",
        "descripcion": "Comprueba el certificado SSL y redirección HTTPS",
        "activo": True
    },
    "verificar_xmlrpc": {
        "nombre": "Verificar XML-RPC",
        "categoria": "Análisis Básicos",
        "descripcion": "Detecta si XML-RPC está habilitado (riesgo de ataques)",
        "activo": True
    },
    "verificar_enumeracion_usuarios": {
        "nombre": "Enumeración de usuarios",
        "categoria": "Análisis Básicos",
        "descripcion": "Verifica si se pueden descubrir nombres de usuario",
        "activo": True
    },
    "verificar_wp_config_backup": {
        "nombre": "Backups de configuración",
        "categoria": "Análisis Básicos",
        "descripcion": "Busca archivos wp-config.php.bak expuestos",
        "activo": True
    },
    "verificar_debug_mode": {
        "nombre": "Modo Debug",
        "categoria": "Análisis Básicos",
        "descripcion": "Detecta si WP_DEBUG está activo",
        "activo": True
    },
    "verificar_listado_directorios": {
        "nombre": "Listado de directorios",
        "categoria": "Análisis Básicos",
        "descripcion": "Verifica si los directorios son listables",
        "activo": True
    },
    "verificar_plugins_vulnerables": {
        "nombre": "Analizar plugins",
        "categoria": "Análisis Básicos",
        "descripcion": "Detecta plugins instalados y versiones expuestas",
        "activo": True
    },
    "verificar_temas": {
        "nombre": "Analizar temas",
        "categoria": "Análisis Básicos",
        "descripcion": "Analiza el tema activo y su versión",
        "activo": True
    },
    "verificar_login_seguridad": {
        "nombre": "Seguridad del login",
        "categoria": "Análisis Básicos",
        "descripcion": "Verifica protecciones en la página de login",
        "activo": True
    },
    "verificar_rest_api": {
        "nombre": "REST API",
        "categoria": "Análisis Básicos",
        "descripcion": "Verifica exposición de la API REST",
        "activo": True
    },
    "verificar_cabeceras_seguridad": {
        "nombre": "Cabeceras HTTP",
        "categoria": "Análisis Básicos",
        "descripcion": "Verifica cabeceras de seguridad HTTP",
        "activo": True
    },
    "verificar_archivo_robots": {
        "nombre": "Archivo robots.txt",
        "categoria": "Análisis Básicos",
        "descripcion": "Detecta rutas sensibles expuestas en robots.txt",
        "activo": True
    },
    # Análisis avanzados
    "verificar_malware_conocido": {
        "nombre": "Detección de malware",
        "categoria": "Análisis Avanzados",
        "descripcion": "Busca patrones de código malicioso conocido",
        "activo": True
    },
    "verificar_permisos_archivos": {
        "nombre": "Permisos de archivos",
        "categoria": "Análisis Avanzados",
        "descripcion": "Verifica exposición de archivos críticos",
        "activo": True
    },
    "verificar_politica_contrasenas": {
        "nombre": "Política de contraseñas",
        "categoria": "Análisis Avanzados",
        "descripcion": "Analiza fortaleza requerida y CAPTCHA",
        "activo": True
    },
    "verificar_hotlinking": {
        "nombre": "Protección hotlinking",
        "categoria": "Análisis Avanzados",
        "descripcion": "Comprueba protección contra hotlinking de imágenes",
        "activo": True
    },
    "verificar_proteccion_csrf": {
        "nombre": "Protección CSRF",
        "categoria": "Análisis Avanzados",
        "descripcion": "Detecta formularios sin tokens de seguridad",
        "activo": True
    },
    # Análisis externos
    "verificar_cve_plugins_temas": {
        "nombre": "Base de datos CVE",
        "categoria": "Análisis Externos",
        "descripcion": "Consulta vulnerabilidades conocidas en plugins/temas",
        "activo": True
    },
    "verificar_listas_negras": {
        "nombre": "Listas negras (Blacklists)",
        "categoria": "Análisis Externos",
        "descripcion": "Verifica si el dominio está en blacklists de spam/malware",
        "activo": True
    },
    "analizar_informacion_dns": {
        "nombre": "Análisis DNS/WHOIS",
        "categoria": "Análisis Externos",
        "descripcion": "Obtiene información de registros DNS y DNSSEC",
        "activo": True
    },
    "detectar_waf": {
        "nombre": "Detección de WAF",
        "categoria": "Análisis Externos",
        "descripcion": "Detecta firewalls de aplicación web (Cloudflare, Sucuri, etc.)",
        "activo": True
    },
}


def cargar_opciones() -> Dict:
    """Carga las opciones guardadas o devuelve las predeterminadas"""
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                opciones_guardadas = json.load(f)
                # Combinar con opciones predeterminadas (por si hay nuevas)
                for clave, valor in OPCIONES_DISPONIBLES.items():
                    if clave not in opciones_guardadas:
                        opciones_guardadas[clave] = valor
                    else:
                        # Mantener el estado activo/inactivo guardado
                        opciones_guardadas[clave]["nombre"] = valor["nombre"]
                        opciones_guardadas[clave]["categoria"] = valor["categoria"]
                        opciones_guardadas[clave]["descripcion"] = valor["descripcion"]
                return opciones_guardadas
    except Exception:
        pass
    return OPCIONES_DISPONIBLES.copy()


def guardar_opciones(opciones: Dict):
    """Guarda las opciones en archivo"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(opciones, f, indent=2, ensure_ascii=False)
    except Exception as e:
        print(f"Error guardando opciones: {e}")


def obtener_verificaciones_activas() -> list:
    """Devuelve lista de nombres de verificaciones activas"""
    opciones = cargar_opciones()
    return [clave for clave, valor in opciones.items() if valor.get("activo", True)]


class DialogoOpciones(ctk.CTkToplevel):
    """Diálogo para configurar las opciones de escaneo"""
    
    def __init__(self, parent, on_save: Optional[Callable] = None):
        super().__init__(parent)
        
        self.parent = parent
        self.on_save = on_save
        self.opciones = cargar_opciones()
        self.checkboxes: Dict[str, ctk.CTkCheckBox] = {}
        
        # Configuración de la ventana
        self.title("Opciones de Escaneo")
        self.geometry("650x600")
        self.minsize(550, 500)
        
        # Hacerla modal
        self.transient(parent)
        self.grab_set()
        
        # Centrar en pantalla
        self.update_idletasks()
        x = (self.winfo_screenwidth() - 650) // 2
        y = (self.winfo_screenheight() - 600) // 2
        self.geometry(f"+{x}+{y}")
        
        # Crear interfaz
        self._crear_interfaz()
        
        # Focus
        self.focus_force()
    
    def _crear_interfaz(self):
        """Crea la interfaz del diálogo"""
        # Frame principal
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Título
        frame_titulo = ctk.CTkFrame(self, fg_color="transparent")
        frame_titulo.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        
        ctk.CTkLabel(
            frame_titulo,
            text="⚙️ Configurar Verificaciones",
            font=ctk.CTkFont(size=20, weight="bold")
        ).pack(anchor="w")
        
        ctk.CTkLabel(
            frame_titulo,
            text="Selecciona qué análisis realizar durante el escaneo",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(anchor="w", pady=(5, 0))
        
        # Frame scrollable para las opciones
        self.scroll_frame = ctk.CTkScrollableFrame(self, label_text="")
        self.scroll_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.scroll_frame.grid_columnconfigure(0, weight=1)
        
        # Agrupar opciones por categoría
        categorias = {}
        for clave, valor in self.opciones.items():
            categoria = valor.get("categoria", "Otros")
            if categoria not in categorias:
                categorias[categoria] = []
            categorias[categoria].append((clave, valor))
        
        # Crear secciones por categoría
        row = 0
        for categoria, items in categorias.items():
            # Encabezado de categoría
            frame_cat = ctk.CTkFrame(self.scroll_frame, fg_color=("gray85", "gray20"))
            frame_cat.grid(row=row, column=0, sticky="ew", pady=(10, 5))
            frame_cat.grid_columnconfigure(0, weight=1)
            
            ctk.CTkLabel(
                frame_cat,
                text=f"  {categoria}",
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w"
            ).grid(row=0, column=0, sticky="w", padx=10, pady=8)
            
            # Botones seleccionar/deseleccionar todo
            frame_btns = ctk.CTkFrame(frame_cat, fg_color="transparent")
            frame_btns.grid(row=0, column=1, sticky="e", padx=5)
            
            ctk.CTkButton(
                frame_btns,
                text="✓ Todo",
                width=60,
                height=24,
                font=ctk.CTkFont(size=11),
                command=lambda c=categoria: self._seleccionar_categoria(c, True)
            ).pack(side="left", padx=2)
            
            ctk.CTkButton(
                frame_btns,
                text="✗ Nada",
                width=60,
                height=24,
                font=ctk.CTkFont(size=11),
                fg_color="gray40",
                command=lambda c=categoria: self._seleccionar_categoria(c, False)
            ).pack(side="left", padx=2)
            
            row += 1
            
            # Opciones de la categoría
            for clave, valor in items:
                frame_opcion = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
                frame_opcion.grid(row=row, column=0, sticky="ew", padx=10, pady=2)
                frame_opcion.grid_columnconfigure(1, weight=1)
                
                # Variable para el checkbox
                var = ctk.BooleanVar(value=valor.get("activo", True))
                
                checkbox = ctk.CTkCheckBox(
                    frame_opcion,
                    text=valor["nombre"],
                    variable=var,
                    font=ctk.CTkFont(size=13),
                    command=lambda k=clave, v=var: self._actualizar_opcion(k, v.get())
                )
                checkbox.grid(row=0, column=0, sticky="w")
                
                self.checkboxes[clave] = checkbox
                
                # Descripción
                ctk.CTkLabel(
                    frame_opcion,
                    text=valor["descripcion"],
                    font=ctk.CTkFont(size=11),
                    text_color="gray",
                    anchor="w"
                ).grid(row=0, column=1, sticky="w", padx=(20, 0))
                
                row += 1
        
        # Frame de botones inferiores
        frame_botones = ctk.CTkFrame(self, fg_color="transparent")
        frame_botones.grid(row=2, column=0, sticky="ew", padx=20, pady=15)
        frame_botones.grid_columnconfigure(0, weight=1)
        
        # Botones de acción rápida
        frame_acciones = ctk.CTkFrame(frame_botones, fg_color="transparent")
        frame_acciones.grid(row=0, column=0, sticky="w")
        
        ctk.CTkButton(
            frame_acciones,
            text="Seleccionar Todo",
            width=130,
            command=lambda: self._seleccionar_todo(True)
        ).pack(side="left", padx=(0, 5))
        
        ctk.CTkButton(
            frame_acciones,
            text="Deseleccionar Todo",
            width=130,
            fg_color="gray40",
            command=lambda: self._seleccionar_todo(False)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_acciones,
            text="Restaurar",
            width=100,
            fg_color="orange",
            command=self._restaurar_predeterminados
        ).pack(side="left", padx=5)
        
        # Botones guardar/cancelar
        frame_guardar = ctk.CTkFrame(frame_botones, fg_color="transparent")
        frame_guardar.grid(row=0, column=1, sticky="e")
        
        ctk.CTkButton(
            frame_guardar,
            text="Cancelar",
            width=100,
            fg_color="gray40",
            command=self.destroy
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            frame_guardar,
            text="Guardar",
            width=100,
            fg_color="green",
            command=self._guardar_y_cerrar
        ).pack(side="left", padx=(5, 0))
    
    def _actualizar_opcion(self, clave: str, activo: bool):
        """Actualiza el estado de una opción"""
        if clave in self.opciones:
            self.opciones[clave]["activo"] = activo
    
    def _seleccionar_categoria(self, categoria: str, seleccionar: bool):
        """Selecciona o deselecciona todas las opciones de una categoría"""
        for clave, valor in self.opciones.items():
            if valor.get("categoria") == categoria:
                valor["activo"] = seleccionar
                if clave in self.checkboxes:
                    if seleccionar:
                        self.checkboxes[clave].select()
                    else:
                        self.checkboxes[clave].deselect()
    
    def _seleccionar_todo(self, seleccionar: bool):
        """Selecciona o deselecciona todas las opciones"""
        for clave, valor in self.opciones.items():
            valor["activo"] = seleccionar
            if clave in self.checkboxes:
                if seleccionar:
                    self.checkboxes[clave].select()
                else:
                    self.checkboxes[clave].deselect()
    
    def _restaurar_predeterminados(self):
        """Restaura las opciones predeterminadas"""
        self.opciones = OPCIONES_DISPONIBLES.copy()
        for clave in self.opciones:
            self.opciones[clave]["activo"] = True
            if clave in self.checkboxes:
                self.checkboxes[clave].select()
        messagebox.showinfo("Restaurado", "Se han restaurado las opciones predeterminadas.")
    
    def _guardar_y_cerrar(self):
        """Guarda las opciones y cierra el diálogo"""
        guardar_opciones(self.opciones)
        
        # Contar opciones activas
        activas = sum(1 for v in self.opciones.values() if v.get("activo", True))
        total = len(self.opciones)
        
        if self.on_save:
            self.on_save()
        
        messagebox.showinfo(
            "Opciones Guardadas",
            f"Se guardaron las preferencias.\n\n"
            f"Verificaciones activas: {activas}/{total}"
        )
        self.destroy()
