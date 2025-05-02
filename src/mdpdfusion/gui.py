"""
Módulo para la interfaz gráfica de MDPDFusion usando PyQt5.
"""

import os
import sys
import logging
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, 
                            QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, 
                            QListWidget, QProgressBar, QMessageBox, QStyle)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QMimeData, QUrl
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QIcon

from .core import convert_md_to_pdf

# Configurar logging
logger = logging.getLogger("mdpdfusion.gui")

class ConversionThread(QThread):
    """Hilo para realizar la conversión en segundo plano."""
    update_progress = pyqtSignal(int, int)  # (current, total)
    conversion_done = pyqtSignal(str, bool)  # (file_path, success)
    
    def __init__(self, files, output_dir):
        super().__init__()
        self.files = files
        self.output_dir = output_dir
        
    def run(self):
        total = len(self.files)
        for i, file_path in enumerate(self.files):
            try:
                self.update_progress.emit(i + 1, total)
                output_pdf = convert_md_to_pdf(file_path, self.output_dir)
                success = output_pdf is not None and os.path.exists(output_pdf)
                self.conversion_done.emit(file_path, success)
            except Exception as e:
                logger.error(f"Error al convertir {file_path}: {str(e)}")
                self.conversion_done.emit(file_path, False)

class DropArea(QLabel):
    """Área para arrastrar y soltar archivos."""
    files_dropped = pyqtSignal(list)
    
    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setText("Arrastra archivos Markdown (.md) aquí")
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 30px;
                background-color: #f8f8f8;
                font-size: 16px;
            }
        """)
        self.setAcceptDrops(True)
        
    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet("""
                QLabel {
                    border: 2px dashed #3498db;
                    border-radius: 5px;
                    padding: 30px;
                    background-color: #e8f4fc;
                    font-size: 16px;
                }
            """)
        
    def dragLeaveEvent(self, event):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 30px;
                background-color: #f8f8f8;
                font-size: 16px;
            }
        """)
        
    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("""
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                padding: 30px;
                background-color: #f8f8f8;
                font-size: 16px;
            }
        """)
        
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.accept()
            
            files = []
            for url in event.mimeData().urls():
                if url.isLocalFile():
                    file_path = url.toLocalFile()
                    if file_path.lower().endswith('.md'):
                        files.append(file_path)
            
            if files:
                self.files_dropped.emit(files)

class MDPDFusionGUI(QMainWindow):
    """Ventana principal de la aplicación."""
    def __init__(self):
        super().__init__()
        self.initUI()
        self.conversion_thread = None
        
    def initUI(self):
        self.setWindowTitle('MDPDFusion - Convertidor de Markdown a PDF')
        self.setGeometry(100, 100, 600, 400)
        
        # Icono de la aplicación
        self.setWindowIcon(self.style().standardIcon(QStyle.SP_FileIcon))
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout principal
        main_layout = QVBoxLayout(central_widget)
        
        # Área para arrastrar y soltar
        self.drop_area = DropArea()
        self.drop_area.files_dropped.connect(self.add_files)
        main_layout.addWidget(self.drop_area)
        
        # Lista de archivos
        self.file_list = QListWidget()
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #ccc;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        main_layout.addWidget(self.file_list)
        
        # Barra de progreso
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        main_layout.addWidget(self.progress_bar)
        
        # Botones
        button_layout = QHBoxLayout()
        
        self.btn_add = QPushButton('Añadir archivos')
        self.btn_add.clicked.connect(self.browse_files)
        button_layout.addWidget(self.btn_add)
        
        self.btn_clear = QPushButton('Limpiar lista')
        self.btn_clear.clicked.connect(self.clear_files)
        button_layout.addWidget(self.btn_clear)
        
        self.btn_convert = QPushButton('Convertir a PDF')
        self.btn_convert.clicked.connect(self.start_conversion)
        self.btn_convert.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #ccc;
            }
        """)
        button_layout.addWidget(self.btn_convert)
        
        main_layout.addLayout(button_layout)
        
    def browse_files(self):
        """Abre un diálogo para seleccionar archivos."""
        files, _ = QFileDialog.getOpenFileNames(
            self, 'Seleccionar archivos Markdown', '', 'Archivos Markdown (*.md)'
        )
        if files:
            self.add_files(files)
            
    def add_files(self, files):
        """Añade archivos a la lista."""
        for file_path in files:
            # Comprobar si el archivo ya está en la lista
            items = self.file_list.findItems(file_path, Qt.MatchExactly)
            if not items:
                self.file_list.addItem(file_path)
        
        # Habilitar el botón de conversión si hay archivos
        self.btn_convert.setEnabled(self.file_list.count() > 0)
        
    def clear_files(self):
        """Limpia la lista de archivos."""
        self.file_list.clear()
        self.btn_convert.setEnabled(False)
        
    def start_conversion(self):
        """Inicia el proceso de conversión."""
        if self.file_list.count() == 0:
            return
        
        # Obtener directorio de salida
        output_dir = QFileDialog.getExistingDirectory(
            self, 'Seleccionar directorio de salida'
        )
        
        if not output_dir:
            return
        
        # Recopilar archivos
        files = []
        for i in range(self.file_list.count()):
            files.append(self.file_list.item(i).text())
        
        # Deshabilitar controles durante la conversión
        self.btn_add.setEnabled(False)
        self.btn_clear.setEnabled(False)
        self.btn_convert.setEnabled(False)
        self.drop_area.setEnabled(False)
        
        # Mostrar barra de progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_bar.setMaximum(len(files))
        
        # Iniciar hilo de conversión
        self.conversion_thread = ConversionThread(files, output_dir)
        self.conversion_thread.update_progress.connect(self.update_progress)
        self.conversion_thread.conversion_done.connect(self.conversion_done)
        self.conversion_thread.finished.connect(self.conversion_finished)
        self.conversion_thread.start()
        
    def update_progress(self, current, total):
        """Actualiza la barra de progreso."""
        self.progress_bar.setValue(current)
        
    def conversion_done(self, file_path, success):
        """Maneja el resultado de la conversión de un archivo."""
        file_name = os.path.basename(file_path)
        if success:
            logger.info(f"Conversión exitosa: {file_path}")
            # Marcar como completado en la lista
            for i in range(self.file_list.count()):
                if self.file_list.item(i).text() == file_path:
                    self.file_list.item(i).setText(f"{file_path} ✓")
                    self.file_list.item(i).setForeground(Qt.green)
                    break
        else:
            logger.error(f"Error al convertir: {file_path}")
            # Marcar como fallido en la lista
            for i in range(self.file_list.count()):
                if self.file_list.item(i).text() == file_path:
                    self.file_list.item(i).setText(f"{file_path} ✗")
                    self.file_list.item(i).setForeground(Qt.red)
                    break
        
    def conversion_finished(self):
        """Maneja la finalización del proceso de conversión."""
        # Habilitar controles
        self.btn_add.setEnabled(True)
        self.btn_clear.setEnabled(True)
        self.btn_convert.setEnabled(True)
        self.drop_area.setEnabled(True)
        
        # Ocultar barra de progreso
        self.progress_bar.setVisible(False)
        
        # Mostrar mensaje de finalización
        QMessageBox.information(
            self, 'Conversión completada', 
            'El proceso de conversión ha finalizado.'
        )

def main():
    """Función principal para iniciar la interfaz gráfica."""
    app = QApplication(sys.argv)
    window = MDPDFusionGUI()
    window.show()
    sys.exit(app.exec_())
