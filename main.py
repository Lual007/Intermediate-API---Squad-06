from fastapi import FastAPI
from app.routers import sentimento
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(sentimento.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI service 🚀"}


