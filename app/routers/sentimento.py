from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas
from ..database import get_db
from ..services import services_sentimentos
import httpx
import datetime

router = APIRouter(
    prefix="",
    tags=["sentimento"]
)

# POST /sentimento
@router.post("/sentimento/create")
async def create_sentimento(acao: schemas.Acao, db: Session = Depends(get_db)):
    """
    Requisita o modelo para analisar o sentimento e salva o resultado no banco de dados
    """
    # TODO:Trocar a url para a da api do modelo
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8001",
                json={"texto": acao.descricao}
            )
        
        sentimento_data = response.json()
        new_sentimento = models.AnaliseSentimento(**acao.model_dump())
        
    except httpx.RequestError as e:
        raise HTTPException(status_code=503, detail=f"Erro ao conectar com o modelo: {str(e)}")
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=response.status_code, detail=f"Erro na API de analise de sentimento: {str(e)}")
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")
    

    new_sentimento.acao_id  = acao.acao_id
    new_sentimento.sentimento = sentimento_data.sentimento
    new_sentimento.score = sentimento_data.score
    new_sentimento.modelo = sentimento_data.modelo
    new_sentimento.data_analise = datetime.now()
    services_sentimentos.create_sentimento(db, new_sentimento)
    
    return JSONResponse(status_code=201, content={
        "message": "Sentimento criado"
    })

# GET /sentimento
@router.get("/sentimento/all")
def get_sentimentos(db: Session = Depends(get_db)):
    """
    Recupera todos os sentimentos.
    """
    return services_sentimentos.get_sentimentos(db)

# GET /sentimentosRecorrentes
@router.get("/sentimento/recorrente")
def sentimentos_recorrentes(db: Session = Depends(get_db)):
    """
    Recupera todos os sentimentos recorrentes.
    """
    return services_sentimentos.sentimentos_recorrentes(db)

# GET /sentimento/tecnico/{id}
@router.get("/sentimento/tecnico/{id}")
def get_sentimento_by_tecnico(id: int, db: Session = Depends(get_db)):
    """
    Recupera todos os sentimentos de um técnico.
    """
    return services_sentimentos.get_sentimentos_por_id(id,db)

# GET /atendimento
@router.get("/atendimento")
def get_atendimento(db: Session = Depends(get_db)):
    """
    Recupera as informações de atendimento incluindo conversas, sentimentos, atendentes e clientes.
    """
    return services_sentimentos.get_atendimento(db)

# GET /tecnico/{id}
@router.get("/tecnico/{id}")
def get_tecnico(id: int, db: Session = Depends(get_db)):
    """
    Recupera informações de um técnico específico.
    """
    tecnico = services_sentimentos.get_tecnico(id,db)
    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico não encontrado") 
    return tecnico

# GET /cliente/{id}
@router.get("/cliente/{id}")
def get_cliente(id: int, db: Session = Depends(get_db)):
    """
    Recupera informações de um cliente específico.
    """
    cliente = services_sentimentos.get_cliente(id, db)
    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return cliente
