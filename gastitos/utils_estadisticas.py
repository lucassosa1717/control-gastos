from django.db.models import Sum
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import datetime
import calendar
import json
import os

def guardar_estadisticas_mensuales():
    """
    Guarda las estadísticas de gastos del mes anterior en un archivo JSON
    y elimina los gastos de ese mes.
    """
    from .models import Gasto
    
    # Obtener el mes anterior
    fecha_actual = datetime.now()
    if fecha_actual.month == 1:
        mes = 12
        año = fecha_actual.year - 1
    else:
        mes = fecha_actual.month - 1
        año = fecha_actual.year
    
    # Obtener el primer y último día del mes
    ultimo_dia = calendar.monthrange(año, mes)[1]
    inicio_mes = datetime(año, mes, 1, 0, 0, 0)
    fin_mes = datetime(año, mes, ultimo_dia, 23, 59, 59)
    
    # Directorio para guardar estadísticas
    directorio = os.path.join('estadisticas')
    if not os.path.exists(directorio):
        os.makedirs(directorio)
    
    # Procesar cada usuario
    estadisticas = {}
    
    for usuario in User.objects.all():
        # Obtener todos los gastos del mes para este usuario
        gastos_mes = Gasto.objects.filter(
            usuario=usuario,
            fecha__gte=inicio_mes,
            fecha__lte=fin_mes
        )
        
        # Calcular el total de gastos
        total = gastos_mes.aggregate(total=Sum('monto'))['total'] or Decimal('0')
        
        # Guardar la estadística mensual
        estadisticas[usuario.username] = {
            'total_gastos': float(total),
            'año': año,
            'mes': mes,
            'nombre_mes': calendar.month_name[mes]
        }
        
        # Eliminar los gastos del mes
        gastos_mes.delete()
    
    # Guardar estadísticas en archivo JSON
    nombre_archivo = f"estadisticas_{año}_{mes}.json"
    ruta_archivo = os.path.join(directorio, nombre_archivo)
    
    with open(ruta_archivo, 'w') as f:
        json.dump(estadisticas, f, indent=4)
    
    return estadisticas

def obtener_estadisticas_mensuales(usuario, año=None, mes=None):
    """
    Obtiene las estadísticas mensuales para un usuario específico.
    Si no se especifica año y mes, devuelve todas las estadísticas disponibles.
    """
    directorio = os.path.join('estadisticas')
    if not os.path.exists(directorio):
        return []
    
    estadisticas = []
    
    # Listar todos los archivos de estadísticas
    for archivo in os.listdir(directorio):
        if archivo.startswith('estadisticas_') and archivo.endswith('.json'):
            try:
                with open(os.path.join(directorio, archivo), 'r') as f:
                    datos = json.load(f)
                
                # Extraer año y mes del nombre del archivo
                partes = archivo.replace('estadisticas_', '').replace('.json', '').split('_')
                año_archivo = int(partes[0])
                mes_archivo = int(partes[1])
                
                # Filtrar por año y mes si se especifican
                if (año is None or año_archivo == año) and (mes is None or mes_archivo == mes):
                    # Obtener estadísticas del usuario
                    if usuario.username in datos:
                        estadistica = datos[usuario.username]
                        estadistica['año'] = año_archivo
                        estadistica['mes'] = mes_archivo
                        estadisticas.append(estadistica)
            except:
                # Ignorar archivos con formato incorrecto
                pass
    
    # Ordenar por año y mes (más reciente primero)
    return sorted(estadisticas, key=lambda x: (x['año'], x['mes']), reverse=True)