# Fijaten-WP

Este es un pequeño programa para analizar las vulnerabilidades de WordPress más conocidas y posiblemente más básicas.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20Windows%20%7C%20macOS-lightgrey.svg)

Fijaten-WP permite analizar las vulnerabilidades más comunes y críticas de cualquier sitio WordPress. Genera informes claros y comprensibles tanto para usuarios técnicos como no técnicos y así poder buscar una solución.

## Características

- **Interfaz gráfica** con tema oscuro/claro y fácil de usar. Los temas se encuentan en Preferencias > Apariencia
- **Análisis no intrusivo** - Solo analiza información pública. De lo que se trata es de impedir que otros se aprovechen
- **Informes para todos** - Explicaciones simples y técnicas (para toda la familia)
- **Plan de acción prioritizado** - Te da una pequeña indicación sobre qué arreglar primero
- **Escaneo múltiple** - Analiza varios sitios WordPress a la vez (para comparar)
- **Barra de progreso detallada** - PAra que todo esté claro en todo momento, muestra qué verificación se está ejecutando
- **Notificaciones de escritorio** - Alertas cuando termine el escaneo
- **Menú de opciones** - Configura qué verificaciones ejecutar en cada momento
- **Exportación de informes** - Guarda los resultados en TXT, PDF o HTML
- **Historial de escaneos** - Guarda y compara con los escaneos anteriores
- **Gráficos visuales** - Puntuación y distribución de severidades
- **Detección de tecnologías** - Identifica CMS, frameworks y lenguajes si no es WordPress
- **Enlaces CVE oficiales** - Links a NVD y MITRE para cada vulnerabilidad

## 🔍 Vulnerabilidades que analiza 🔍

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

## 🔍 Detección de tecnologías

Si el sitio analizado **no es WordPress**, Fijaten-WP intenta detectar automáticamente las tecnologías utilizadas:

### CMS y Plataformas
- Joomla, Drupal, Magento, PrestaShop
- Shopify, Wix, Squarespace, Webflow
- Ghost, TYPO3, Concrete5

### Frameworks
- **Backend**: Django, Laravel, Ruby on Rails, ASP.NET, Next.js, Nuxt.js
- **Frontend**: React, Vue.js, Angular, jQuery, Bootstrap, Tailwind CSS

### Lenguajes y Servidores
- PHP, Python, Ruby, Java, .NET
- Apache, Nginx, IIS, LiteSpeed

El detector muestra el **nivel de confianza** de cada tecnología identificada.

## Instalación

### Requisitos previos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

## ▶️ Uso

### Ejecutar la aplicación 

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

2. **Haz clic en "Analizar"** o presiona Intro

3. **Espera** mientras se realiza el análisis (10-30 segundos)

4. **Revisa los resultados** en las diferentes pestañas:
   - **📊 Resumen**: Vista general con puntuación de seguridad
   - **🔍 Detalles**: Explicación simple de cada problema
   - **⚙️ Técnico**: Información técnica detallada
   - **✅ Plan de Acción**: Pasos ordenados por prioridad

5. **Guarda el informe** haciendo clic en "Guardar Informe" o exporta a PDF/HTML

## Exportar informes

### Formatos disponibles

| Formato | Descripción | Atajo |
|---------|-------------|-------|
| **TXT** | Texto plano, ideal para copiar/pegar | `Ctrl+S` |
| **PDF** | Documento profesional con gráficos y tablas | `Ctrl+P` |
| **HTML** | Informe visual interactivo con gráficos Chart.js | `Ctrl+H` |

### Exportar a PDF

Requiere la librería `reportlab`:
```bash
pip install reportlab
```

El PDF incluye:
- Gráfico de puntuación circular
- Tabla de resumen por severidad
- Detalle de cada vulnerabilidad con colores
- Información del sitio

### Exportar a HTML

No requiere dependencias adicionales. El HTML incluye:
- Diseño con Tailwind CSS
- Gráfico de distribución con Chart.js
- Botón de imprimir integrado
- Opción de abrir en navegador

## Historial de escaneos

Fijaten-WP guarda automáticamente cada escaneo realizado:

- **Ubicación**: `~/.fijaten-wp/historial/`
- **Filtrar por dominio**: Busca escaneos de un sitio específico
- **Comparar escaneos**: Selecciona 2 escaneos para ver diferencias
- **Estadísticas**: Tendencia de seguridad (mejorando/empeorando/estable)
- **Límite**: Se mantienen los últimos 100 escaneos

### Información de comparación

- ✅ Vulnerabilidades resueltas
- ⚠️ Nuevas vulnerabilidades
- ⏳ Vulnerabilidades pendientes
- 📈 Cambio en puntuación

## Estructura del proyecto

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
│   ├── dialogo_historial.py    # Historial de escaneos
│   ├── dialogo_atajos.py       # Diálogo de atajos de teclado
│   ├── gestor_temas.py         # Gestión de tema claro/oscuro
│   ├── notificaciones.py       # Notificaciones de escritorio
│   ├── barra_menu.py           # Barra de menú
│   ├── componentes.py          # Componentes reutilizables
│   ├── exportador_pdf.py       # Exportación a PDF
│   ├── exportador_html.py      # Exportación a HTML
│   ├── historial_escaneos.py   # Gestión de historial
│   └── grafico_puntuacion.py   # Widget gráfico circular
└── scanner/
    ├── __init__.py
    ├── analizador_vulnerabilidades.py  # Motor de análisis
    ├── generador_informes.py           # Generación de informes
    ├── modelos.py                      # Modelos de datos
    ├── verificador_cve.py              # Verificación de CVEs
    ├── verificador_blacklist.py        # Verificación de listas negras
    ├── analizador_dns.py               # Análisis DNS/WHOIS
    ├── detector_waf.py                 # Detección de WAF/CDN
    └── detector_tecnologias.py         # Detección de tecnologías web
```

## Niveles de severidad

| Icono | Nivel | Descripción |
|-------|-------|-------------|
| 🔴 | CRÍTICA | Requiere acción inmediata |
| 🟠 | ALTA | Importante, arreglar pronto |
| 🟡 | MEDIA | Mejora recomendada |
| 🟢 | BAJA | Mejora opcional |
| 🔵 | INFO | Información |

## Atajos de teclado

| Atajo | Acción |
|-------|--------|
| `Ctrl+S` | Guardar informe en texto |
| `Ctrl+P` | Exportar a PDF |
| `Ctrl+H` | Exportar a HTML |
| `Ctrl+L` | Abrir historial de escaneos |
| `Ctrl+M` | Abrir escaneo múltiple |
| `Ctrl+O` | Abrir opciones de escaneo |
| `Ctrl+T` | Alternar modo claro/oscuro |
| `Ctrl+K` | Mostrar atajos de teclado |
| `Ctrl+Q` | Salir de la aplicación |
| `F1` | Mostrar "Acerca de" |
| `Enter` | Iniciar escaneo (en campo de dominio) |
| `Escape` | Cerrar ventanas flotantes |

> **Nota:** En macOS usa `Cmd` en lugar de `Ctrl`

## Pantalla principal

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
║  │  📊 PUNTUACIÓN DE SEGURIDAD: 75/100                 │  ║
║  │  📈 NIVEL DE RIESGO: 🟢 BUENO                       │  ║
║  │                                                     │  ║
║  │  📋 RESUMEN DE HALLAZGOS:                           │  ║
║  │     🔴 Problemas Críticos: 0                        │  ║
║  │     🟠 Problemas Altos: 2                           │  ║
║  │     🟡 Problemas Medios: 3                          │  ║
║  │                                                     │  ║
║  └─────────────────────────────────────────────────────┘  ║
╚═══════════════════════════════════════════════════════════╝
```

## ⚠️ Aviso legal ⚠️

Este software está diseñado para:
- Analizar la seguridad de **tus propios sitios WordPress**
- Ayudar a mejorar la seguridad de forma rápida
- Realizar análisis **no intrusivos** basados en información pública

**NO** utilices esta herramienta para:
- Analizar sitios sin autorización
- Realizar actividades ilegales
- Intentar explotar vulnerabilidades encontradas

El uso indebido de esta herramienta es responsabilidad exclusiva del usuario.

## Contribuciones

1. Haz fork del repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -am 'Añade nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Crea un Pull Request

## Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## Soporte

Si encuentras algún problema o tienes sugerencias:
- Abre un issue en el [repositorio de GitHub](https://github.com/sapoclay/fijaten-wp)
- Describe el problema detalladamente
- Incluye la versión de Python que usas

**GitHub**: https://github.com/sapoclay/fijaten-wp
**Autor**: entreunosyceros

---
