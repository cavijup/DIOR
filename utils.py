def obtener_letra_a_indice(letra):
    """Convierte una letra de columna Excel a índice numérico."""
    if len(letra) == 1:
        return ord(letra) - ord('A')
    elif len(letra) == 2:
        return (ord(letra[0]) - ord('A') + 1) * 26 + (ord(letra[1]) - ord('A'))
    return -1

def interpretar_promedio(valor):
    """
    Interpreta el valor promedio según la escala.
    """
    if valor < 1.5:
        return "Muy Desfavorable"
    elif valor < 2.5:
        return "Desfavorable"
    elif valor < 3.5:
        return "Neutral"
    elif valor < 4.5:
        return "Favorable"
    else:
        return "Muy Favorable"