from fastapi import FastAPI

from src.application.controller.simple_controller import SimpleController

app = FastAPI()

app.include_router(SimpleController.router)
