import streamlit as st
import os
import tempfile
import logging
import sys
import traceback
import re
import urllib.request
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intentar importar markdown con manejo de errores
try:
    import markdown
    logger.info("Módulo markdown importado correctamente")
except ImportError:
    st.error("Error: No se pudo importar el módulo 'markdown'. Instalando automáticamente...")
    import subprocess
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "markdown"])
        import markdown
        st.success("Módulo markdown instalado y importado correctamente")
    except Exception as e:
        st.error(f"No se pudo instalar el módulo markdown: {str(e)}")
        markdown = None

def convert_with_pypandoc(md_content, output_pdf):
    try:
        import pypandoc
        pypandoc.convert_text(md_content, 'pdf', format='md', outputfile=output_pdf)
        return True
    except ImportError:
        logger.error("No se pudo importar pypandoc. Asegúrate de que esté instalado.")
        return False
    except Exception as e:
        logger.error(f"Error al convertir con pypandoc: {str(e)}")
        return False

def convert_with_reportlab(md_content, output_pdf):
    try:
        # Configuración del documento PDF
        doc = SimpleDocTemplate(output_pdf, pagesize=letter)
        styles = getSampleStyleSheet()

        # Estilos personalizados
        bullet_style_level1 = ParagraphStyle(
            'BulletLevel1',
            parent=styles['Normal'],
            leftIndent=20,
            firstLineIndent=-15
        )

        bullet_style_level2 = ParagraphStyle(
            'BulletLevel2',
            parent=styles['Normal'],
            leftIndent=40,
            firstLineIndent=-15
        )

        bullet_style_level3 = ParagraphStyle(
            'BulletLevel3',
            parent=styles['Normal'],
            leftIndent=60,
            firstLineIndent=-15
        )

        heading3_style = ParagraphStyle(
            'CustomHeading3',
            parent=styles['Heading2'],
            fontSize=14
        )

        heading4_style = ParagraphStyle(
            'CustomHeading4',
            parent=styles['Heading2'],
            fontSize=12
        )

        code_style = ParagraphStyle(
            'CustomCode',
            parent=styles['Normal'],
            fontName='Courier',
            fontSize=9,
            leftIndent=20,
            rightIndent=20,
            backColor=colors.lightgrey,
            borderWidth=1,
            borderColor=colors.grey,
            borderPadding=5
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

                    # Crear un estilo con fondo gris y borde
                    code_block = Paragraph(code_text, code_style)
                    flowables.append(code_block)

                    code_content = []
                    in_code_block = False
                else:
                    # Inicio del bloque de código
                    in_code_block = True
                    # Capturar el lenguaje si está especificado
                    if len(line) > 3:
                        language = line[3:].strip()
                        if language:
                            # Añadir el lenguaje como una etiqueta antes del bloque de código
                            # pero no lo incluimos en el flowable todavía, lo guardaremos para después
                            code_content.append(f"<b>Lenguaje: {language}</b>")
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
                # Primero eliminar marcas de formato
                clean_text = re.sub(r'\*\*|\*|__|_|`', '', heading_text)
                # Convertir a minúsculas
                anchor_id = clean_text.lower()
                # Reemplazar espacios y caracteres especiales con guiones
                anchor_id = re.sub(r'\s+', '-', anchor_id)  # Espacios a guiones
                anchor_id = re.sub(r'[^a-z0-9_-]', '-', anchor_id)  # Otros caracteres a guiones
                # Eliminar guiones múltiples
                anchor_id = re.sub(r'-+', '-', anchor_id)
                # Eliminar guiones al inicio y final
                anchor_id = anchor_id.strip('-')

                # Aplicar formato en línea al texto del encabezado y añadir ancla
                formatted_text = f'<a name="{anchor_id}"/>' + process_inline_formatting(heading_text)
                flowables.append(Paragraph(formatted_text, styles['Title']))

            elif line.startswith('## '):
                heading_text = line[3:]
                # Primero eliminar marcas de formato
                clean_text = re.sub(r'\*\*|\*|__|_|`', '', heading_text)
                # Convertir a minúsculas
                anchor_id = clean_text.lower()
                # Reemplazar espacios y caracteres especiales con guiones
                anchor_id = re.sub(r'\s+', '-', anchor_id)  # Espacios a guiones
                anchor_id = re.sub(r'[^a-z0-9_-]', '-', anchor_id)  # Otros caracteres a guiones
                # Eliminar guiones múltiples
                anchor_id = re.sub(r'-+', '-', anchor_id)
                # Eliminar guiones al inicio y final
                anchor_id = anchor_id.strip('-')

                formatted_text = f'<a name="{anchor_id}"/>' + process_inline_formatting(heading_text)
                flowables.append(Paragraph(formatted_text, styles['Heading2']))

            elif line.startswith('### '):
                heading_text = line[4:]
                # Primero eliminar marcas de formato
                clean_text = re.sub(r'\*\*|\*|__|_|`', '', heading_text)
                # Convertir a minúsculas
                anchor_id = clean_text.lower()
                # Reemplazar espacios y caracteres especiales con guiones
                anchor_id = re.sub(r'\s+', '-', anchor_id)  # Espacios a guiones
                anchor_id = re.sub(r'[^a-z0-9_-]', '-', anchor_id)  # Otros caracteres a guiones
                # Eliminar guiones múltiples
                anchor_id = re.sub(r'-+', '-', anchor_id)
                # Eliminar guiones al inicio y final
                anchor_id = anchor_id.strip('-')

                formatted_text = f'<a name="{anchor_id}"/>' + process_inline_formatting(heading_text)
                flowables.append(Paragraph(formatted_text, heading3_style))

            elif line.startswith('#### '):
                heading_text = line[5:]
                # Primero eliminar marcas de formato
                clean_text = re.sub(r'\*\*|\*|__|_|`', '', heading_text)
                # Convertir a minúsculas
                anchor_id = clean_text.lower()
                # Reemplazar espacios y caracteres especiales con guiones
                anchor_id = re.sub(r'\s+', '-', anchor_id)  # Espacios a guiones
                anchor_id = re.sub(r'[^a-z0-9_-]', '-', anchor_id)  # Otros caracteres a guiones
                # Eliminar guiones múltiples
                anchor_id = re.sub(r'-+', '-', anchor_id)
                # Eliminar guiones al inicio y final
                anchor_id = anchor_id.strip('-')

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

# Función auxiliar para procesar formato en línea (negritas, cursivas, etc.)
def process_inline_formatting(text):
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

def convert_md_to_pdf(md_file, output_folder):
    try:
        # Leer el contenido del archivo MD
        with open(md_file, 'r', encoding='utf-8') as file:
            md_content = file.read()

        # Preparar el nombre del archivo de salida
        output_pdf = os.path.join(output_folder, os.path.splitext(os.path.basename(md_file))[0] + '.pdf')

        # Intentar conversión con pypandoc
        if convert_with_pypandoc(md_content, output_pdf):
            logger.info("Conversión exitosa con pypandoc")
            return output_pdf

        # Si falla, usar reportlab como última opción
        try:
            if convert_with_reportlab(md_content, output_pdf):
                logger.info("Conversión exitosa con reportlab")
                return output_pdf
        except ValueError as ve:
            # Manejar específicamente errores de enlaces
            if "format not resolved" in str(ve) and "missing URL scheme or undefined destination target" in str(ve):
                target = str(ve).split("'")[-2] if "'" in str(ve) else "desconocido"
                logger.error(f"Error en enlaces internos: No se pudo resolver el enlace a '{target}'. "
                            f"Esto puede ocurrir cuando un enlace apunta a una sección que no existe o tiene formato incorrecto.")
                # Intentar nuevamente con una versión modificada que ignore enlaces problemáticos
                try:
                    # Modificar el contenido para marcar los enlaces problemáticos
                    modified_content = md_content.replace(f"(#{target})", f"(#ERROR-ENLACE-{target})")
                    if convert_with_reportlab(modified_content, output_pdf):
                        logger.warning(f"Conversión completada con advertencias: Algunos enlaces internos pueden no funcionar correctamente.")
                        return output_pdf
                except Exception as retry_error:
                    logger.error(f"Error en segundo intento: {str(retry_error)}")
            else:
                # Otros errores de ValueError
                logger.error(f"Error de valor en la conversión: {str(ve)}")
        except Exception as e:
            # Otros errores en reportlab
            logger.error(f"Error en la conversión con reportlab: {str(e)}")
            traceback.print_exc()

        # Si todas las conversiones fallan, registrar un error
        logger.error("Todas las conversiones fallaron")
        return None
    except Exception as e:
        logger.error(f"Error inesperado en convert_md_to_pdf: {str(e)}")
        traceback.print_exc()
        return None

def main():
    try:
        st.title("MDPDFusion: Convertidor de Markdown a PDF")

        # Selección de archivos MD
        md_files = st.file_uploader("Selecciona los archivos Markdown (.md)", type=['md'], accept_multiple_files=True)

        if md_files:
            # Crear una carpeta temporal para los archivos de salida
            with tempfile.TemporaryDirectory() as output_folder:
                for md_file in md_files:
                    # Guardar el archivo subido temporalmente
                    temp_md_path = os.path.join(output_folder, md_file.name)
                    with open(temp_md_path, 'wb') as temp_file:
                        temp_file.write(md_file.getvalue())

                    # Convertir MD a PDF
                    pdf_path = convert_md_to_pdf(temp_md_path, output_folder)

                    if pdf_path and os.path.exists(pdf_path):
                        # Ofrecer el archivo PDF para descarga
                        with open(pdf_path, 'rb') as pdf_file:
                            st.download_button(
                                label=f"Descargar {os.path.basename(pdf_path)}",
                                data=pdf_file,
                                file_name=os.path.basename(pdf_path),
                                mime="application/pdf"
                            )
                    else:
                        st.error(f"No se pudo convertir {md_file.name} a PDF. Por favor, revisa el archivo de entrada.")
    except Exception as e:
        st.error(f"Error inesperado: {str(e)}")
        logger.error(f"Error inesperado en main: {str(e)}")
        logger.error(traceback.format_exc())

if __name__ == "__main__":
    main()