# main.py
from fastapi import FastAPI
from app.routers import sentimento, auth # Importe o roteador de autenticação
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware

Base.metadata.create_all(bind=engine)

app = FastAPI()

origins=[
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:3000",
<<<<<<< HEAD
=======
    "http://localhost:3000",
>>>>>>> 5d0adcc059b8173e3f2491b7767df81d160be75a
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
app.include_router(sentimento.router)
app.include_router(auth.router) # Inclua o roteador de autenticação

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI service 🚀"}
