import uvicorn
from fastapi import FastAPI
from loguru import logger
from starlette.responses import RedirectResponse

from applications import router


def add_router(main_app: FastAPI):
    main_app.include_router(router)


def create_app():
    main_app = FastAPI()

    @main_app.get("/")
    async def root():
        return RedirectResponse(url="/docs")

    add_router(main_app)
    return main_app


app = create_app()


if __name__ == "__main__":
    logger.info("FastAPI is running")
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
