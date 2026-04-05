import uvicorn
from fastapi import FastAPI

from src.db.models import init_db
from src.api.chat import router as chat_router
from src.config import API_HOST, API_PORT

app = FastAPI(title="Emira AI Assistant")

app.include_router(chat_router)


@app.on_event("startup")
async def startup():
    await init_db()
    print("Emira запущена!")


if __name__ == "__main__":
    uvicorn.run("src.main:app", host=API_HOST, port=API_PORT, reload=True)
