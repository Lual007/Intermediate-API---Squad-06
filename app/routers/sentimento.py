from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware
from .auth import obter_usuario_atual
from .. import models, schemas
from ..database import get_db
from ..services import services_sentimentos
import httpx
import datetime

router = APIRouter(
    prefix="",
    tags=["sentimento"]
)

# Configuração do rate limiter
limiter = Limiter(key_func=lambda request: request.state.user.user_id if hasattr(request.state, "user") else get_remote_address)

# POST /sentimento
@router.post("/sentimento/create", dependencies=[Depends(obter_usuario_atual), Depends(limiter.limit("20/minute"))])
async def create_sentimento(acao: schemas.Acao, db: Session = Depends(get_db)):
    """
    Requisita o modelo para analisar o sentimento
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001/analisar",
                json={"text": acao.descricao},
                timeout=120.0
            )
        sentimento_data = response.json()
        sentimento_dict = {
            "acao_id": acao.acao_id,
            "sentimento": sentimento_data.get("sentiment"),
            "score": 1.0,
            "modelo": "Emollama-7b",
            "data_analise": datetime.datetime.now(),
        }
        new_sentimento = models.AnaliseSentimento(**sentimento_dict)

    except httpx.RequestError as e:
        print("Erro ao conectar com o modelo:", repr(e))
        raise HTTPException(status_code=503, detail=f"Erro ao conectar com o modelo: {repr(e)}")

    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=response.status_code, detail=f"Erro na API de analise de sentimento: {str(e)}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")

    services_sentimentos.save_analise(db, new_sentimento)

    return JSONResponse(status_code=201, content={
        "message": "Sentimento criado"
    })

# GET /sentimento
@router.get("/sentimento/all", dependencies=[Depends(obter_usuario_atual), Depends(limiter.limit("60/minute"))])
def get_sentimentos(db: Session = Depends(get_db)):
    """
    Recupera todos os sentimentos.
    """
    return services_sentimentos.get_sentimentos(db)

# GET /sentimentosRecorrentes
@router.get("/sentimento/recorrente", dependencies=[Depends(obter_usuario_atual), Depends(limiter.limit("60/minute"))])
def sentimentos_recorrentes(db: Session = Depends(get_db)):
    """
    Recupera todos os sentimentos recorrentes.
    """
    return services_sentimentos.sentimentos_recorrentes(db)

# GET /sentimento/tecnico/{id}
@router.get("/sentimento/tecnico/{id}", dependencies=[Depends(obter_usuario_atual), Depends(limiter.limit("30/minute"))])
def get_sentimento_by_tecnico(id: int, db: Session = Depends(get_db)):
    """
    Recupera todos os sentimentos de um técnico.
    """
    return services_sentimentos.get_sentimentos_por_id(id, db)

# GET /atendimento
@router.get("/atendimento", dependencies=[Depends(obter_usuario_atual), Depends(limiter.limit("30/minute"))])
def get_atendimento(db: Session = Depends(get_db)):
    """
    Recupera as informações de atendimento incluindo conversas, sentimentos, atendentes e clientes.
    """
    return services_sentimentos.get_atendimento(db)

# GET /tecnico/{id}
@router.get("/tecnico/{id}", dependencies=[Depends(obter_usuario_atual), Depends(limiter.limit("30/minute"))])
def get_tecnico(id: int, db: Session = Depends(get_db)):
    """
    Recupera informações de um técnico específico.
    """
    tecnico = services_sentimentos.get_tecnico(id, db)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico não encontrado")
    return tecnico

# GET /cliente/{id}
@router.get("/cliente/{id}", dependencies=[Depends(obter_usuario_atual), Depends(limiter.limit("30/minute"))])
def get_cliente(id: int, db: Session = Depends(get_db)):
    """
    Recupera informações de um cliente específico.
    """
    cliente = services_sentimentos.get_cliente(id, db)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente