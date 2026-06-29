import os
import shutil
import uuid
from fastapi import UploadFile


def save_uploaded_file(file: UploadFile, folder: str):

    os.makedirs(folder, exist_ok=True)

    extension = os.path.splitext(file.filename)[1]

    filename = f"{uuid.uuid4()}{extension}"

    file_path = os.path.join(folder, filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path