import threading
import time
from datetime import datetime, timedelta

def iniciar_tarea_limpieza_mensual():
    """Inicia un hilo para ejecutar la limpieza mensual de gastos"""
    thread = threading.Thread(target=programar_limpieza_mensual)
    thread.daemon = True  # El hilo se cerrará cuando termine la aplicación
    thread.start()

def programar_limpieza_mensual():
    """
    Programa la ejecución de la limpieza mensual para el primer día de cada mes.
    """
    while True:
        # Calcular tiempo hasta el primer día del próximo mes
        ahora = datetime.now()
        if ahora.month == 12:
            proximo_mes = datetime(ahora.year + 1, 1, 1, 0, 5, 0)  # 00:05 AM del primer día
        else:
            proximo_mes = datetime(ahora.year, ahora.month + 1, 1, 0, 5, 0)
        
        # Calcular segundos hasta el próximo mes
        segundos_espera = (proximo_mes - ahora).total_seconds()
        
        # Si estamos en el primer día del mes y antes de las 00:10 AM, ejecutar ahora
        if ahora.day == 1 and ahora.hour == 0 and ahora.minute < 10:
            ejecutar_limpieza_mensual()
        
        # Esperar hasta el próximo mes (máximo 1 día para evitar bloqueos largos)
        tiempo_espera = min(segundos_espera, 86400)  # 86400 segundos = 1 día
        time.sleep(tiempo_espera)
        
        # Si ya es el primer día del mes, ejecutar la limpieza
        if datetime.now().day == 1 and datetime.now().hour == 0:
            ejecutar_limpieza_mensual()

def ejecutar_limpieza_mensual():
    """
    Ejecuta la limpieza mensual de gastos y guarda las estadísticas.
    """
    try:
        # Importar aquí para evitar importaciones circulares
        from .models import EstadisticaMensual
        
        # Obtener el mes anterior
        ahora = datetime.now()
        if ahora.month == 1:
            mes_anterior = 12
            año_anterior = ahora.year - 1
        else:
            mes_anterior = ahora.month - 1
            año_anterior = ahora.year
            
        # Guardar estadísticas y limpiar gastos del mes anterior
        EstadisticaMensual.guardar_estadisticas_y_limpiar(año_anterior, mes_anterior)
        
        print(f"[{datetime.now()}] Limpieza mensual ejecutada correctamente para {mes_anterior}/{año_anterior}")
    except Exception as e:
        print(f"[{datetime.now()}] Error en la limpieza mensual: {str(e)}")