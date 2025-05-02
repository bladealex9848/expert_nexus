"""
Módulo que contiene los diferentes conversores de Markdown a PDF.
"""

import os
import re
import logging
import traceback
import urllib.request
from io import BytesIO

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle, Preformatted

from .formatters import process_inline_formatting, create_anchor_id

# Configurar logging
logger = logging.getLogger("mdpdfusion")

def convert_with_pypandoc(md_content, output_pdf):
    """
    Convierte contenido Markdown a PDF usando pypandoc.

    Args:
        md_content (str): Contenido Markdown a convertir
        output_pdf (str): Ruta donde guardar el PDF generado

    Returns:
        bool: True si la conversión fue exitosa, False en caso contrario
    """
    try:
        import pypandoc
        pypandoc.convert_text(md_content, 'pdf', format='md', outputfile=output_pdf)
        return os.path.exists(output_pdf)
    except Exception as e:
        logger.error(f"Error al convertir con pypandoc: {str(e)}")
        return False

def convert_with_reportlab(md_content, output_pdf):
    """
    Convierte contenido Markdown a PDF usando ReportLab.

    Args:
        md_content (str): Contenido Markdown a convertir
        output_pdf (str): Ruta donde guardar el PDF generado

    Returns:
        bool: True si la conversión fue exitosa, False en caso contrario
    """
    try:
        # Crear el documento PDF
        doc = SimpleDocTemplate(
            output_pdf,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )

        # Estilos
        styles = getSampleStyleSheet()

        # Estilo para encabezado nivel 3
        heading3_style = ParagraphStyle(
            'Heading3',
            parent=styles['Heading2'],
            fontSize=14,
            leading=16
        )

        # Estilo para encabezado nivel 4
        heading4_style = ParagraphStyle(
            'Heading4',
            parent=styles['Heading3'],
            fontSize=12,
            leading=14
        )

        # Estilo para código
        code_style = ParagraphStyle(
            'Code',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=9,
            leading=11,
            leftIndent=36,
            rightIndent=36,
            backColor=colors.lightgrey.clone(alpha=0.3),
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=5,
            borderRadius=5,
            spaceAfter=10,
            spaceBefore=10
        )

        # Estilos para listas
        bullet_style_level1 = ParagraphStyle(
            'BulletLevel1',
            parent=styles['Normal'],
            leftIndent=20,
            firstLineIndent=0,
            spaceBefore=3,
            spaceAfter=3
        )

        bullet_style_level2 = ParagraphStyle(
            'BulletLevel2',
            parent=bullet_style_level1,
            leftIndent=40
        )

        bullet_style_level3 = ParagraphStyle(
            'BulletLevel3',
            parent=bullet_style_level1,
            leftIndent=60
        )

        quote_style = ParagraphStyle(
            'CustomBlockQuote',
            parent=styles['Normal'],
            leftIndent=30,
            rightIndent=30,
            fontStyle='italic',
            borderWidth=0,
            borderColor=colors.grey,
            borderPadding=5,
            borderRadius=5,
            backColor=colors.lightgrey.clone(alpha=0.3)
        )

        # Enfoque simple línea por línea con mejor manejo de formato
        flowables = []
        in_code_block = False
        code_content = []
        code_language = ""
        in_table = False
        table_header = []
        table_rows = []
        table_separator_line = -1

        # Procesamos el contenido línea por línea
        lines = md_content.split('\n')
        i = 0

        # Función para determinar el nivel de indentación de una lista
        def get_list_level(line):
            if line.startswith('  '):
                spaces = len(line) - len(line.lstrip())
                return spaces // 2
            return 0

        # Función para procesar listas anidadas
        def process_list_item(line, is_ordered=False):
            level = get_list_level(line)
            line = line.lstrip()

            # Eliminar el marcador de lista
            if is_ordered:
                parts = line.split('. ', 1)
                if len(parts) == 2 and parts[0].isdigit():
                    num, text = parts
                    text = process_inline_formatting(text)

                    if level == 0:
                        return Paragraph(f"{num}. {text}", bullet_style_level1)
                    elif level == 1:
                        return Paragraph(f"{num}. {text}", bullet_style_level2)
                    else:
                        return Paragraph(f"{num}. {text}", bullet_style_level3)
            else:
                if line.startswith('- ') or line.startswith('* '):
                    text = line[2:]
                    text = process_inline_formatting(text)

                    if level == 0:
                        return Paragraph(f"• {text}", bullet_style_level1)
                    elif level == 1:
                        return Paragraph(f"◦ {text}", bullet_style_level2)
                    else:
                        return Paragraph(f"▪ {text}", bullet_style_level3)

            # Si no es una lista válida, devolver como texto normal
            return Paragraph(process_inline_formatting(line), styles['Normal'])

        while i < len(lines):
            line = lines[i]

            # Detectar bloques de código
            if line.startswith('```'):
                if in_code_block:
                    # Fin del bloque de código
                    code_text = '<br/>'.join(code_content)

                    # Verificar si es un diagrama Mermaid
                    if code_language and code_language.lower() == "mermaid":
                        try:
                            # Para diagramas Mermaid, intentamos generar una imagen
                            import io
                            import base64
                            import requests
                            from PIL import Image

                            # Contenido del diagrama Mermaid (sin la primera línea que contiene "mermaid")
                            # Eliminar la primera línea si contiene "Lenguaje: mermaid"
                            if len(code_content) > 0 and "Lenguaje: mermaid" in code_content[0]:
                                mermaid_code = "\n".join(code_content[2:] if len(code_content) > 2 else [])
                            else:
                                mermaid_code = "\n".join(code_content)

                            logger.info(f"Procesando diagrama Mermaid: {mermaid_code}")

                            # Intentar generar el diagrama usando la API de Mermaid.ink
                            mermaid_encoded = base64.urlsafe_b64encode(mermaid_code.encode()).decode()
                            mermaid_url = f"https://mermaid.ink/img/{mermaid_encoded}?bgColor=white"

                            logger.info(f"URL de Mermaid: {mermaid_url}")

                            try:
                                # Intentar descargar la imagen
                                response = requests.get(mermaid_url, timeout=15)
                                if response.status_code == 200:
                                    logger.info("Imagen Mermaid descargada correctamente")

                                    # Guardar la imagen temporalmente para depuración
                                    with open("temp_mermaid.png", "wb") as f:
                                        f.write(response.content)

                                    # Crear una imagen a partir de los bytes descargados
                                    img = Image(io.BytesIO(response.content))

                                    # Ajustar tamaño si es necesario
                                    max_width = 6 * inch  # 6 pulgadas de ancho máximo
                                    if img.drawWidth > max_width:
                                        ratio = max_width / img.drawWidth
                                        img.drawWidth = max_width
                                        img.drawHeight *= ratio

                                    # Centrar la imagen
                                    img.hAlign = 'CENTER'
                                    flowables.append(img)

                                    # Añadir leyenda
                                    caption_style = ParagraphStyle(
                                        'Caption',
                                        parent=styles['Normal'],
                                        alignment=1,  # Centrado
                                        fontSize=9,
                                        leading=11
                                    )
                                    flowables.append(Paragraph(f"<i>Diagrama Mermaid</i>", caption_style))

                                    # Continuar con el siguiente bloque
                                    code_content = []
                                    in_code_block = False
                                    i += 1
                                    continue
                                else:
                                    logger.warning(f"Error al descargar imagen Mermaid: {response.status_code} - {response.text}")
                            except Exception as e:
                                logger.warning(f"No se pudo generar el diagrama Mermaid: {str(e)}")
                                # Si falla, mostrar como código normal
                        except ImportError as ie:
                            logger.warning(f"No se pudo importar las bibliotecas necesarias para generar diagramas Mermaid: {str(ie)}")
                            # Si falla, mostrar como código normal

                    # Verificar si es un diagrama ASCII (contiene caracteres como │, ┌, ┐, └, ┘, ─, etc.)
                    ascii_diagram_chars = ['│', '┌', '┐', '└', '┘', '─', '┬', '┴', '┼', '├', '┤', '━', '┃', '┏', '┓', '┗', '┛']
                    is_ascii_diagram = any(char in '\n'.join(code_content) for char in ascii_diagram_chars)

                    if is_ascii_diagram:
                        # Para diagramas ASCII, usar Preformatted que preserva espacios y formato exacto
                        logger.info("Procesando diagrama ASCII")

                        # Unir el contenido original sin procesar para preservar el formato exacto
                        raw_content = '\n'.join(code_content)

                        # Eliminar la primera línea si contiene información de lenguaje
                        if len(code_content) > 0 and code_content[0].startswith("<b>Lenguaje:"):
                            if len(code_content) > 1 and code_content[1] == "":
                                raw_content = '\n'.join(code_content[2:])
                            else:
                                raw_content = '\n'.join(code_content[1:])

                        # Crear un estilo para el diagrama ASCII
                        ascii_style = ParagraphStyle(
                            'AsciiArt',
                            parent=styles['Normal'],
                            fontName='Courier',
                            fontSize=8,
                            leading=9,
                            leftIndent=36,
                            rightIndent=36,
                            spaceAfter=10,
                            spaceBefore=10,
                        )

                        # Usar Preformatted para preservar espacios y formato exacto
                        # Añadir un recuadro alrededor del diagrama
                        flowables.append(Spacer(1, 5))

                        # Título del diagrama
                        flowables.append(Paragraph("<b>Diagrama ASCII</b>", ParagraphStyle(
                            'AsciiTitle',
                            parent=styles['Normal'],
                            alignment=1,  # Centrado
                            fontSize=9,
                            leading=11,
                            spaceBefore=5,
                            spaceAfter=5
                        )))

                        # Crear un recuadro con fondo gris claro
                        ascii_box = Table(
                            [[Preformatted(raw_content, ascii_style)]],
                            colWidths=[6.5 * inch]
                        )
                        ascii_box.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey.clone(alpha=0.3)),
                            ('BOX', (0, 0), (-1, -1), 1, colors.grey),
                            ('TOPPADDING', (0, 0), (-1, -1), 10),
                            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                            ('LEFTPADDING', (0, 0), (-1, -1), 10),
                            ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                        ]))

                        flowables.append(ascii_box)
                        flowables.append(Spacer(1, 5))
                    else:
                        # Para código normal o si falló la generación del diagrama Mermaid
                        code_block = Paragraph(code_text, code_style)
                        flowables.append(code_block)

                    code_content = []
                    in_code_block = False
                else:
                    # Inicio del bloque de código
                    in_code_block = True
                    # Capturar el lenguaje si está especificado
                    code_language = ""
                    if len(line) > 3:
                        code_language = line[3:].strip()
                        if code_language:
                            # Añadir el lenguaje como una etiqueta antes del bloque de código
                            # pero no lo incluimos en el flowable todavía, lo guardaremos para después
                            code_content.append(f"<b>Lenguaje: {code_language}</b>")
                            # Añadir una línea en blanco después del lenguaje
                            code_content.append("")
                i += 1
                continue

            if in_code_block:
                # Estamos dentro de un bloque de código
                code_content.append(line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;'))
                i += 1
                continue

            # Detectar imágenes
            image_match = re.match(r'!\[(.*?)\]\((.*?)\)', line)
            if image_match:
                alt_text = image_match.group(1)
                image_url = image_match.group(2)

                try:
                    # Intentar cargar la imagen
                    if image_url.startswith('http'):
                        # Imagen desde URL
                        response = urllib.request.urlopen(image_url)
                        img_data = response.read()
                        img = Image(BytesIO(img_data))
                    else:
                        # Imagen local
                        img = Image(image_url)

                    # Ajustar tamaño si es necesario
                    max_width = 6 * inch  # 6 pulgadas de ancho máximo
                    if img.drawWidth > max_width:
                        ratio = max_width / img.drawWidth
                        img.drawWidth = max_width
                        img.drawHeight *= ratio

                    # Centrar la imagen
                    img.hAlign = 'CENTER'
                    flowables.append(img)

                    # Añadir leyenda si hay texto alternativo
                    if alt_text:
                        caption_style = ParagraphStyle(
                            'Caption',
                            parent=styles['Normal'],
                            alignment=1,  # Centrado
                            fontSize=9,
                            leading=11
                        )
                        flowables.append(Paragraph(f"<i>{alt_text}</i>", caption_style))
                except Exception as img_error:
                    logger.error(f"Error al procesar imagen: {str(img_error)}")
                    # Si falla, mostrar como texto
                    flowables.append(Paragraph(f"[Imagen: {alt_text}]", styles['Normal']))

                i += 1
                continue

            # Detectar tablas - Implementación mejorada
            if line.strip().startswith('|') and line.strip().endswith('|'):
                logger.info(f"Línea de tabla detectada: {line}")

                # Si no estamos en una tabla, iniciar una nueva
                if not in_table:
                    in_table = True
                    # Guardar la línea de encabezado
                    table_header = [cell.strip() for cell in line.strip('|').split('|')]
                    table_rows = []
                    logger.info(f"Encabezado de tabla: {table_header}")

                # Si la línea actual es un separador de tabla (contiene guiones)
                elif '-' in line and line.strip().startswith('|') and line.strip().endswith('|'):
                    table_separator_line = i
                    logger.info(f"Separador de tabla detectado en línea {i}: {line}")

                # Si es una fila de datos (y ya hemos visto un encabezado)
                elif in_table and table_separator_line == -1:
                    # Todavía no hemos visto un separador, podría ser un separador
                    if all(c == '-' or c == '|' or c == ':' or c == ' ' for c in line):
                        table_separator_line = i
                        logger.info(f"Separador de tabla alternativo detectado en línea {i}: {line}")
                    else:
                        logger.warning(f"Línea de tabla ignorada (esperando separador): {line}")

                # Si es una fila de datos (después del separador)
                elif in_table and table_separator_line > 0 and i > table_separator_line:
                    row_data = [cell.strip() for cell in line.strip('|').split('|')]
                    table_rows.append(row_data)
                    logger.info(f"Fila de datos añadida: {row_data}")

                i += 1

                # Si la siguiente línea no es parte de la tabla o es el final del archivo, procesar la tabla
                if i >= len(lines) or not lines[i].strip().startswith('|'):
                    logger.info(f"Fin de tabla detectado. Encabezados: {len(table_header)}, Filas: {len(table_rows)}, Separador: {table_separator_line}")

                    # Verificar que tenemos todos los componentes necesarios para una tabla válida
                    if len(table_header) > 0 and len(table_rows) > 0:
                        try:
                            # Crear la tabla con datos procesados para formato
                            header_style = ParagraphStyle(
                                'TableHeader',
                                parent=styles['Normal'],
                                fontName='Helvetica-Bold',
                                alignment=1  # Centrado
                            )

                            cell_style = ParagraphStyle(
                                'TableCell',
                                parent=styles['Normal']
                            )

                            # Procesar encabezados
                            processed_header = [Paragraph(process_inline_formatting(cell), header_style) for cell in table_header]

                            # Procesar filas
                            processed_rows = []
                            for row in table_rows:
                                # Asegurarse de que la fila tiene la misma longitud que el encabezado
                                while len(row) < len(table_header):
                                    row.append("")  # Rellenar con celdas vacías si es necesario

                                if len(row) > len(table_header):
                                    row = row[:len(table_header)]  # Truncar si hay demasiadas celdas

                                processed_row = [Paragraph(process_inline_formatting(cell), cell_style) for cell in row]
                                processed_rows.append(processed_row)

                            # Datos de la tabla
                            table_data = [processed_header] + processed_rows

                            # Calcular anchos de columna
                            available_width = 6 * inch  # Ancho disponible
                            col_width = available_width / len(table_header)
                            col_widths = [col_width] * len(table_header)

                            # Crear la tabla
                            table = Table(table_data, colWidths=col_widths)

                            # Estilo de la tabla
                            table_style = TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
                                ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                                ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
                                ('PADDING', (0, 0), (-1, -1), 6),
                            ])
                            table.setStyle(table_style)

                            # Añadir la tabla al documento
                            flowables.append(Spacer(1, 10))  # Espacio antes de la tabla
                            flowables.append(table)
                            flowables.append(Spacer(1, 10))  # Espacio después de la tabla

                            logger.info(f"Tabla procesada exitosamente con {len(table_header)} columnas y {len(table_rows)} filas")
                        except Exception as table_error:
                            logger.error(f"Error al procesar tabla: {str(table_error)}")
                            traceback.print_exc()
                    else:
                        logger.warning(f"Tabla incompleta: Encabezados={len(table_header)}, Filas={len(table_rows)}")

                    # Reiniciar variables de tabla
                    in_table = False
                    table_header = []
                    table_rows = []
                    table_separator_line = -1

                continue

            # Procesar encabezados con formato en línea y generar anclas
            if line.startswith('# '):
                # Crear un ID de ancla a partir del texto del encabezado
                heading_text = line[2:]
                anchor_id = create_anchor_id(heading_text)

                # Aplicar formato en línea al texto del encabezado y añadir ancla
                formatted_text = f'<a name="{anchor_id}"/>' + process_inline_formatting(heading_text)
                flowables.append(Paragraph(formatted_text, styles['Title']))

            elif line.startswith('## '):
                heading_text = line[3:]
                anchor_id = create_anchor_id(heading_text)

                formatted_text = f'<a name="{anchor_id}"/>' + process_inline_formatting(heading_text)
                flowables.append(Paragraph(formatted_text, styles['Heading2']))

            elif line.startswith('### '):
                heading_text = line[4:]
                anchor_id = create_anchor_id(heading_text)

                formatted_text = f'<a name="{anchor_id}"/>' + process_inline_formatting(heading_text)
                flowables.append(Paragraph(formatted_text, heading3_style))

            elif line.startswith('#### '):
                heading_text = line[5:]
                anchor_id = create_anchor_id(heading_text)

                formatted_text = f'<a name="{anchor_id}"/>' + process_inline_formatting(heading_text)
                flowables.append(Paragraph(formatted_text, heading4_style))

            # Procesar listas no ordenadas con anidamiento
            elif line.lstrip().startswith('- ') or line.lstrip().startswith('* '):
                flowables.append(process_list_item(line))

            # Procesar listas numeradas con anidamiento
            elif line.lstrip().strip() and line.lstrip()[0].isdigit() and '. ' in line.lstrip():
                flowables.append(process_list_item(line, is_ordered=True))

            # Procesar citas
            elif line.startswith('> '):
                text = process_inline_formatting(line[2:])
                flowables.append(Paragraph(text, quote_style))

            # Procesar líneas horizontales
            elif line.strip() == '---' or line.strip() == '***' or line.strip() == '___':
                flowables.append(Paragraph("<hr width='100%'/>", styles['Normal']))
                flowables.append(Spacer(1, 5))

            # Procesar texto normal con formato
            elif line.strip():
                text = process_inline_formatting(line)
                flowables.append(Paragraph(text, styles['Normal']))

            # Líneas vacías
            else:
                flowables.append(Spacer(1, 10))

            i += 1

        # Construir el PDF
        doc.build(flowables)
        return True
    except Exception as e:
        logger.error(f"Error al convertir con reportlab: {str(e)}")
        traceback.print_exc()
        return False
