from django.contrib.auth.models import User
from django.db.models import Sum, Avg
from .models import MetaAhorro, Gasto, PerfilUsuario
from datetime import datetime, date, timedelta
from decimal import Decimal


def calcular_capacidad_ahorro_usuario(usuario):
    """Calcula la capacidad de ahorro mensual del usuario basada en su historial"""
    try:
        perfil = PerfilUsuario.objects.get(user=usuario)
        
        # Obtener gastos de los últimos 3 meses para calcular promedio
        hace_3_meses = datetime.now() - timedelta(days=90)
        gastos_recientes = Gasto.objects.filter(
            usuario=usuario,
            fecha__gte=hace_3_meses
        )
        
        if gastos_recientes.exists():
            # Calcular promedio mensual de gastos
            total_gastos = gastos_recientes.aggregate(Sum('monto'))['monto__sum'] or 0
            promedio_mensual_gastos = total_gastos / Decimal('3')
        else:
            # Si no hay historial, usar 70% del salario como estimación conservadora
            promedio_mensual_gastos = perfil.salario_mensual * Decimal('0.7')
        
        # Capacidad de ahorro = Salario - Gastos promedio
        capacidad_ahorro = perfil.salario_mensual - promedio_mensual_gastos
        
        # Asegurar que no sea negativa
        return max(capacidad_ahorro, Decimal('0'))
        
    except PerfilUsuario.DoesNotExist:
        return Decimal('0')


def calcular_recomendacion_ahorro_inteligente(meta_ahorro, usuario):
    """Calcula una recomendación de ahorro inteligente basada en la capacidad del usuario"""
    capacidad_ahorro = calcular_capacidad_ahorro_usuario(usuario)
    recomendacion_basica = meta_ahorro.ahorro_mensual_recomendado
    
    # Si la recomendación básica excede la capacidad, ajustar
    if recomendacion_basica > capacidad_ahorro:
        # Sugerir el 80% de la capacidad para ser realista
        recomendacion_ajustada = capacidad_ahorro * Decimal('0.8')
        
        # Calcular cuánto tiempo adicional necesitaría
        if recomendacion_ajustada > 0:
            meses_necesarios = meta_ahorro.monto_restante / recomendacion_ajustada
            nueva_fecha_objetivo = date.today() + timedelta(days=int(meses_necesarios * Decimal('30.44')))
        else:
            nueva_fecha_objetivo = None
            
        return {
            'recomendacion_mensual': recomendacion_ajustada,
            'es_ajustada': True,
            'capacidad_ahorro': capacidad_ahorro,
            'nueva_fecha_sugerida': nueva_fecha_objetivo,
            'mensaje': 'Recomendación ajustada según tu capacidad de ahorro'
        }
    else:
        return {
            'recomendacion_mensual': recomendacion_basica,
            'es_ajustada': False,
            'capacidad_ahorro': capacidad_ahorro,
            'nueva_fecha_sugerida': None,
            'mensaje': 'Meta alcanzable con tu capacidad actual'
        }


def obtener_estadisticas_ahorro_usuario(usuario):
    """Obtiene estadísticas completas de ahorro del usuario"""
    metas = MetaAhorro.objects.filter(usuario=usuario)
    
    estadisticas = {
        'total_metas': metas.count(),
        'metas_activas': metas.filter(estado='activa').count(),
        'metas_completadas': metas.filter(estado='completada').count(),
        'monto_total_objetivos': metas.aggregate(Sum('monto_objetivo'))['monto_objetivo__sum'] or 0,
        'monto_total_ahorrado': metas.aggregate(Sum('monto_ahorrado'))['monto_ahorrado__sum'] or 0,
        'capacidad_ahorro_mensual': calcular_capacidad_ahorro_usuario(usuario),
        'metas_con_recomendaciones': []
    }
    
    # Agregar recomendaciones para cada meta activa
    for meta in metas.filter(estado='activa'):
        recomendacion = calcular_recomendacion_ahorro_inteligente(meta, usuario)
        estadisticas['metas_con_recomendaciones'].append({
            'meta': meta,
            'recomendacion': recomendacion
        })
    
    return estadisticas


def verificar_metas_vencidas(usuario):
    """Verifica y actualiza el estado de metas vencidas"""
    metas_activas = MetaAhorro.objects.filter(usuario=usuario, estado='activa')
    metas_actualizadas = []
    
    for meta in metas_activas:
        if meta.esta_vencida:
            meta.estado = 'cancelada'
            meta.save()
            metas_actualizadas.append(meta)
    
    return metas_actualizadas


def calcular_progreso_general_ahorro(usuario):
    """Calcula el progreso general de ahorro del usuario"""
    metas_activas = MetaAhorro.objects.filter(usuario=usuario, estado='activa')
    
    if not metas_activas.exists():
        return {
            'progreso_promedio': 0,
            'total_ahorrado': 0,
            'total_objetivo': 0,
            'metas_en_riesgo': 0
        }
    
    total_ahorrado = 0
    total_objetivo = 0
    metas_en_riesgo = 0
    
    for meta in metas_activas:
        total_ahorrado += meta.monto_ahorrado
        total_objetivo += meta.monto_objetivo
        
        # Meta en riesgo si el progreso de tiempo supera el progreso de dinero por más del 20%
        progreso_tiempo = meta.calcular_progreso_tiempo()
        progreso_dinero = meta.porcentaje_completado
        
        if progreso_tiempo > progreso_dinero + 20:
            metas_en_riesgo += 1
    
    progreso_promedio = (total_ahorrado / total_objetivo * 100) if total_objetivo > 0 else 0
    
    return {
        'progreso_promedio': progreso_promedio,
        'total_ahorrado': total_ahorrado,
        'total_objetivo': total_objetivo,
        'metas_en_riesgo': metas_en_riesgo
    }


def generar_consejos_ahorro(usuario):
    """Genera consejos personalizados de ahorro basados en el perfil del usuario"""
    estadisticas = obtener_estadisticas_ahorro_usuario(usuario)
    consejos = []
    
    # Consejo basado en capacidad de ahorro
    if estadisticas['capacidad_ahorro_mensual'] <= 0:
        consejos.append({
            'tipo': 'warning',
            'titulo': 'Revisa tus gastos',
            'mensaje': 'Tus gastos actuales igualan o superan tus ingresos. Considera reducir gastos innecesarios.'
        })
    elif estadisticas['capacidad_ahorro_mensual'] < 50000:
        consejos.append({
            'tipo': 'info',
            'titulo': 'Aumenta tu capacidad de ahorro',
            'mensaje': f'Tu capacidad actual es de ${estadisticas["capacidad_ahorro_mensual"]:,.0f}/mes. Busca formas de reducir gastos.'
        })
    
    # Consejo basado en metas
    if estadisticas['total_metas'] == 0:
        consejos.append({
            'tipo': 'success',
            'titulo': 'Crea tu primera meta',
            'mensaje': 'Establecer metas de ahorro te ayudará a mantener la motivación y el enfoque.'
        })
    elif estadisticas['metas_activas'] == 0:
        consejos.append({
            'tipo': 'info',
            'titulo': 'Reactiva tus metas',
            'mensaje': 'No tienes metas activas. Considera crear nuevas metas o reactivar las existentes.'
        })
    
    # Consejo basado en progreso
    progreso = calcular_progreso_general_ahorro(usuario)
    if progreso['metas_en_riesgo'] > 0:
        consejos.append({
            'tipo': 'warning',
            'titulo': 'Metas en riesgo',
            'mensaje': f'Tienes {progreso["metas_en_riesgo"]} meta(s) que podrían no cumplirse a tiempo. Revisa tus recomendaciones.'
        })
    
    return consejos