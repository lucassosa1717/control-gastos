# Gastitos - Control de Gastos Personales

Gastitos es una aplicación web desarrollada con Django para el control y gestión de gastos personales.

## Características

- Registro de gastos diarios
- Configuración de salario mensual
- Gestión de gastos fijos recurrentes
- Cálculo de saldo disponible
- Visualización de gastos recientes
- Procesamiento de estados de cuenta de tarjetas de crédito

## Requisitos

- Python 3.11 o superior
- Django 5.2.5
- Otras dependencias en el entorno virtual

## Instalación

El proyecto ya incluye un entorno virtual con todas las dependencias necesarias.

## Uso

### Scripts de inicio rápido

Se han incluido dos scripts para facilitar el inicio del proyecto:

1. **start_server.bat** - Activa el entorno virtual e inicia el servidor de desarrollo Django
   ```
   start_server.bat
   ```

2. **activate_venv.bat** - Solo activa el entorno virtual, permitiendo ejecutar otros comandos de Django
   ```
   activate_venv.bat
   ```
   Después de ejecutar este script, puedes usar comandos como:
   ```
   python manage.py runserver
   python manage.py makemigrations
   python manage.py migrate
   python manage.py shell
   ```

### Acceso a la aplicación

Una vez iniciado el servidor, puedes acceder a la aplicación en:

- http://localhost:8000/ o http://127.0.0.1:8000/

## Estructura del proyecto

- **gastitos/** - Aplicación principal con modelos, vistas y lógica de negocio
- **gastos/** - Configuración del proyecto Django
- **templates/** - Plantillas HTML para la interfaz de usuario
- **static/** - Archivos estáticos (CSS, JavaScript, imágenes)
- **media/** - Archivos subidos por los usuarios
- **.venv/** - Entorno virtual con dependencias