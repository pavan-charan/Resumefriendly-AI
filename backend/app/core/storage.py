import os
import uuid
import shutil
from fastapi import UploadFile
from app.core.config import settings

class LocalStorageManager:
    def __init__(self, upload_dir: str = settings.UPLOAD_DIR):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)

    def save_file(self, file: UploadFile) -> str:
        """
        Saves uploaded file to local filesystem.
        Returns the absolute or relative path to the saved file.
        """
        # Generate unique filename to avoid collision
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        target_path = os.path.join(self.upload_dir, unique_filename)
        
        with open(target_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        return target_path

    def delete_file(self, file_path: str) -> bool:
        """
        Removes file from filesystem.
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception:
            return False

# Export instantiated manager
storage_manager = LocalStorageManager()
