from fastapi import APIRouter, UploadFile

from application.handlers.upload_handler import UploadHandler


class SimpleController:
    router = APIRouter()

    name = "storage"

    @staticmethod
    @router.get(path=f"/{name}/", tags=[name])
    async def default_controller():
        return {"msg": "Hello API"}

    @staticmethod
    @router.post(path=f"/{name}/upload-file", tags=[name])
    async def upload_file(file: UploadFile):
        await UploadHandler.upload_file_handle(file)
        return {"name": file.filename}
