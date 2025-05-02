# Pruebas de Conversión Markdown a PDF

Este directorio contiene scripts para probar la conversión de archivos Markdown a PDF en Expert Nexus.

## Estructura del Directorio

```
conversion_tests/
├── README.md                         # Este archivo
├── run_tests.py                      # Script principal para ejecutar todas las pruebas
├── test_conversion.py                # Prueba todos los métodos de conversión
├── test_streamlit_cloud_conversion.py # Prueba específica para el método de Streamlit Cloud
├── samples/                          # Archivos Markdown de muestra
│   ├── test_sample.md                # Muestra básica con elementos comunes
│   ├── advanced_sample.md            # Muestra con características avanzadas
│   └── conversation_sample.md        # Muestra que simula una conversación
└── results/                          # Directorio donde se guardan los PDFs generados
    └── test_report.md                # Informe generado automáticamente
```

## Requisitos Previos

Antes de ejecutar las pruebas, asegúrate de tener instaladas las siguientes dependencias:

```bash
pip install pdfkit markdown2 pygments weasyprint fpdf2 reportlab
```

Para el método `pdfkit`, también necesitas tener instalado `wkhtmltopdf`:

- **macOS**: `brew install wkhtmltopdf`
- **Linux**: `apt-get install wkhtmltopdf`
- **Windows**: Descarga e instala desde [wkhtmltopdf.org](https://wkhtmltopdf.org/downloads.html)

## Cómo Ejecutar las Pruebas

1. Navega al directorio de pruebas:

```bash
cd tests/conversion_tests
```

2. Ejecuta el script principal:

```bash
python run_tests.py
```

Este script ejecutará todas las pruebas y generará un informe en el directorio `results/`.

## Métodos de Conversión Probados

1. **Método Streamlit Cloud**: Utiliza `pdfkit` y `markdown2` para la conversión, optimizado para funcionar en Streamlit Cloud.
2. **Método Primario**: Utiliza `fpdf2` para la conversión.
3. **Método Secundario**: Utiliza `reportlab` para la conversión.
4. **Método de Respaldo**: Método simple de conversión como último recurso.

## Interpretación de los Resultados

Después de ejecutar las pruebas, se generarán varios archivos PDF en el directorio `results/`. Cada archivo tiene un sufijo que indica el método de conversión utilizado:

- `*_streamlit_cloud.pdf`: Generado con el método optimizado para Streamlit Cloud
- `*_primary.pdf`: Generado con el método primario (FPDF)
- `*_secondary.pdf`: Generado con el método secundario (ReportLab)
- `*_fallback.pdf`: Generado con el método de respaldo

Examina visualmente estos archivos para verificar que la conversión mantiene el formato, los colores, las imágenes y los diagramas ASCII correctamente.

## Solución de Problemas

Si encuentras errores durante la ejecución de las pruebas:

1. Verifica que todas las dependencias estén instaladas correctamente.
2. Asegúrate de que `wkhtmltopdf` esté instalado y accesible en el PATH del sistema.
3. Revisa el archivo de registro `conversion_tests.log` para obtener información detallada sobre los errores.

## Adaptación a la Aplicación Principal

Los métodos de conversión probados aquí son los mismos que se utilizan en la aplicación principal. Si encuentras un método que funciona mejor para tu caso de uso, puedes modificar la función `export_chat_to_pdf` en `app.py` para priorizar ese método.
