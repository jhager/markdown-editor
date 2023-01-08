import sys
from PyQt5.QtWidgets import QApplication, QAction, QMainWindow, QTextEdit, QFileDialog, QSplitter
from PyQt5.QtCore import QUrl, QSettings
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage, QWebEngineProfile




import markdown
import json
import base64
import os
import math

class MyWebEngineView(QWebEngineView):
    def acceptNavigationRequest(self, url, type, isMainFrame):
        print ("acceptNavigationRequest " + url)
        if type == QWebEnginePage.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(url)
            return False
        return super().acceptNavigationRequest(url, type, isMainFrame)

class WebEngineUrlRequestInterceptor(QWebEngineUrlRequestInterceptor):
    def interceptRequest(self, info):
        pass
#        print("loading...")
#        print(info.requestUrl()) 

class MyWebEnginePage(QWebEnginePage):
    def acceptNavigationRequest(self, url, _type, isMainFrame):
#        print("acceptNavigationRequest for ...")
#        print(url)
        if _type == QWebEnginePage.NavigationTypeLinkClicked:
            QDesktopServices.openUrl(url)
            return False
        return QWebEnginePage.acceptNavigationRequest(self, url, _type, isMainFrame)


class MarkdownEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings('MarkdownEditor', 'MarkdownEditor')
        self.current_file = ''
        # Create the text edit widgets for the markdown source and the rendered document
        self.source_text_edit = QTextEdit()
        self.preview_text_edit = MyWebEngineView()
        self.interceptor = WebEngineUrlRequestInterceptor()
        self.profile = QWebEngineProfile()
        self.profile.setRequestInterceptor(self.interceptor)
        page = MyWebEnginePage(self.profile, self.preview_text_edit)
        self.preview_text_edit.setPage(page)

        #todo self.preview_text_edit.anchorClicked.connect(self.open_link)
        # Create the layout
        layout = QSplitter()
        layout.setContentsMargins(0,0,0,0)
        layout.setSizes([50, 50])
        layout.addWidget(self.source_text_edit)
        layout.addWidget(self.preview_text_edit)
	# Connect the textChanged signal of the source text edit to the update function
        self.source_text_edit.textChanged.connect(self.update)
        self.source_text_edit.setAcceptRichText(False)
        # Connect the keyPressEvent signal of the source text edit to the paste_as_plain_text function
       # self.source_text_edit.keyPressEvent = self.paste_as_plain_text

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

        # Create a View menu and add it to the menu bar
        view_menu = menu_bar.addMenu('View')
        # Create the "Dark Mode" action and add it to the View menu
        dark_mode_action = QAction('Dark Mode', self, checkable=True)
        view_menu.addAction(dark_mode_action)
        # Connect the triggered signal of the "Dark Mode" action to a function that applies the dark mode style
        dark_mode_action.triggered[bool].connect(self.apply_dark_mode)
        dark_mode = self.settings.value('dark_mode', False)
        dark_mode_action.setChecked(dark_mode)
        self.apply_dark_mode(dark_mode)

        # Add the "Full Screen" action only for Windows
        if sys.platform == 'win32':
            # Create the "Full Screen" action and add it to the View menu
            full_screen_action = QAction('Full Screen', self, checkable=True)
            view_menu.addAction(full_screen_action)
            full_screen_action.triggered[bool].connect(self.toggle_full_screen)
            full_screen_action.setShortcut('Ctrl+F')



        # Create a Help menu and add it to the menu bar
        help_menu = menu_bar.addMenu('Help')
        # Create the "Markdown Syntax" action and add it to the Help menu
        markdown_syntax_action = QAction('Markdown Syntax', self)
        help_menu.addAction(markdown_syntax_action)
        markdown_syntax_action.triggered.connect(self.open_markdown_syntax)

        self.setCentralWidget(layout)
        layout.show()
        # Set the window properties
        self.setWindowTitle('Markdown Editor')
        self.setGeometry(100, 100, 800, 600)

        #Restore the size and position of the window from the settings file
        if self.settings.value('geometry') is not None:
            self.restoreGeometry(self.settings.value('geometry'))
        if self.settings.value('state') is not None:
            self.restoreState(self.settings.value('state'))

        self.source_text_edit.resize(math.floor(self.geometry().width()/2), self.geometry().height())
        self.preview_text_edit.resize(math.floor(self.geometry().width()/2), self.geometry().height())
        self.update()

    
    def update(self):
        # Get the markdown source from the source text edit
        source = self.source_text_edit.toPlainText()
        # Render the markdown source to HTML
        renderer = markdown.Markdown(extensions=["fenced_code"])
        html = renderer.convert(source)
        # Set the HTML as the content of the rendered text edit
        html = renderer.convert(source)
        html = html.replace('\n</code></pre>', '</code></pre>')
        # Set the HTML as the content of the rendered text edit, including a style sheet for <pre> blocks
        finalHtml = (
           f'<html><head><style>pre {{ display: block; font-size:14px; padding: 20px; background-color: #666; border-radius: 5px; margin-left: 40; margin-right:40; }} body {{background-color: #333; color: #CCC;"}}</style></head><body>{html}</body></html>'
        )

        self.preview_text_edit.setHtml(finalHtml)

    def save(self):
        if self.current_file is not None and len(self.current_file) > 0:
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

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.write_settings()
 
    def moveEvent(self, event):
        # Call the superclass implementation of the moveEvent method
        super().moveEvent(event)
        self.write_settings()


    def write_settings(self):
        # Save the size and position of the window to the settings file
        self.settings.setValue('geometry', self.saveGeometry())
        self.settings.setValue('state', self.saveState())

    def toggle_full_screen(self): 
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def open_markdown_syntax(self):
        # Open the "Markdown Syntax" page in the system's default web browser
        QDesktopServices.openUrl(QUrl('https://commonmark.org/help/'))

    def apply_dark_mode(self, checked):
        self.settings.setValue('dark_mode', checked)
        if checked:
            # Set the dark mode style sheet
            self.setStyleSheet("""
                QWidget {
                    background-color: #333333;
                    color: #ffffff;
                }
                QTextEdit {
                    background-color: #444444;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #222222;
                    color: #ffffff;
                }
                QMenu {
                    background-color: #222222;
                    color: #ffffff;
                }
                QMenu::item {
                    background-color: #222222;
                    color: #ffffff;
                }
                QMenu::item:selected {
                    background-color: #555555;
                }
            """)
        else:
            # Reset the style sheet to the default
            self.setStyleSheet('')


app = QApplication(sys.argv)
editor = MarkdownEditor()
editor.show()
sys.exit(app.exec_())
