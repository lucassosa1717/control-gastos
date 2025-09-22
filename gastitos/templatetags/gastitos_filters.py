from django import template
import re

register = template.Library()

@register.filter
def simplificar_nombre_gasto(descripcion):
    """
    Simplifica el nombre de un gasto eliminando números al inicio y espacios extra.
    Ejemplo: "123 - Supermercado" -> "Supermercado"
    """
    # Patrón para eliminar números y caracteres especiales al inicio
    patron = r'^[\d\s\-:\.]+\s*'
    descripcion_simplificada = re.sub(patron, '', descripcion)
    
    # Eliminar espacios extra
    descripcion_simplificada = descripcion_simplificada.strip()
    
    return descripcion_simplificada if descripcion_simplificada else descripcion