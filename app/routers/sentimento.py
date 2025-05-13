from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..services import services_sentimentos
import httpx
import datetime
from os import getenv

load_dotenv()

ANALISE_URL = getenv("ANALISE_URL")

router = APIRouter(
    prefix="",
    tags=["sentimento"]
)

# POST /sentimento
@router.post("/sentimento/create")
async def create_sentimento(acao: schemas.Acao, db: Session = Depends(get_db)):
    """
    Requisita o modelo para analisar o sentimento
    """
    acao_db = db.query(models.Acao).filter(models.Acao.acao_id == acao.acao_id).first()

    if not acao_db:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Ação não encontrada"
                )
    if not acao.descricao:
        raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ação não possui descrição"
                )
    try:
        async with httpx.AsyncClient() as client:
            if ANALISE_URL == None:
                print("Erro ao conectar com o modelo")
                raise HTTPException(
                        status_code=404, 
                        detail=f"Erro ao conectar com o modelo"
                        )
            response = await client.post(
                ANALISE_URL,
                json={"text": acao.descricao},
                timeout=120.0
            )
        sentimento_data = response.json()
        if not sentimento_data.get("sentiment"):
            raise HTTPException(
                status_code=502,
                detail="Resposta inválida do serviço de análise"
                )

        sentimento_dict = {
            "acao_id": acao.acao_id,
            "sentimento": sentimento_data.get("sentiment"),
            "score": 1.0,
            "modelo": "Emollama-7b",
            "data_analise": datetime.datetime.now(),
            "acao": acao
        }    

        new_sentimento = models.AnaliseSentimento(**sentimento_dict)
        services_sentimentos.save_analise(db, new_sentimento)
        
    except httpx.RequestError:
        raise HTTPException(
                status_code=503,
                detail="Erro ao conectar com o serviço de análise:"
                )
    
    except httpx.HTTPStatusError:
        raise HTTPException(
                status_code=response.status_code,
                detail="Erro na API de análise de sentimento"
                )


    except Exception as e:
        raise HTTPException(
                status_code=500,
                detail=str(e)
                )
    
    return JSONResponse(
        status_code=201,
        content={
            "message": "Sentimento criado",
            "sentimento": sentimento_data.get("sentiment")
        }
    )

# GET /sentimento
@router.get("/sentimento/all")
def get_sentimentos(db: Session = Depends(get_db)):
    """
    Recupera todos os sentimentos.
    """
    try:
        return services_sentimentos.get_sentimentos(db)
        
    except Exception as e:
        raise HTTPException(
                status_code=500,
                detail=str(e)
                )

# GET /sentimentosRecorrentes
@router.get("/sentimento/recorrente")
def sentimentos_recorrentes(db: Session = Depends(get_db)):
    """
    Recupera todos os sentimentos recorrentes.
    """
    try:
        return services_sentimentos.sentimentos_recorrentes(db)
    
    except Exception as e:
        raise HTTPException(
                status_code=500,
                detail=str(e)
                )

# GET /sentimento/tecnico/{id}
@router.get("/sentimento/tecnico/{id}")
def get_sentimento_by_tecnico(id: int, db: Session = Depends(get_db)):
    """
    Recupera todos os sentimentos de um técnico.
    """
    try:    
        return services_sentimentos.get_sentimentos_por_id(id, db)
       
    
    except Exception as e:
        raise HTTPException(
                status_code=500,
                detail=str(e)
                )

# GET /atendimento
@router.get("/atendimento")
def get_atendimento(db: Session = Depends(get_db)):
    """
    Recupera as informações de atendimento incluindo conversas, sentimentos, atendentes e clientes.
    """
    try: 
        
        return services_sentimentos.get_atendimento(db)
    
    except Exception as e:
        raise HTTPException(
                status_code=500, 
                detail=str(e)
                )
    
    

# GET /tecnico/{id}
@router.get("/tecnico/{id}")
def get_tecnico(id: int, db: Session = Depends(get_db)):
    """
    Recupera informações de um técnico específico.
    """
    try:    
            
        return services_sentimentos.get_tecnico(id, db)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
    

# GET /cliente/{id}
@router.get("/cliente/{id}")
def get_cliente(id: int, db: Session = Depends(get_db)):
    """
    Recupera informações de um cliente específico.
    """
    try:    
        return services_sentimentos.get_cliente(id, db)
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
    
    
