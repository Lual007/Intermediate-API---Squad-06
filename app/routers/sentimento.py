from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
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
async def create_sentimento(acao: schemas.AcaoBase, db: Session = Depends(get_db)):
    """
    Requisita o modelo para analisar o sentimento
    """
    try:
       services_sentimentos.enviar_menssagem(acao,db)
    except Exception as e:
        print(f"Erro ao processar a requisição: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")
    
    return JSONResponse(status_code=201, content={
        "message": "Descrições enviadas com sucesso para análise de sentimento."
    })


# POST /sentimento/recebido
@router.post("/sentimento/recebido")
async def receber_sentimento(dados: dict, db: Session = Depends(get_db)):
    """
    Recebe os dados enviados pelo consumer e salva no banco de dados.
    """
    try:
        texto = dados.get("texto")
        resultado = dados.get("resultado")
        print(dados)

        if not texto or not resultado:
            raise HTTPException(status_code=400, detail="Texto e resultado são obrigatórios.")

    
        return JSONResponse(status_code=201, content={
            "message": "Sentimento recebido"
        })

    except Exception as e:
        print(f"Erro ao processar a requisição: {repr(e)}")
        raise HTTPException(status_code=500, detail=f"Erro inesperado: {str(e)}")
    
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
    Recupera as informações de atendimento incluindo conversas, sentimentos, atendenctes e clientes.
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
