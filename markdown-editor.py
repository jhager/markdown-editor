import functools
import math
import mistune
import os
import sys

from PyQt5.QtCore import (
    QSettings,
    QUrl,
)
from PyQt5.QtGui import (
    QDesktopServices,
)
from PyQt5.QtPrintSupport import QPrinter

from PyQt5.QtWebEngineWidgets import (
    QWebEngineProfile,
)
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QMainWindow,
    QSplitter,
    QTextEdit,
)

from webengine import (
    MyWebEngineView,
    WebEngineUrlRequestInterceptor,
    MyWebEnginePage
)

from searchbox import (
    SearchBox
)


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
        self.page = MyWebEnginePage(self.profile, self.preview_text_edit)
        self.preview_text_edit.setPage(self.page)
        self.page.setParent(self.profile)


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
        # Create the "Export" action and add it to the "File" menu
        export_action = QAction("Export to PDF", self)
        export_action.setShortcut('Ctrl+E')
        file_menu.addAction(export_action)
        # Connect the triggered signal of the "Export" action to the export_pdf function
        export_action.triggered.connect(self.export_pdf)

        edit_menu = menu_bar.addMenu('Edit')
        find_action = QAction('Find', self)
        find_action.setShortcut('Ctrl+F')
        edit_menu.addAction(find_action)
        find_action.triggered.connect(self.show_find_box)

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

        view_menu.addSeparator()
        # create a new "Styles" menu
        styles_menu = view_menu.addMenu("Styles")
        
        self.current_css = None
        # iterate through all files in the "styles" folder
        path = "styles"
        for filename in os.listdir(path):
            if filename.endswith(".css"):
                css_action = QAction(filename[:-4], self)
                css_action.triggered.connect(functools.partial(self.change_css, filename))
                css_action.setCheckable(True)
                styles_menu.addAction(css_action)
                if filename == "default.css":
                    css_action.setChecked(True)
                    self.current_css = css_action
                else:
                    css_action.setChecked(False)

        styles_menu.addSeparator()
        reload_action = QAction("Reload CSS", self)
        reload_action.setShortcut("Ctrl+R")
        reload_action.triggered.connect(self.reload_css)
        styles_menu.addAction(reload_action)

        # Add the "Full Screen" action only for Windows
        if sys.platform == 'win32':
            # Create the "Full Screen" action and add it to the View menu
            full_screen_action = QAction('Full Screen', self, checkable=True)
            view_menu.addAction(full_screen_action)
            full_screen_action.triggered[bool].connect(self.toggle_full_screen)
            full_screen_action.setShortcut(Qt.Key_F11)

        # Create a list of all the plugins
        plugins = [
            'strikethrough',
            'footnotes',
            'table',
            'url',
            'task_lists',
            'def_list',
            'abbr',
            'mark',
            'insert',
            'superscript',
            'subscript',
            'math',
            'ruby',
            'spoiler',
        ]

        # Create a dictionary to store the QAction objects for each plugin
        self.plugin_actions = {}
        self.enabled_plugins = []

        # Create a Markdown menu and add it to the menu bar
        markdown_menu = self.menuBar().addMenu('Markdown')

        # Create a QAction for each plugin and add it to the Markdown menu
        for plugin in plugins:
            action = QAction(plugin, self, checkable=True)
            markdown_menu.addAction(action)
            self.plugin_actions[plugin] = action

        # Connect the triggered signal of each QAction to a function that updates the list of enabled plugins
        for action in self.plugin_actions.values():
            action.triggered.connect(self.update_enabled_plugins)
        
        self.load_enabled_plugins()

        # Create a Help menu and add it to the menu bar
        help_menu = menu_bar.addMenu('Help')
        # Create the "Markdown Syntax" action and add it to the Help menu
        markdown_syntax_action = QAction('Markdown Syntax', self)
        help_menu.addAction(markdown_syntax_action)
        markdown_syntax_action.triggered.connect(self.open_markdown_syntax)

        with open('styles/default.css', 'r') as f:
            self.css = f.read()

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
        #print (self.enabled_plugins)
        # Render the markdown source to HTML
        markdown = mistune.create_markdown(plugins=self.enabled_plugins)

        html = markdown(source)
        # Set the HTML as the content of the rendered text edit
        html = html.replace('\n</code></pre>', '</code></pre>')
        # Set the HTML as the content of the rendered text edit, including a style sheet for <pre> blocks
        finalHtml = (
           f'<html><head><style>{self.css}</style></head><body>{html}</body></html>'
        )
        #print(finalHtml)

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

    def print_finished(self,result):
       self.printer = None

    def export_pdf(self):
        # Open a file dialog to let the user choose the PDF file to save
        file_name, _ = QFileDialog.getSaveFileName(self, "Export PDF", "", "PDF files (*.pdf)")
        if file_name:
            self.preview_text_edit.page().runJavaScript("window.scrollTo(0, 0);")
            # Create a QPrinter object and set its output format to PDF
            self.printer = QPrinter(QPrinter.HighResolution)
            self.printer.setOutputFormat(QPrinter.PdfFormat)
            self.printer.setOutputFileName(file_name)
            # Render the contents of the preview pane to the PDF file
            self.preview_text_edit.page().print(self.printer, self.print_finished)

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

    def show_find_box(self):
        self.search_box = SearchBox(parent=self.source_text_edit)
        self.search_box.setFixedWidth(500)  # Set the width to 300 pixels
        self.search_box.show()

    def update_enabled_plugins(self):
        # Get the list of enabled plugins from the QAction objects
        self.enabled_plugins = [
            plugin for plugin, action in self.plugin_actions.items()
            if action.isChecked()
        ]
        self.update()
        # Save the list of enabled plugins as a setting using QSettings
        self.settings.setValue('enabled_plugins', self.enabled_plugins)

    def load_enabled_plugins(self):
        # Load the list of enabled plugins from the settings using QSettings
        self.enabled_plugins = self.settings.value('enabled_plugins', ['strikethrough', 'footnotes', 'table'])
        # Set the state of the QAction objects for the enabled plugins to checked
        for plugin, action in self.plugin_actions.items():
            action.setChecked(plugin in self.enabled_plugins)

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
                    background-color: #333333;
                    color: #ffffff;
                }
                QMenuBar {
                    background-color: #333333;
                    color: #ffffff;
                }
                QMenu {
                    background-color: #333333;
                    color: #ffffff;
                }
                QMenu::item {
                    background-color: #333333;
                    color: #ffffff;
                }
                QMenu::item:selected {
                    background-color: #555555;
                }
            """)
        else:
            # Reset the style sheet to the default
            self.setStyleSheet('')

    def change_css(self, filename):
        print("CHANGE CSS")
        if self.current_css is not None:
            self.current_css.setChecked(False)
        self.current_css = self.sender()
        self.current_css.setChecked(True)
        with open(f'styles/{filename}', 'r') as f:
            self.css = f.read()
        print(self.css)
        self.update()
    
    def reload_css(self):
        with open(f'styles/{self.current_css.text()}.css', 'r') as f:
            self.css = f.read()
        self.update()

app = QApplication(sys.argv)
editor = MarkdownEditor()
editor.show()
sys.exit(app.exec_())