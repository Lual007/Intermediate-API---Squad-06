from fastapi import FastAPI, HTTPException
from app.routers import sentimento, auth
from app.database import Base, engine
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address) 

app = FastAPI(lifespan=[limiter.init_app])
app.state.limiter = limiter
app.add_exception_handler(HTTPException, _rate_limit_exceeded_handler)
app.add_middleware(SlowAPIMiddleware)

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
app.include_router(auth.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI service 🚀"}