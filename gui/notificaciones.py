"""
Fijaten-WP - Sistema de Notificaciones de Escritorio
Envía alertas cuando finalizan los escaneos
"""

import platform
import subprocess
import json
from pathlib import Path

# Archivo de configuración de notificaciones
ARCHIVO_CONFIG_NOTIF = Path(__file__).parent.parent / "notificaciones_config.json"


class NotificadorEscritorio:
    """Gestiona las notificaciones de escritorio multiplataforma"""
    
    _instancia = None
    
    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializado = False
        return cls._instancia
    
    def __init__(self):
        if self._inicializado:
            return
        self._inicializado = True
        self._cargar_configuracion()
    
    def _cargar_configuracion(self):
        """Carga la configuración de notificaciones"""
        self.habilitadas = True
        self.sonido = True
        
        try:
            if ARCHIVO_CONFIG_NOTIF.exists():
                with open(ARCHIVO_CONFIG_NOTIF, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self.habilitadas = config.get("habilitadas", True)
                    self.sonido = config.get("sonido", True)
        except Exception:
            pass
    
    def _guardar_configuracion(self):
        """Guarda la configuración de notificaciones"""
        try:
            config = {
                "habilitadas": self.habilitadas,
                "sonido": self.sonido
            }
            with open(ARCHIVO_CONFIG_NOTIF, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception:
            pass
    
    def establecer_habilitadas(self, valor: bool):
        """Habilita o deshabilita las notificaciones"""
        self.habilitadas = valor
        self._guardar_configuracion()
    
    def establecer_sonido(self, valor: bool):
        """Habilita o deshabilita el sonido"""
        self.sonido = valor
        self._guardar_configuracion()
    
    def estan_habilitadas(self) -> bool:
        """Retorna si las notificaciones están habilitadas"""
        return self.habilitadas
    
    def sonido_habilitado(self) -> bool:
        """Retorna si el sonido está habilitado"""
        return self.sonido
    
    def notificar(self, titulo: str, mensaje: str, tipo: str = "info") -> bool:
        """
        Envía una notificación de escritorio
        
        Args:
            titulo: Título de la notificación
            mensaje: Mensaje de la notificación
            tipo: Tipo de notificación (info, warning, error, success)
        
        Devuelve:
            True si la notificación se envió correctamente
        """
        if not self.habilitadas:
            return False
        
        sistema = platform.system().lower()
        
        try:
            if sistema == "linux":
                return self._notificar_linux(titulo, mensaje, tipo)
            elif sistema == "darwin":  # macOS
                return self._notificar_macos(titulo, mensaje)
            elif sistema == "windows":
                return self._notificar_windows(titulo, mensaje, tipo)
            else:
                return False
        except Exception:
            return False
    
    def _notificar_linux(self, titulo: str, mensaje: str, tipo: str) -> bool:
        """Envía notificación en Linux usando notify-send"""
        # Determinar icono según tipo
        iconos = {
            "info": "dialog-information",
            "warning": "dialog-warning",
            "error": "dialog-error",
            "success": "emblem-default"
        }
        icono = iconos.get(tipo, "dialog-information")
        
        # Intentar notify-send
        try:
            cmd = [
                "notify-send",
                "-a", "Fijaten-WP",
                "-i", icono,
                "-u", "normal",
                titulo,
                mensaje
            ]
            subprocess.run(cmd, capture_output=True, timeout=5)
            
            # Reproducir sonido si está habilitado
            if self.sonido:
                self._reproducir_sonido_linux()
            
            return True
        except FileNotFoundError:
            # notify-send no está instalado, intentar zenity
            try:
                cmd = [
                    "zenity",
                    "--notification",
                    f"--text={titulo}\n{mensaje}"
                ]
                subprocess.run(cmd, capture_output=True, timeout=5)
                return True
            except Exception:
                return False
        except Exception:
            return False
    
    def _reproducir_sonido_linux(self):
        """Reproduce un sonido de notificación en Linux"""
        try:
            # Intentar varios métodos
            sonidos = [
                "/usr/share/sounds/freedesktop/stereo/complete.oga",
                "/usr/share/sounds/freedesktop/stereo/message.oga",
                "/usr/share/sounds/sound-icons/glass-water-1.wav"
            ]
            
            for sonido in sonidos:
                if Path(sonido).exists():
                    subprocess.Popen(
                        ["paplay", sonido],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    break
        except Exception:
            pass
    
    def _notificar_macos(self, titulo: str, mensaje: str) -> bool:
        """Envía notificación en macOS usando osascript"""
        try:
            script = f'''
            display notification "{mensaje}" with title "{titulo}" sound name "Glass"
            '''
            subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                timeout=5
            )
            return True
        except Exception:
            return False
    
    def _notificar_windows(self, titulo: str, mensaje: str, tipo: str) -> bool:
        """Envía notificación en Windows usando PowerShell o win10toast"""
        try:
            # Intentar con win10toast si está instalado
            try:
                from win10toast import ToastNotifier  # type: ignore
                toaster = ToastNotifier()
                toaster.show_toast(
                    titulo,
                    mensaje,
                    duration=5,
                    threaded=True
                )
                return True
            except ImportError:
                pass
            
            # Usar PowerShell como alternativa
            script = f'''
            [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
            [Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null
            
            $template = @"
            <toast>
                <visual>
                    <binding template="ToastText02">
                        <text id="1">{titulo}</text>
                        <text id="2">{mensaje}</text>
                    </binding>
                </visual>
                <audio src="ms-winsoundevent:Notification.Default"/>
            </toast>
"@
            
            $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
            $xml.LoadXml($template)
            $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
            [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Fijaten-WP").Show($toast)
            '''
            
            subprocess.run(
                ["powershell", "-Command", script],
                capture_output=True,
                timeout=10
            )
            return True
            
        except Exception:
            # Método de respaldo: MessageBox
            try:
                import ctypes
                ctypes.windll.user32.MessageBoxW(0, mensaje, titulo, 0x40)  # type: ignore
                return True
            except Exception:
                return False


# Instancia global del notificador
notificador = NotificadorEscritorio()


def obtener_notificador() -> NotificadorEscritorio:
    """Obtiene la instancia del notificador"""
    return notificador


def notificar_escaneo_completado(dominio: str, vulnerabilidades: int, puntuacion: int):
    """Envía notificación de escaneo completado"""
    tipo = "success" if puntuacion >= 70 else "warning" if puntuacion >= 40 else "error"
    
    notificador.notificar(
        titulo="🔒 Escaneo completado - Fijaten-WP",
        mensaje=f"Sitio: {dominio}\nVulnerabilidades: {vulnerabilidades}\nPuntuación: {puntuacion}/100",
        tipo=tipo
    )
