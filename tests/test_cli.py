import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from cli.main import cli_main, TEMP_DIR, setup_temp_dir, cleanup_temp_dir

class TestCliFileUpload(unittest.TestCase):

    def setUp(self):
        setup_temp_dir()
        self.test_files_dir = "./test_files"
        os.makedirs(self.test_files_dir, exist_ok=True)

        # Create dummy valid files
        with open(os.path.join(self.test_files_dir, "test.xlsx"), "wb") as f:
            f.write(os.urandom(1 * 1024 * 1024)) # 1 MB
        with open(os.path.join(self.test_files_dir, "test.csv"), "wb") as f:
            f.write(os.urandom(1 * 1024 * 1024)) # 1 MB
        with open(os.path.join(self.test_files_dir, "test.tsv"), "wb") as f:
            f.write(os.urandom(1 * 1024 * 1024)) # 1 MB

        # Create dummy invalid file (too large)
        with open(os.path.join(self.test_files_dir, "large.xlsx"), "wb") as f:
            f.write(os.urandom(15 * 1024 * 1024)) # 15 MB

        # Create dummy invalid file (wrong type)
        with open(os.path.join(self.test_files_dir, "image.jpg"), "wb") as f:
            f.write(os.urandom(1 * 1024 * 1024)) # 1 MB

    def tearDown(self):
        cleanup_temp_dir()
        if os.path.exists(self.test_files_dir):
            import shutil
            shutil.rmtree(self.test_files_dir)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.stdout.write')
    @patch('sys.stderr.write')
    @patch('os.path.exists')
    @patch('shutil.copy')
    def test_cli_valid_xlsx_file(self, mock_shutil_copy, mock_os_path_exists, mock_stderr, mock_stdout, mock_args):
        test_file_path = os.path.join(self.test_files_dir, "test.xlsx")
        mock_os_path_exists.side_effect = lambda path: True if path == os.path.abspath(test_file_path) or path == os.path.join(TEMP_DIR, "test.xlsx") else False
        mock_args.return_value = type('Args', (object,), {'file_path': test_file_path, 'run': False})()
        
        cli_main()
        mock_shutil_copy.assert_called_once_with(os.path.abspath(test_file_path), os.path.join(TEMP_DIR, "test.xlsx"))
        self.assertTrue(os.path.exists(os.path.join(TEMP_DIR, "test.xlsx")))
        mock_stdout.assert_any_call(f"File '{test_file_path}' validated successfully and stored temporarily.\n")
        self.assertEqual(mock_stderr.call_count, 0) 

    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.stdout.write')
    @patch('sys.stderr.write')
    @patch('os.path.exists')
    @patch('shutil.copy')
    def test_cli_valid_csv_file(self, mock_shutil_copy, mock_os_path_exists, mock_stderr, mock_stdout, mock_args):
        test_file_path = os.path.join(self.test_files_dir, "test.csv")
        mock_os_path_exists.side_effect = lambda path: True if path == os.path.abspath(test_file_path) or path == os.path.join(TEMP_DIR, "test.csv") else False
        mock_args.return_value = type('Args', (object,), {'file_path': test_file_path, 'run': False})()
        cli_main()
        mock_shutil_copy.assert_called_once_with(os.path.abspath(test_file_path), os.path.join(TEMP_DIR, "test.csv"))
        self.assertTrue(os.path.exists(os.path.join(TEMP_DIR, "test.csv")))
        mock_stdout.assert_any_call(f"File '{test_file_path}' validated successfully and stored temporarily.\n")
        self.assertEqual(mock_stderr.call_count, 0)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.stdout.write')
    @patch('sys.stderr.write')
    @patch('os.path.exists')
    @patch('shutil.copy')
    def test_cli_valid_tsv_file(self, mock_shutil_copy, mock_os_path_exists, mock_stderr, mock_stdout, mock_args):
        test_file_path = os.path.join(self.test_files_dir, "test.tsv")
        mock_os_path_exists.side_effect = lambda path: True if path == os.path.abspath(test_file_path) or path == os.path.join(TEMP_DIR, "test.tsv") else False
        mock_args.return_value = type('Args', (object,), {'file_path': test_file_path, 'run': False})()
        cli_main()
        mock_shutil_copy.assert_called_once_with(os.path.abspath(test_file_path), os.path.join(TEMP_DIR, "test.tsv"))
        self.assertTrue(os.path.exists(os.path.join(TEMP_DIR, "test.tsv")))
        mock_stdout.assert_any_call(f"File '{test_file_path}' validated successfully and stored temporarily.\n")
        self.assertEqual(mock_stderr.call_count, 0)

    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.stdout.write')
    @patch('sys.stderr.write')
    @patch('os.path.exists')
    @patch('shutil.copy')
    def test_cli_file_not_found(self, mock_shutil_copy, mock_os_path_exists, mock_stderr, mock_stdout, mock_args):
        test_file_path = os.path.join(self.test_files_dir, "non_existent.xlsx")
        mock_os_path_exists.side_effect = lambda path: False # Ensure os.path.exists returns False for the source file
        mock_args.return_value = type('Args', (object,), {'file_path': test_file_path, 'run': False})()
        cli_main()
        mock_stderr.assert_any_call(f"Error: File not found at '{test_file_path}'\n")
        self.assertEqual(mock_stdout.call_count, 0)
        mock_shutil_copy.assert_not_called() 

    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.stdout.write')
    @patch('sys.stderr.write')
    @patch('os.path.exists')
    @patch('utils.file_validation.os.path.getsize') 
    @patch('shutil.copy')
    def test_cli_file_too_large(self, mock_shutil_copy, mock_getsize, mock_os_path_exists, mock_stderr, mock_stdout, mock_args):
        test_file_path = os.path.join(self.test_files_dir, "large.xlsx")
        mock_os_path_exists.return_value = True 
        mock_getsize.return_value = 15 * 1024 * 1024 
        mock_args.return_value = type('Args', (object,), {'file_path': test_file_path, 'run': False})()
        cli_main()
        mock_stderr.assert_any_call("Error: File size exceeds the 10MB limit.\n")
        self.assertEqual(mock_stdout.call_count, 0)
        mock_shutil_copy.assert_called_once()

    @patch('argparse.ArgumentParser.parse_args')
    @patch('sys.stdout.write')
    @patch('sys.stderr.write')
    @patch('os.path.exists')
    @patch('shutil.copy')
    def test_cli_invalid_file_type(self, mock_shutil_copy, mock_os_path_exists, mock_stderr, mock_stdout, mock_args):
        test_file_path = os.path.join(self.test_files_dir, "image.jpg")
        mock_os_path_exists.return_value = True 
        mock_args.return_value = type('Args', (object,), {'file_path': test_file_path, 'run': False})()
        cli_main()
        mock_stderr.assert_any_call("Error: Unsupported file type. Only .xlsx, .csv, and .tsv are allowed.\n")
        self.assertEqual(mock_stdout.call_count, 0)
        mock_shutil_copy.assert_called_once()

if __name__ == '__main__':
    unittest.main() 