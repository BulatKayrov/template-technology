import uvicorn
from fastapi import FastAPI
from starlette.responses import RedirectResponse

from applications import router

app = FastAPI()
app.include_router(router)


@app.get("/")
async def root():
    return RedirectResponse(url="/docs")


if __name__ == "__main__":
    uvicorn.run(app="main:app", host="0.0.0.0", port=8000, reload=True)
