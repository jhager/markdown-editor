import os
import unittest
from unittest.mock import patch
from PyQt5.QtWidgets import QApplication
from markdown_editor import MarkdownEditor
import PyPDF2

TEST_SAVE_FILE = './test/test_save_file.md'
TEST_OPEN_FILE = './test/test_open_file.md'
TEST_EXPORT_FILE = './test/test_export_file.pdf'
TEST_EXPORT_COMPARE_FILE = './test/test_export_compare_file.pdf'
TEST_SAVE_CONTENTS = 'Hello, world!'
TEST_OPEN_CONTENTS = 'Hello, world!'
TEST_EXPORT_CONTENTS = 'Hello, world!'

def compare_pdfs(file1, file2):
    # Open the two PDF files in binary mode
    with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
        # Create two PyPDF2 PdfFileReader objects
        pdf1 = PyPDF2.PdfFileReader(f1)
        pdf2 = PyPDF2.PdfFileReader(f2)

        # Compare the number of pages in each PDF
        if pdf1.getNumPages() != pdf2.getNumPages():
            return False

        # Compare the content of each page in the two PDFs
        for i in range(pdf1.getNumPages()):
            page1 = pdf1.getPage(i)
            page2 = pdf2.getPage(i)
            if page1.extractText() != page2.extractText():
                return False

    # If we made it this far, the two PDFs are identical
    return True

class TestMarkdownEditor(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Write a test file for the open file test
        os.makedirs('./temp', exist_ok=True)
        with open(TEST_OPEN_FILE, 'w') as f:
            f.write(TEST_OPEN_CONTENTS)

        # Create a QApplication instance once for all test cases
        cls.app = QApplication([])

        # Create a shared MarkdownEditor instance
        cls.editor = MarkdownEditor()

    @classmethod
    def tearDownClass(cls):
        # Clean up the QApplication instance after all test cases
        cls.app.quit()
        cls.editor.page.deleteLater()

    def test_save(self):
        # Set the current file to a temporary file path
        self.editor.current_file = TEST_SAVE_FILE

        # Set some text in the source text edit
        self.editor.source_text_edit.setPlainText(TEST_SAVE_CONTENTS)

        # Call the save method
        self.editor.save()

        # Open the file using vanilla Python to ensure it was saved correctly
        with open(TEST_SAVE_FILE, 'r') as f:
            self.assertEqual(f.read(), TEST_SAVE_CONTENTS)

    def test_open_file(self):
        # Mock the QFileDialog.getOpenFileName method to return a file path
        with patch('markdown_editor.QFileDialog.getOpenFileName') as mock_getOpenFileName:
            mock_getOpenFileName.return_value = (TEST_OPEN_FILE, '')

            # Call the open_file method
            self.editor.open_file()

        # TODO: Add assertions to check if the file was opened correctly
        self.assertEqual(self.editor.source_text_edit.toPlainText(), TEST_OPEN_CONTENTS)

    def test_export_pdf(self):
        # Mock the QFileDialog.getSaveFileName method to return a file path
        with patch('markdown_editor.QFileDialog.getSaveFileName') as mock_getSaveFileName:
            mock_getSaveFileName.return_value = (TEST_EXPORT_FILE, '')

            # Call the export_pdf method
            self.editor.export_pdf()

        # TODO: Add assertions to check if the PDF was exported correctly
        # NOTE: Original thinking was to create a variable `TEST_EXPORT_CONTENTS`
        #       and compare the contents of the PDF to that variable. 
        #       However, the PDF is binary and not human-readable, so this is not a good way.
        # Open the PDF and check if the contents are correct
        # with open(TEST_EXPORT_FILE, 'r') as f:
        #     self.assertEqual(f.read(), TEST_EXPORT_CONTENTS)
        self.assertTrue(compare_pdfs(TEST_EXPORT_FILE, TEST_EXPORT_COMPARE_FILE))


if __name__ == '__main__':
    unittest.main()
