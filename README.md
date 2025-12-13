# 🔒 Fijaten-WP

Analizador de vulnerabilidades de WordPress con interfaz gráfica moderna.

## 📋 Descripción

Fijaten-WP permite analizar las vulnerabilidades más comunes y críticas de cualquier sitio WordPress. Genera informes claros y comprensibles tanto para usuarios técnicos como no técnicos.

## 🚀 Características

- **Interfaz gráfica moderna** y fácil de usar
- **Análisis no intrusivo** - Solo analiza información pública
- **Informes para todos** - Explicaciones simples y técnicas
- **Plan de acción prioritizado** - Sabe qué arreglar primero
- **Menú con opciones** - Archivo > Salir y About

## 🔍 Vulnerabilidades que analiza

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
| Cabeceras HTTP | Verifica cabeceras de seguridad |
| Y más... | Múltiples verificaciones adicionales |

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
python run_app.py
```

Este script automáticamente:
- Crea el entorno virtual si no existe
- Instala las dependencias necesarias
- Ejecuta la aplicación

### Ejecutar directamente (si ya tienes las dependencias)

```bash
python main.py
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

## 📊 Niveles de severidad

| Icono | Nivel | Descripción |
|-------|-------|-------------|
| 🔴 | CRÍTICA | Requiere acción inmediata |
| 🟠 | ALTA | Importante, arreglar pronto |
| 🟡 | MEDIA | Mejora recomendada |
| 🟢 | BAJA | Mejora opcional |
| 🔵 | INFO | Información |

## 📸 Capturas de pantalla

### Pantalla principal
```
╔═══════════════════════════════════════════════════════════╗
║  🔒 Fijaten-WP                                            ║
╠═══════════════════════════════════════════════════════════╣
║  Archivo | Ayuda                                          ║
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

---

