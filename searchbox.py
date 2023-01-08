
from PyQt5.QtCore import (
    QEvent,
    Qt
)
from PyQt5.QtGui import (
    QTextDocument,
)

from PyQt5.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QWidget,
)

class SearchBox(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Tool)
        self.line_edit = QLineEdit(self)
        self.next_button = QPushButton("\u2193", self)
        self.prev_button = QPushButton("\u2191", self)
        layout = QHBoxLayout(self)
        layout.addWidget(self.line_edit)
        layout.addWidget(self.next_button)
        layout.addWidget(self.prev_button)
        # Add the "case sensitive" checkbox
        self.case_sensitive_checkbox = QCheckBox("Match Case")
        layout.addWidget(self.case_sensitive_checkbox)
        self.flags = QTextDocument.FindFlag()
        # Connect the stateChanged signal of the checkbox to the update_flags slot
        self.case_sensitive_checkbox.stateChanged.connect(self.update_flags)
        self.hide()
        self.line_edit.returnPressed.connect(self.find_next)
        self.next_button.clicked.connect(self.find_next)
        self.next_button.setShortcut(Qt.Key_Return)
        self.prev_button.clicked.connect(self.find_prev)
        self.prev_button.setShortcut(Qt.AltModifier + Qt.Key_Return)

        self.installEventFilter(self)
    
    def update_flags(self):
        # Update the flags based on the state of the "case sensitive" checkbox
        if self.case_sensitive_checkbox.isChecked():
            self.flags = QTextDocument.FindCaseSensitively
        else:
            self.flags = QTextDocument.FindFlag()

    def eventFilter(self, obj, event):
        if event.type() == QEvent.FocusOut:
            self.hide()
        return super().eventFilter(obj, event)

    def find_next(self):
        text_edit = self.parent()
        query = self.line_edit.text()
        cursor = text_edit.textCursor()
        cursor = text_edit.document().find(query, cursor, self.flags)
        if not cursor.isNull():
            text_edit.setTextCursor(cursor)
    
    def find_prev(self):
        text_edit = self.parent()
        query = self.line_edit.text()
        flags = QTextDocument.FindBackward | self.flags
        cursor = text_edit.textCursor()
        cursor = text_edit.document().find(query, cursor, flags)
        if not cursor.isNull():
            text_edit.setTextCursor(cursor)