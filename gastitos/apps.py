from django.apps import AppConfig
from django.utils import timezone
import threading
import time
from datetime import datetime, timedelta


class GastitosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'gastitos'
    
    def ready(self):
        # Evitar ejecutar en comandos de manejo como migrate
        import sys
        if 'runserver' not in sys.argv:
            return
            
        # Iniciar el hilo para la tarea programada
        from .tasks import iniciar_tarea_limpieza_mensual
        iniciar_tarea_limpieza_mensual()
