from fastapi import FastAPI
from app.routers import sentimento
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()
#
origins=[
    "http://localhost",
    "http://localhost:8080",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
]
app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins, 
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(sentimento.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI service 🚀"}


