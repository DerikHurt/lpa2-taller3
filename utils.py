"""
Módulo de utilidades para la aplicación.
Contiene funciones auxiliares utilizadas en diferentes partes de la aplicación.
"""

import re
from datetime import datetime

PATRON_CORREO = re.compile(r"^[\w.+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}$")


def validar_correo(correo):
    """
    Valida que un correo electrónico tenga un formato válido.

    Args:
        correo (str): Correo electrónico a validar

    Returns:
        bool: True si el correo es válido, False en caso contrario
    """
    if not isinstance(correo, str):
        return False
    return bool(PATRON_CORREO.fullmatch(correo))


def formatear_duracion(segundos):
    """
    Convierte una duración en segundos a formato mm:ss.

    Args:
        segundos (int): Duración en segundos

    Returns:
        str: Duración formateada como mm:ss
    """
    if segundos is None or segundos < 0:
        raise ValueError("La duración debe ser un número no negativo")
    minutos, segs = divmod(int(segundos), 60)
    return f"{minutos:02d}:{segs:02d}"


def generar_slug(texto):
    """
    Genera un slug a partir de un texto.
    Un slug es una versión de texto amigable para URLs.
    
    Args:
        texto (str): Texto a convertir en slug
        
    Returns:
        str: Slug generado
    """
    # TODO: Convertir a minúsculas
    slug = texto
    
    # TODO: Reemplazar espacios con guiones
    
    # TODO: Eliminar caracteres no alfanuméricos (excepto guiones)
    
    # TODO: Reemplazar múltiples guiones con uno solo
    
    # TODO: Eliminar guiones al inicio y final
    
    return slug


def obtener_año_actual():
    """
    Obtiene el año actual.
    
    Returns:
        int: Año actual
    """
    # TODO: pendiente por implementar
    return ""


def validar_año(año):
    """
    Valida que un año sea válido (no futuro y no muy antiguo).
    
    Args:
        año (int): Año a validar
        
    Returns:
        bool: True si el año es válido, False en caso contrario
    """
    año_actual = obtener_año_actual()
    return 1900 <= año <= año_actual
