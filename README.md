# 🔒 Fijaten-WP

Analizador de vulnerabilidades de WordPress con interfaz gráfica moderna.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)

## 📋 Descripción

Fijaten-WP permite analizar las vulnerabilidades más comunes y críticas de cualquier sitio WordPress. Genera informes claros y comprensibles tanto para usuarios técnicos como no técnicos.

## 🚀 Características

- **Interfaz gráfica moderna** con tema oscuro/claro y fácil de usar
- **Análisis no intrusivo** - Solo analiza información pública
- **Informes para todos** - Explicaciones simples y técnicas
- **Plan de acción prioritizado** - Sabe qué arreglar primero
- **Escaneo múltiple** - Analiza varios sitios WordPress a la vez
- **Barra de progreso detallada** - Muestra qué verificación se está ejecutando
- **Notificaciones de escritorio** - Alertas cuando termine el escaneo
- **Modo claro/oscuro** - Selector de tema en Preferencias > Apariencia
- **Menú de opciones** - Configura qué verificaciones ejecutar
- **Exportación de informes** - Guarda los resultados en archivo de texto
- **Enlaces CVE oficiales** - Links a NVD y MITRE para cada vulnerabilidad

## 🔍 Vulnerabilidades que analiza

### Análisis básicos
| Vulnerabilidad | Descripción |
|---------------|-------------|
| Versión de WordPress | Detecta si está expuesta o desactualizada |
| SSL/HTTPS | Verifica certificado y redirección |
| XML-RPC | Detecta si está habilitado (riesgo de ataques) |
| Enumeración de usuarios | Verifica si se pueden descubrir usuarios |
| Archivos expuestos | Busca wp-config.php.bak, debug.log, etc. |
| Modo Debug | Detecta si WP_DEBUG está activo |
| Listado de directorios | Verifica si los directorios son listables |
| Plugins | Detecta plugins y versiones expuestas |
| Temas | Analiza el tema activo y su versión |
| REST API | Verifica exposición de la API |
| Cabeceras HTTP | Verifica cabeceras de seguridad |
| Robots.txt | Detecta rutas sensibles expuestas |

### Análisis avanzados
| Vulnerabilidad | Descripción |
|---------------|-------------|
| 🦠 Detección de malware | Busca patrones de código malicioso conocido |
| 📁 Permisos de archivos | Verifica exposición de archivos críticos |
| 🔑 Política de contraseñas | Analiza fortaleza requerida y CAPTCHA |
| 🖼️ Protección hotlinking | Comprueba protección de imágenes |
| 🛡️ Protección CSRF | Detecta formularios sin tokens de seguridad |
| 🔐 Base de datos CVE | Consulta vulnerabilidades conocidas en plugins/temas |
| 📋 Listas negras | Verifica si el dominio está en blacklists de spam/malware |
| 🌐 Análisis DNS/WHOIS | Obtiene información de registros DNS y DNSSEC |
| 🛡️ Detección WAF | Detecta firewalls de aplicación web (Cloudflare, Sucuri, etc.) |

## 📦 Instalación

### Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación de dependencias

```bash
# Crear entorno virtual (recomendado)
python -m venv venv
source venv/bin/activate  # En Linux/Mac
# o
venv\Scripts\activate  # En Windows

# Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Uso

### Ejecutar la aplicación (recomendado)

```bash
python3 iniciar.py
```

Este script automáticamente:
- Crea el entorno virtual si no existe
- Instala las dependencias necesarias
- Verifica la versión de Python
- Ejecuta la aplicación

### Ejecutar directamente (si ya tienes las dependencias)

```bash
python3 main.py
```

### Instrucciones

1. **Introduce el dominio** en la barra superior
   - Ejemplo: `misitioweb.com` o `https://misitioweb.com`

2. **Haz clic en "Analizar"** o presiona Enter

3. **Espera** mientras se realiza el análisis (10-30 segundos)

4. **Revisa los resultados** en las diferentes pestañas:
   - **📊 Resumen**: Vista general con puntuación de seguridad
   - **🔍 Detalles**: Explicación simple de cada problema
   - **⚙️ Técnico**: Información técnica detallada
   - **✅ Plan de Acción**: Pasos ordenados por prioridad

5. **Guarda el informe** haciendo clic en "Guardar Informe"

## 🗂️ Estructura del proyecto

```
fijaten-wp/
├── iniciar.py                  # Script de inicio con verificaciones
├── main.py                     # Punto de entrada principal
├── configuracion.py            # Configuración centralizada
├── requirements.txt            # Dependencias
├── README.md
├── img/
│   └── logo.png                # Logo de la aplicación
├── gui/
│   ├── __init__.py
│   ├── ventana_principal.py    # Ventana principal
│   ├── dialogo_acerca.py       # Diálogo "Acerca de"
│   ├── dialogo_opciones.py     # Opciones de escaneo
│   ├── dialogo_escaneo_multiple.py  # Escaneo de múltiples sitios
│   ├── gestor_temas.py         # Gestión de tema claro/oscuro
│   ├── notificaciones.py       # Notificaciones de escritorio
│   ├── barra_menu.py           # Barra de menú
│   └── componentes.py          # Componentes reutilizables
└── scanner/
    ├── __init__.py
    ├── analizador_vulnerabilidades.py  # Motor de análisis
    ├── generador_informes.py           # Generación de informes
    ├── modelos.py                      # Modelos de datos
    ├── verificador_cve.py              # Verificación de CVEs
    ├── verificador_blacklist.py        # Verificación de listas negras
    ├── analizador_dns.py               # Análisis DNS/WHOIS
    └── detector_waf.py                 # Detección de WAF/CDN
```

## 📊 Niveles de severidad

| Icono | Nivel | Descripción |
|-------|-------|-------------|
| 🔴 | CRÍTICA | Requiere acción inmediata |
| 🟠 | ALTA | Importante, arreglar pronto |
| 🟡 | MEDIA | Mejora recomendada |
| 🟢 | BAJA | Mejora opcional |
| 🔵 | INFO | Información |

## ⌨️ Atajos de teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl+Q` | Salir de la aplicación |
| `Ctrl+O` | Abrir opciones de escaneo |
| `Ctrl+M` | Abrir escaneo múltiple |
| `Ctrl+T` | Alternar modo claro/oscuro |
| `Ctrl+K` | Mostrar atajos de teclado |
| `F1` | Mostrar "Acerca de" |
| `Enter` | Iniciar escaneo (en campo de dominio) |
| `Escape` | Cerrar ventanas flotantes |

> **Nota:** En macOS usa `Cmd` en lugar de `Ctrl`

## 📸 Capturas de pantalla

### Pantalla principal

```
╔═══════════════════════════════════════════════════════════╗
║  🔒 Fijaten-WP                                            ║
╠═══════════════════════════════════════════════════════════╣
║  Archivo | Herramientas | Preferencias | Ayuda            ║
╠═══════════════════════════════════════════════════════════╣
║  🌐 Dominio: [ejemplo.com_________________] [🔍 Analizar] ║
╠═══════════════════════════════════════════════════════════╣
║  📊 Resumen | 🔍 Detalles | ⚙️ Técnico | ✅ Plan          ║
║                                                           ║
║  ┌─────────────────────────────────────────────────────┐  ║
║  │                                                     │  ║
║  │  📊 PUNTUACIÓN DE SEGURIDAD: 75/100                │  ║
║  │  📈 NIVEL DE RIESGO: 🟢 BUENO                      │  ║
║  │                                                     │  ║
║  │  📋 RESUMEN DE HALLAZGOS:                          │  ║
║  │     🔴 Problemas Críticos: 0                       │  ║
║  │     🟠 Problemas Altos: 2                          │  ║
║  │     🟡 Problemas Medios: 3                         │  ║
║  │                                                     │  ║
║  └─────────────────────────────────────────────────────┘  ║
╚═══════════════════════════════════════════════════════════╝
```

## ⚠️ Aviso legal

Este software está diseñado para:
- Analizar la seguridad de **tus propios sitios WordPress**
- Ayudar a administradores web a mejorar la seguridad
- Realizar análisis **no intrusivos** basados en información pública

**NO** utilices esta herramienta para:
- Analizar sitios sin autorización
- Realizar actividades ilegales
- Intentar explotar vulnerabilidades encontradas

El uso indebido de esta herramienta es responsabilidad exclusiva del usuario.

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Añade nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Si encuentras algún problema o tienes sugerencias:
- Abre un issue en el [repositorio de GitHub](https://github.com/sapoclay/fijaten-wp)
- Describe el problema detalladamente
- Incluye la versión de Python que usas

## 🔗 Enlaces

- **GitHub**: https://github.com/sapoclay/fijaten-wp
- **Autor**: Entreunosyceros

---

*Desarrollado con ❤️ para la comunidad WordPress*