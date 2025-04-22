# Expert Nexus 🧠🔄

![Logo de Expert Nexus](https://raw.githubusercontent.com/bladealex9848/expert_nexus/main/assets/logo.png)

[![Version](https://img.shields.io/badge/versión-1.0.0-darkgreen.svg)](https://github.com/bladealex9848/expert_nexus)
[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.30.0-ff4b4b.svg)](https://streamlit.io/)
[![OpenAI](https://img.shields.io/badge/OpenAI_API-v2-00C244.svg)](https://platform.openai.com/)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-yellow.svg)](LICENSE)
[![Visitantes](https://api.visitorbadge.io/api/visitors?path=https%3A%2F%2Fexpertnexus.streamlit.app&label=Visitantes&labelColor=%235d5d5d&countColor=%231e7ebf&style=flat)](https://expertnexus.streamlit.app)

## 🧠 Descripción

Expert Nexus es un sistema avanzado de asistentes virtuales especializados que permite cambiar entre diferentes expertos durante una misma conversación, manteniendo siempre el contexto completo. Desarrollado con Streamlit y la API de OpenAI, este sistema ofrece acceso a múltiples dominios de conocimiento a través de una interfaz unificada.

La plataforma cuenta con expertos en áreas como transformación digital, inteligencia artificial, derecho constitucional, proceso civil, derecho disciplinario, entre muchos otros, permitiendo a los usuarios obtener respuestas especializadas sin perder el hilo de la conversación al cambiar de un dominio a otro.

## 🔍 Funcionalidades Principales

### 1. Múltiples Expertos en una Sola Interfaz
- **Asistentes Especializados**: Acceso a expertos en diversas áreas del conocimiento
- **Cambio Fluido**: Transición sin interrupciones entre diferentes especialistas
- **Persistencia de Contexto**: Mantenimiento del hilo completo de la conversación al cambiar de experto

### 2. Detección Automática de Temas
- **Análisis de Palabras Clave**: Sistema que identifica el tema principal del mensaje
- **Sugerencias Inteligentes**: Recomendación automática del experto más adecuado
- **Cambio Asistido**: Opción para aceptar o rechazar la sugerencia de cambio de experto

### 3. Visualización del Estado Actual
- **Identificación Clara**: Muestra qué experto está respondiendo en cada momento
- **Descripción del Experto**: Información sobre la especialidad del asistente actual
- **Historial de Cambios**: Registro cronológico de los expertos utilizados en la conversación

### 4. Control de la Conversación
- **Selector Manual**: Posibilidad de elegir manualmente el experto deseado
- **Reinicio de Sesión**: Opción para comenzar una nueva conversación cuando sea necesario
- **Interfaz Adaptativa**: Elementos visuales que reflejan el cambio de contexto

## 🚀 Instalación

### Requisitos Previos
- Python 3.8 o superior
- Pip (administrador de paquetes de Python)
- Cuenta en OpenAI con acceso a la API
- Múltiples asistentes configurados en OpenAI para diferentes especialidades

### Pasos de Instalación

#### Opción 1: Instalación Manual

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/bladealex9848/expert_nexus.git
   cd expert_nexus
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   python -m venv venv

   # En Windows
   venv\Scripts\activate

   # En macOS/Linux
   source venv/bin/activate
   ```

3. **Instalar las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

#### Opción 2: Instalación Automatizada

Se proporcionan scripts de automatización que detectan el sistema operativo, crean un entorno virtual, instalan las dependencias y ejecutan la aplicación:

1. **En Windows**

   Ejecuta el archivo `setup.bat` haciendo doble clic o desde la línea de comandos:
   ```bash
   setup.bat
   ```

   Alternativamente, puedes usar el script Bash universal:
   ```bash
   # Desde Git Bash, WSL o similar
   chmod +x setup.sh
   ./setup.sh
   ```

2. **En macOS/Linux**
   ```bash
   # Dar permisos de ejecución
   chmod +x setup_mac.sh

   # Ejecutar el script
   ./setup_mac.sh
   ```

   Alternativamente, puedes usar el script Bash universal:
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

Estos scripts automatizan todo el proceso de configuración, incluyendo:
- Detección del sistema operativo y tipo de terminal
- Creación y activación del entorno virtual
- Actualización de pip
- Instalación de dependencias
- Ejecución de la aplicación Streamlit

4. **Configurar credenciales de manera segura**

   **Opción A: Usando variables de entorno (Recomendado para desarrollo local)**
   ```bash
   # En Windows
   set OPENAI_API_KEY=tu-api-key-aqui
   set MISTRAL_API_KEY=tu-api-key-mistral-aqui
   set ASSISTANT_ID=tu-assistant-id-aqui

   # En macOS/Linux
   export OPENAI_API_KEY=tu-api-key-aqui
   export MISTRAL_API_KEY=tu-api-key-mistral-aqui
   export ASSISTANT_ID=tu-assistant-id-aqui
   ```

   **Opción B: Usando archivo secrets.toml (Recomendado para Streamlit Cloud)**

   Crea un archivo `.streamlit/secrets.toml` con la siguiente estructura:
   ```toml
   # Configuración estructurada por secciones
   [openai]
   api_key = "tu-api-key-aqui"
   api_model = "gpt-4-turbo" # Opcional: modelo a utilizar

   [mistral] # Opcional: si deseas usar Mistral AI para OCR
   api_key = "tu-api-key-mistral-aqui"

   # Variables directas para compatibilidad con la aplicación
   # IMPORTANTE: Estas variables son OBLIGATORIAS para que la aplicación funcione correctamente
   OPENAI_API_KEY = "tu-api-key-aqui"
   MISTRAL_API_KEY = "tu-api-key-mistral-aqui"
   # ASSISTANT_ID es necesario para la verificación inicial de la aplicación
   # Puede ser cualquiera de los IDs de la sección assistants
   ASSISTANT_ID = "asst_xxxx"

   [assistants]
   transformacion_digital = { id = "asst_xxxx", titulo = "Asistente especializado en transformación digital", descripcion = "Experto en procesos de transformación digital..." }
   inteligencia_artificial = { id = "asst_xxxx", titulo = "Asistente de Inteligencia Artificial", descripcion = "Especialista en IA..." }
   asistente_virtual = { id = "asst_RfRNo5Ij76ieg7mV11CqYV9v", titulo = "Asistente Virtual de Inteligencia Artificial", descripcion = "Ayudante virtual con conocimiento amplio en múltiples disciplinas" }
   # Añade más asistentes según sea necesario
   ```

   **Opción C: Usando archivos de configuración local (Para desarrollo)**

   Crea un archivo `assistants_config_local.py` con tus claves reales y añádelo al `.gitignore` para evitar subirlo al repositorio:
   ```python
   # Configuración de API Keys - NO SUBIR ESTE ARCHIVO AL REPOSITORIO
   OPENAI_API_KEY = "tu-api-key-real-aqui"
   MISTRAL_API_KEY = "tu-api-key-mistral-real-aqui"
   # Usar el ID del asistente virtual como predeterminado
   ASSISTANT_ID = "asst_RfRNo5Ij76ieg7mV11CqYV9v"
   ```

   > **IMPORTANTE SOBRE SEGURIDAD**:
   > - NUNCA incluyas claves API reales en el código fuente que subas a repositorios públicos
   > - Asegúrate de que los archivos con claves reales estén incluidos en `.gitignore`
   > - Para desarrollo local, usa variables de entorno o archivos de configuración local
   > - Para producción, usa servicios de secretos o variables de entorno seguras
   >
   > Si ves el mensaje "⚠️ Configuración incompleta" o "No se pudo cargar la configuración de expertos", verifica que hayas configurado correctamente las claves API y los IDs de los asistentes.

## ⚙️ Uso

### Iniciar la Aplicación

#### Opción 1: Ejecución Manual

```bash
streamlit run app.py
```

Esto lanzará la aplicación y abrirá automáticamente una ventana del navegador en `http://localhost:8501`.

#### Opción 2: Usando los Scripts de Automatización

Si utilizaste los scripts de automatización mencionados en la sección de instalación, la aplicación se iniciará automáticamente al final del proceso.

Para futuras ejecuciones, puedes volver a utilizar los mismos scripts:

- En Windows: `setup.bat` o `./setup.sh` (desde Git Bash)
- En macOS/Linux: `./setup_mac.sh` o `./setup.sh`

Los scripts detectarán que el entorno virtual ya existe y te preguntarán si deseas recrearlo o simplemente activarlo para continuar.

### Funcionalidades del Sistema

1. **Iniciar Conversación**
   - Comienza escribiendo tu mensaje en el campo de texto
   - El sistema iniciará con el experto predeterminado o sugerirá uno adecuado

2. **Cambiar de Experto Manualmente**
   - Selecciona el experto deseado en el menú desplegable de la barra lateral
   - Haz clic en "Cambiar a este experto" para confirmar

3. **Aceptar Sugerencias Automáticas**
   - Cuando el sistema detecte que otro experto podría ser más adecuado, te lo sugerirá
   - Puedes aceptar el cambio o continuar con el experto actual

4. **Visualizar el Historial**
   - Revisa el registro de cambios de experto en la barra lateral
   - Observa qué experto respondió cada mensaje en la conversación

5. **Reiniciar Conversación**
   - Utiliza el botón "Nueva Conversación" para comenzar un nuevo hilo
   - Todos los mensajes anteriores se mantendrán visibles hasta el reinicio

## ⚠️ Limitaciones

- La detección automática de temas se basa en palabras clave y puede no ser perfecta en todos los casos
- Aunque se mantiene el contexto, cada experto tiene su propia especialidad y enfoque
- La calidad de las respuestas depende de la configuración de cada asistente en OpenAI
- Las respuestas están limitadas por el conocimiento disponible hasta la fecha de entrenamiento
- El sistema no reemplaza la consulta con profesionales humanos especializados para casos críticos

## 📊 Escenarios de Uso

### 1. Entornos Educativos
- Estudiantes que necesitan explorar múltiples disciplinas en una misma sesión
- Docentes que desean ofrecer acceso a conocimiento especializado en diferentes materias
- Instituciones educativas que buscan complementar recursos de aprendizaje

### 2. Asesoría Jurídica
- Navegación entre diferentes áreas del derecho (constitucional, civil, laboral, etc.)
- Análisis de casos que requieren perspectivas desde múltiples especialidades legales
- Consultas preliminares antes de acudir a servicios legales especializados

### 3. Empresas y Organizaciones
- Equipos multidisciplinarios que requieren acceso a diferentes dominios de conocimiento
- Proyectos que abarcan diversas áreas (tecnología, finanzas, recursos humanos, etc.)
- Investigación y desarrollo que cruza múltiples campos de especialización

### 4. Investigación y Desarrollo
- Exploración de temas que requieren integración de diferentes disciplinas
- Consultas técnicas que evolucionan y abarcan múltiples dominios
- Generación de ideas desde diferentes perspectivas especializadas

## 👥 Contribuciones

Las contribuciones son bienvenidas. Para contribuir al desarrollo de Expert Nexus:

1. Realiza un fork del repositorio
2. Crea una nueva rama (`git checkout -b feature/nueva-funcionalidad`)
3. Implementa tus cambios
4. Envía un pull request

## 📝 Licencia

Este proyecto está bajo la licencia MIT. Consulta el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **OpenAI** por proporcionar la tecnología que impulsa los asistentes
- **Streamlit** por facilitar el desarrollo de interfaces intuitivas
- **Comunidad de desarrolladores** por su contribución a las bibliotecas utilizadas
- **Usuarios beta** por su valioso feedback durante el desarrollo

## 👤 Autor

Creado con ❤️ por [Alexander Oviedo Fadul](https://github.com/bladealex9848)

[GitHub](https://github.com/bladealex9848) | [Website](https://alexanderoviedofadul.dev) | [LinkedIn](https://www.linkedin.com/in/alexander-oviedo-fadul/) | [Instagram](https://www.instagram.com/alexander.oviedo.fadul) | [Twitter](https://twitter.com/alexanderofadul) | [Facebook](https://www.facebook.com/alexanderof/) | [WhatsApp](https://api.whatsapp.com/send?phone=573015930519&text=Hola%20!Quiero%20conversar%20contigo!%20)

---

## 💼 Mensaje Final

Expert Nexus representa un paso adelante en la interacción con asistentes virtuales, permitiendo una experiencia conversacional más fluida y especializada sin las limitaciones tradicionales de los chatbots de propósito único. La capacidad de cambiar entre expertos manteniendo el contexto abre nuevas posibilidades para el aprendizaje, la consultoría y la resolución de problemas complejos.

*"El verdadero poder del conocimiento no solo reside en la especialización, sino en la capacidad de transitar fluidamente entre diferentes dominios manteniendo una visión coherente e integrada."*