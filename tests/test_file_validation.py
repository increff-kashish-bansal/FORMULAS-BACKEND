import os
import unittest
from unittest.mock import patch

from utils.file_validation import InvalidFileTypeError, FileTooLargeError, validate_file_type, validate_file_size, validate_uploaded_file

class TestFileValidation(unittest.TestCase):

    def setUp(self):
        # Create a dummy file for testing size validation
        self.dummy_file_path = "test_dummy_file.txt"
        with open(self.dummy_file_path, "wb") as f:
            f.write(os.urandom(5 * 1024 * 1024)) # 5 MB

    def tearDown(self):
        # Clean up the dummy file
        if os.path.exists(self.dummy_file_path):
            os.remove(self.dummy_file_path)

    def test_validate_file_type_valid(self):
        self.assertIsNone(validate_file_type("test.xlsx"))
        self.assertIsNone(validate_file_type("document.csv"))
        self.assertIsNone(validate_file_type("data.tsv"))
        self.assertIsNone(validate_file_type("UPPERCASE.XLSX"))

    def test_validate_file_type_invalid(self):
        with self.assertRaises(InvalidFileTypeError):
            validate_file_type("image.jpg")
        with self.assertRaises(InvalidFileTypeError):
            validate_file_type("script.py")
        with self.assertRaises(InvalidFileTypeError):
            validate_file_type("archive.zip")
        with self.assertRaises(InvalidFileTypeError):
            validate_file_type("no_extension")

    @patch('os.path.getsize')
    def test_validate_file_size_within_limit(self, mock_getsize):
        mock_getsize.return_value = 5 * 1024 * 1024 # 5 MB
        self.assertIsNone(validate_file_size(self.dummy_file_path, max_size_mb=10))

    @patch('os.path.getsize')
    def test_validate_file_size_at_limit(self, mock_getsize):
        mock_getsize.return_value = 10 * 1024 * 1024 # 10 MB
        self.assertIsNone(validate_file_size(self.dummy_file_path, max_size_mb=10))

    @patch('os.path.getsize')
    def test_validate_file_size_exceeds_limit(self, mock_getsize):
        mock_getsize.return_value = 11 * 1024 * 1024 # 11 MB
        with self.assertRaises(FileTooLargeError):
            validate_file_size(self.dummy_file_path, max_size_mb=10)

    @patch('os.path.getsize')
    def test_validate_uploaded_file_valid(self, mock_getsize):
        mock_getsize.return_value = 5 * 1024 * 1024 # 5 MB
        self.assertIsNone(validate_uploaded_file("report.xlsx", self.dummy_file_path, max_size_mb=10))

    @patch('os.path.getsize')
    def test_validate_uploaded_file_invalid_type(self, mock_getsize):
        mock_getsize.return_value = 5 * 1024 * 1024 # 5 MB
        with self.assertRaises(InvalidFileTypeError):
            validate_uploaded_file("image.png", self.dummy_file_path, max_size_mb=10)

    @patch('os.path.getsize')
    def test_validate_uploaded_file_too_large(self, mock_getsize):
        mock_getsize.return_value = 15 * 1024 * 1024 # 15 MB
        with self.assertRaises(FileTooLargeError):
            validate_uploaded_file("data.csv", self.dummy_file_path, max_size_mb=10)

    @patch('os.path.getsize')
    def test_validate_uploaded_file_both_invalid(self, mock_getsize):
        # Type error should be raised first
        mock_getsize.return_value = 15 * 1024 * 1024 # 15 MB
        with self.assertRaises(InvalidFileTypeError):
            validate_uploaded_file("invalid.pdf", self.dummy_file_path, max_size_mb=10)

if __name__ == '__main__':
    unittest.main() 