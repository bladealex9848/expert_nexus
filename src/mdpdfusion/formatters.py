"""
Módulo para el procesamiento y formateo de texto Markdown.
"""

import re

def process_inline_formatting(text):
    """
    Procesa el formato en línea de Markdown para ReportLab.
    
    Args:
        text (str): Texto Markdown a procesar
        
    Returns:
        str: Texto con etiquetas de formato para ReportLab
    """
    import re
    
    if text is None:
        return ""
    
    # Escapar caracteres especiales de XML primero
    text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    
    # Ahora procesamos el formato Markdown de manera más robusta
    
    # Casos especiales de negrita+cursiva
    # ***texto*** o ___texto___
    text = re.sub(r'\*\*\*(.*?)\*\*\*', r'<b><i>\1</i></b>', text)
    text = re.sub(r'___(.*?)___', r'<b><i>\1</i></b>', text)
    
    # Negritas (** o __)
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.*?)__', r'<b>\1</b>', text)
    
    # Cursivas (* o _) - usando expresiones regulares más precisas
    # Usamos lookahead y lookbehind para evitar confusión con asteriscos en medio de palabras
    text = re.sub(r'(?<!\*)\*((?!\*).+?)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'(?<!_)_((?!_).+?)_(?!_)', r'<i>\1</i>', text)
    
    # Código en línea
    text = re.sub(r'`(.*?)`', r'<font face="Courier">\1</font>', text)
    
    # Enlaces [texto](url)
    # Manejar enlaces internos (con # al inicio) de manera especial
    def process_link(match):
        text, url = match.groups()
        # Si es un enlace interno (comienza con #)
        if url.startswith('#'):
            # Eliminar el # inicial
            anchor_text = url[1:]
            # Convertir a minúsculas
            anchor = anchor_text.lower()
            # Reemplazar espacios y caracteres especiales con guiones
            anchor = re.sub(r'\s+', '-', anchor)  # Espacios a guiones
            anchor = re.sub(r'[^a-z0-9_-]', '-', anchor)  # Otros caracteres a guiones
            # Eliminar guiones múltiples
            anchor = re.sub(r'-+', '-', anchor)
            # Eliminar guiones al inicio y final
            anchor = anchor.strip('-')
            # Para ReportLab, usamos <a name=""> para anclas y <link> para enlaces
            return f'<link href="#{anchor}">{text}</link>'
        else:
            return f'<link href="{url}">{text}</link>'
    
    text = re.sub(r'\[(.*?)\]\((.*?)\)', process_link, text)
    
    # Tachado: ~~texto~~
    text = re.sub(r'~~(.*?)~~', r'<strike>\1</strike>', text)
    
    # Eliminar escapes de caracteres Markdown
    text = re.sub(r'\\([\\`*_{}[\]()#+\-.!])', r'\1', text)
    
    return text

def create_anchor_id(text):
    """
    Crea un ID de ancla a partir de un texto.
    
    Args:
        text (str): Texto para convertir en ID de ancla
        
    Returns:
        str: ID de ancla normalizado
    """
    # Primero eliminar marcas de formato
    clean_text = re.sub(r'\*\*|\*|__|_|`', '', text)
    # Convertir a minúsculas
    anchor_id = clean_text.lower()
    # Reemplazar espacios y caracteres especiales con guiones
    anchor_id = re.sub(r'\s+', '-', anchor_id)  # Espacios a guiones
    anchor_id = re.sub(r'[^a-z0-9_-]', '-', anchor_id)  # Otros caracteres a guiones
    # Eliminar guiones múltiples
    anchor_id = re.sub(r'-+', '-', anchor_id)
    # Eliminar guiones al inicio y final
    anchor_id = anchor_id.strip('-')
    
    return anchor_id
