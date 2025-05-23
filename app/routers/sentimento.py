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
        acao_id = dados.get("acao_id")
        event_id = dados.get("event_id")
        resultado = dados.get("resultado")
        modelo = dados.get("modelo")
        enviar = {
            "acao_id": acao_id,
            "event_id": event_id,
            "sentimento": resultado,
            "modelo": modelo
        }
        services_sentimentos.salvar_analise(db,enviar)
        
        if not resultado or not resultado:
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
    Recupera as informações de atendimento incluindo conversas, sentimentos, atendenctes e clientes.
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
    
# GET /tecnicos
@router.get("/tecnicos-lista")
def get_tecnicos(db: Session = Depends(get_db)):
    try:
        return services_sentimentos.get_tecnicos(db)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao buscar técnicos: {str(e)}")

# GET /clientes
@router.get("/clientes-lista")
def get_clientes(db: Session = Depends(get_db)):
    return services_sentimentos.get_clientes(db)

# GET /sentimento/by-score
@router.get("/sentimento/by-score")
def get_sentimentos_by_score(min: float = 0.0, max: float = 1.0, db: Session = Depends(get_db)):
    return services_sentimentos.get_sentimentos_by_score(min, max, db)

# GET /sentimento/by-data
@router.get("/sentimento/by-data")
def get_sentimentos_by_data(start: datetime.date, end: datetime.date, db: Session = Depends(get_db)):
    return services_sentimentos.get_sentimentos_by_data(start, end, db)

# Sentimento mais negativo
@router.get("/sentimento/mais-negativo")
def get_mais_negativo(db: Session = Depends(get_db)):
    sentimento_negativo = services_sentimentos.get_sentimento_mais_negativo(db)

    return sentimento_negativo

# GET /sentimento/quantidade
@router.get("/sentimento/quantidade")
def get_quantidade_sentimentos(db: Session = Depends(get_db)):
    print("Chamando a função get_quantidade_sentimentos")
    quantidade = services_sentimentos.get_quantidade_sentimentos(db)
    print(f"Quantidade de sentimentos: {quantidade}")
    return {"quantidade": quantidade}


# Get/ sentimento/mais-frequente
@router.get("/sentimento/mais-frequente")
def get_sentimento_mais_frequente(db: Session = Depends(get_db)):
    return services_sentimentos.get_sentimento_mais_frequente(db)