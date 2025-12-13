"""
Fijaten-WP - Diálogo de Atajos de Teclado
Muestra los atajos de teclado disponibles en la aplicación
"""

import customtkinter as ctk
import platform


class DialogoAtajos(ctk.CTkToplevel):
    """Diálogo que muestra los atajos de teclado disponibles"""
    
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configurar ventana
        self.title("⌨️ Atajos de Teclado - Fijaten-WP")
        self.geometry("500x450")
        self.resizable(False, False)
        
        # Hacer modal
        self.transient(parent)
        self.grab_set()
        
        # Centrar ventana
        self.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 450) // 2
        self.geometry(f"+{x}+{y}")
        
        # Determinar tecla modificadora según SO
        self.es_mac = platform.system() == "Darwin"
        self.mod_key = "Cmd" if self.es_mac else "Ctrl"
        
        # Crear contenido
        self._crear_contenido()
        
        # Cerrar con Escape
        self.bind("<Escape>", lambda e: self.destroy())
    
    def _crear_contenido(self):
        """Crea el contenido del diálogo"""
        
        # Frame principal con padding
        frame_principal = ctk.CTkFrame(self, fg_color="transparent")
        frame_principal.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Título
        ctk.CTkLabel(
            frame_principal,
            text="⌨️ Atajos de Teclado",
            font=ctk.CTkFont(size=22, weight="bold")
        ).pack(pady=(0, 5))
        
        # Subtítulo
        ctk.CTkLabel(
            frame_principal,
            text="Accesos rápidos disponibles en Fijaten-WP",
            font=ctk.CTkFont(size=12),
            text_color="gray"
        ).pack(pady=(0, 20))
        
        # Frame con scroll para los atajos
        frame_scroll = ctk.CTkScrollableFrame(
            frame_principal,
            fg_color="transparent"
        )
        frame_scroll.pack(fill="both", expand=True)
        frame_scroll.grid_columnconfigure(0, weight=1)
        frame_scroll.grid_columnconfigure(1, weight=2)
        
        # Definir atajos por categoría
        atajos = [
            ("📁 Archivo", [
                (f"{self.mod_key}+Q", "Salir de la aplicación"),
            ]),
            ("🔧 Herramientas", [
                (f"{self.mod_key}+M", "Abrir escaneo múltiple"),
            ]),
            ("⚙️ Preferencias", [
                (f"{self.mod_key}+O", "Abrir opciones de escaneo"),
                (f"{self.mod_key}+T", "Alternar modo claro/oscuro"),
            ]),
            ("❓ Ayuda", [
                ("F1", "Mostrar 'Acerca de'"),
                (f"{self.mod_key}+K", "Mostrar atajos de teclado"),
            ]),
            ("🔍 Escaneo", [
                ("Enter", "Iniciar escaneo (en campo de dominio)"),
                ("Escape", "Cerrar ventanas flotantes"),
            ]),
        ]
        
        fila = 0
        for categoria, lista_atajos in atajos:
            # Cabecera de categoría
            frame_cat = ctk.CTkFrame(frame_scroll, fg_color=("gray85", "gray20"))
            frame_cat.grid(row=fila, column=0, columnspan=2, sticky="ew", pady=(10, 5), padx=5)
            
            ctk.CTkLabel(
                frame_cat,
                text=categoria,
                font=ctk.CTkFont(size=14, weight="bold")
            ).pack(anchor="w", padx=10, pady=5)
            
            fila += 1
            
            # Atajos de esta categoría
            for tecla, descripcion in lista_atajos:
                # Frame para cada atajo
                frame_atajo = ctk.CTkFrame(frame_scroll, fg_color="transparent")
                frame_atajo.grid(row=fila, column=0, columnspan=2, sticky="ew", padx=10, pady=2)
                frame_atajo.grid_columnconfigure(1, weight=1)
                
                # Tecla (badge)
                etiqueta_tecla = ctk.CTkLabel(
                    frame_atajo,
                    text=f" {tecla} ",
                    font=ctk.CTkFont(family="Consolas", size=12, weight="bold"),
                    fg_color=("gray75", "gray30"),
                    corner_radius=5,
                    width=100
                )
                etiqueta_tecla.grid(row=0, column=0, padx=(0, 15), pady=3, sticky="w")
                
                # Descripción
                ctk.CTkLabel(
                    frame_atajo,
                    text=descripcion,
                    font=ctk.CTkFont(size=12),
                    anchor="w"
                ).grid(row=0, column=1, sticky="w", pady=3)
                
                fila += 1
        
        # Nota sobre el sistema operativo
        sistema = platform.system()
        if sistema == "Darwin":
            nota_so = "💻 macOS: Usa ⌘ (Command) en lugar de Ctrl"
        elif sistema == "Windows":
            nota_so = "💻 Windows: Usa Ctrl para los atajos"
        else:
            nota_so = "💻 Linux: Usa Ctrl para los atajos"
        
        ctk.CTkLabel(
            frame_principal,
            text=nota_so,
            font=ctk.CTkFont(size=11),
            text_color="gray"
        ).pack(pady=(15, 10))
        
        # Botón cerrar
        ctk.CTkButton(
            frame_principal,
            text="Cerrar",
            width=120,
            command=self.destroy
        ).pack(pady=(5, 0))
