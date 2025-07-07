from fastapi.testclient import TestClient
import os
import shutil

from api.main import app, TEMP_DIR
from utils.file_validation import InvalidFileTypeError, FileTooLargeError

class TestApiFileUpload:

    def setup_method(self):
        os.makedirs(TEMP_DIR, exist_ok=True)
        self.client = TestClient(app)
        self.test_files_dir = "./test_api_files"
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

    def teardown_method(self):
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        if os.path.exists(self.test_files_dir):
            shutil.rmtree(self.test_files_dir)

    def test_upload_valid_xlsx_file(self):
        file_path = os.path.join(self.test_files_dir, "test.xlsx")
        with open(file_path, "rb") as f:
            response = self.client.post(
                "/uploadfile/", files={"file": ("test.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        assert response.status_code == 200
        assert response.json()["message"] == "File uploaded and validated successfully"
        assert response.json()["filename"] == "test.xlsx"
        # Verify that the temporary file was created and then removed by the API endpoint's finally block
        assert not os.path.exists(response.json()["temp_path"])

    def test_upload_valid_csv_file(self):
        file_path = os.path.join(self.test_files_dir, "test.csv")
        with open(file_path, "rb") as f:
            response = self.client.post(
                "/uploadfile/", files={"file": ("test.csv", f, "text/csv")}
            )
        assert response.status_code == 200
        assert response.json()["message"] == "File uploaded and validated successfully"
        assert response.json()["filename"] == "test.csv"
        assert not os.path.exists(response.json()["temp_path"])

    def test_upload_valid_tsv_file(self):
        file_path = os.path.join(self.test_files_dir, "test.tsv")
        with open(file_path, "rb") as f:
            response = self.client.post(
                "/uploadfile/", files={"file": ("test.tsv", f, "text/tsv")}
            )
        assert response.status_code == 200
        assert response.json()["message"] == "File uploaded and validated successfully"
        assert response.json()["filename"] == "test.tsv"
        assert not os.path.exists(response.json()["temp_path"])

    def test_upload_file_too_large(self):
        file_path = os.path.join(self.test_files_dir, "large.xlsx")
        with open(file_path, "rb") as f:
            response = self.client.post(
                "/uploadfile/", files={"file": ("large.xlsx", f, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
            )
        assert response.status_code == 400
        assert response.json()["detail"] == FileTooLargeError().message

    def test_upload_invalid_file_type(self):
        file_path = os.path.join(self.test_files_dir, "image.jpg")
        with open(file_path, "rb") as f:
            response = self.client.post(
                "/uploadfile/", files={"file": ("image.jpg", f, "image/jpeg")}
            )
        assert response.status_code == 400
        assert response.json()["detail"] == InvalidFileTypeError().message

    def test_upload_no_filename(self):
        # For FastAPI UploadFile, if filename is None, it implies a malformed request
        # FastAPI might handle this before our explicit check, but we test the HTTPException path
        # We simulate this by directly constructing the file dictionary without a filename
        response = self.client.post(
            "/uploadfile/", files={
                "file": (None, b"dummy content", "application/octet-stream")
            }
        )
        assert response.status_code == 422
        # FastAPI's default response for missing filename in multipart is a 422 with validation error details
        assert "detail" in response.json()
        assert len(response.json()["detail"]) > 0
        assert "loc" in response.json()["detail"][0] and "file" in response.json()["detail"][0]["loc"]
        assert "msg" in response.json()["detail"][0] and "Value error, Expected UploadFile, received: <class 'str'>" in response.json()["detail"][0]["msg"] 