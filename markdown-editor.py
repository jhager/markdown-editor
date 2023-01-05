import sys
from PyQt5.QtWidgets import QApplication, QAction, QMainWindow, QTextEdit, QVBoxLayout, QHBoxLayout, QPushButton, QWidget, QFileDialog, QTextBrowser
from PyQt5.QtCore import QByteArray, QUrl
from PyQt5.QtGui import QDesktopServices
import markdown
import json
import base64
import os

class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_file = ''
        # Create the text edit widgets for the markdown source and the rendered document
        self.source_text_edit = QTextEdit()
        self.preview_text_edit = QTextBrowser()
        self.preview_text_edit.anchorClicked.connect(self.open_link)
        # Create the layout
        layout = QHBoxLayout()
        layout.addWidget(self.source_text_edit)
        layout.addWidget(self.preview_text_edit)
	# Connect the textChanged signal of the source text edit to the update function
        self.source_text_edit.textChanged.connect(self.update)

	# Create a menu bar
        menu_bar = self.menuBar()
        # Create a file menu and add it to the menu bar
        file_menu = menu_bar.addMenu('File')
        # Create the Save action and add it to the file menu
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        file_menu.addAction(save_action)
        # Connect the triggered signal of the Save action to the save function
        save_action.triggered.connect(self.save)
        # Create the Open action and add it to the file menu
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        file_menu.addAction(open_action)
        # Connect the triggered signal of the Open action to the open_file function
        open_action.triggered.connect(self.open_file)

        # Create the central widget and set the layout
        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)
        # Set the window properties
        self.setWindowTitle('Markdown Editor')
        self.setGeometry(100, 100, 800, 600)

        #Restore the size and position of the window from the settings file
        self.restoreGeometry(self.read_settings('geometry'))
        self.restoreState(self.read_settings('state'))
    
    def update(self):
        # Get the markdown source from the source text edit
        source = self.source_text_edit.toPlainText()
        # Render the markdown source to HTML
        html = markdown.markdown(source)
        # Set the HTML as the content of the rendered text edit
        self.preview_text_edit.setHtml(html)


    def save(self):
        if self.current_file is not None:
           with open(self.current_file, 'w') as f:
              f.write(self.source_text_edit.toPlainText())
        else:
           self.saveUsingSaveDialog() 

    def saveUsingSaveDialog(self):
        # Get the markdown source from the source text edit
        source = self.source_text_edit.toPlainText()
        # Show the save file dialog
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getSaveFileName(self, 'Save File', '', 'Markdown Files (*.md);;Text Files (*.txt)', options=options)
        if file_name:
            # Save the source to the selected file
            with open(file_name, 'w') as f:
                f.write(source)

    def open_file(self):
        # Show the open file dialog
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_name, _ = QFileDialog.getOpenFileName(self, 'Open File', '', 'Markdown Files (*.md);;Text Files (*.txt)', options=options)
        if file_name:
            # Open the selected file and read its contents
            with open(file_name, 'r') as f:
                source = f.read()
            # Set the contents of the source text edit
            self.source_text_edit.setPlainText(source)
            self.current_file = file_name
            # Update the rendered document
            self.update()
            self.setWindowTitle(f"Markdown Editor - {os.path.basename(file_name)}")

    def read_settings(self, key):
        try:
            # Try to open the settings file
            with open('.markdown-editor-settings.json', 'r') as f:
                settings = json.loads(f.read())
        except (FileNotFoundError, ValueError):
            # If the file does not exist, create it with default settings
            with open('settings.ini', 'w') as f:
                settings = {}
        # Return the value of the specified key from the settings
        return QByteArray(base64.b64decode(settings.get(key, '')))

    def resizeEvent(self, event):
        self.write_settings()
 
    def write_settings(self):
        # Save the size and position of the window to the settings file
        with open('.markdown-editor-settings.json', 'w') as f:
            # Convert the dictionary to a string and write it to the file
            geometry = base64.b64encode(self.saveGeometry().data()).decode('utf-8')
            state = base64.b64encode(self.saveState().data()).decode('utf-8')
            f.write(json.dumps({
                'geometry': geometry,
                'state': state 
            }))

    def open_link(self, url):
        # Open the link in the system's external web browser
        QDesktopServices.openUrl(QUrl(url))

app = QApplication(sys.argv)
editor = MarkdownEditor()
editor.show()
sys.exit(app.exec_())

