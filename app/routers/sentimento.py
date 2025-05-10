from dotenv import load_dotenv
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy.exc import (
    SQLAlchemyError,
    OperationalError,
    IntegrityError,
    DataError,
    NoResultFound,
)
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
                print("erro ao conectar com o modelo")
                raise HTTPException(status_code=404, detail=f"erro ao conectar com o modelo")
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
        
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Erro ao conectar com o serviço de análise: {str(e)}"
        )
    
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Erro na API de análise de sentimento: {str(e)}"
        )
    
    except OperationalError as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao acessar o banco de dados: {e}"
        )

    except (IntegrityError, DataError) as e:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Erro de integridade dos dados ao salvar a análise"
        )

    except (SQLAlchemyError, Exception) as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro inesperado ao salvar a análise no banco: {e}"
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
    
    except OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao acessar o banco de dados: {e}"
        )
    
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail="Nenhum sentimento encontrado"
        )
    
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar sentimentos: {e}"
        )

# GET /sentimentosRecorrentes
@router.get("/sentimento/recorrente")
def sentimentos_recorrentes(db: Session = Depends(get_db)):
    """
    Recupera todos os sentimentos recorrentes.
    """
    try:
        return services_sentimentos.sentimentos_recorrentes(db)
    
    except OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao acessar o banco de dados: {e}"
        )
    
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail="Nenhum sentimento recorrente encontrado"
        )
    
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar sentimentos recorrentes: {e}"
        )

# GET /sentimento/tecnico/{id}
@router.get("/sentimento/tecnico/{id}")
def get_sentimento_by_tecnico(id: int, db: Session = Depends(get_db)):
    """
    Recupera todos os sentimentos de um técnico.
    """
    try:
        if not id or id <= 0:
            raise HTTPException(
                status_code=400,
                detail="ID do técnico inválido"
            )
            
        return services_sentimentos.get_sentimentos_por_id(id, db)
    
    except OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao acessar o banco de dados: {e}"
        )
    
    except NoResultFound:
        raise HTTPException(
            status_code=404,
            detail=f"Nenhum sentimento encontrado para o técnico {id}"
        )
    
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao buscar sentimentos do técnico: {e}"
        )

# GET /atendimento
@router.get("/atendimento")
def get_atendimento(db: Session = Depends(get_db)):
    """
    Recupera as informações de atendimento incluindo conversas, sentimentos, atendentes e clientes.
    """
    try: 
        
        return services_sentimentos.get_atendimento(db)
    
    except OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar o banco de dados: {e}")
    
    except NoResultFound:
        raise HTTPException(status_code=404, detail=f"Nenhum atendimento encontrado")
    
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer a busca dos atendimentos no banco: {e}")
    
    

# GET /tecnico/{id}
@router.get("/tecnico/{id}")
def get_tecnico(id: int, db: Session = Depends(get_db)):
    """
    Recupera informações de um técnico específico.
    """
    try: 
        if not id or id <= 0:
            raise HTTPException(
                status_code=400,
                detail="ID do técnico inválido"
            )
        return services_sentimentos.get_tecnico(id,db)
        
    except OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar o banco de dados: {e}")
    
    except NoResultFound:
        raise HTTPException(status_code=404, detail="O técnico não foi encontrado")
    
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer a busca do técnico no banco: {e}")
    
    

# GET /cliente/{id}
@router.get("/cliente/{id}")
def get_cliente(id: int, db: Session = Depends(get_db)):
    """
    Recupera informações de um cliente específico.
    """
    try:
        
        return services_sentimentos.get_cliente(id, db)
        
    except OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Erro ao acessar o banco de dados: {e}")
    
    except NoResultFound:
        raise HTTPException(status_code=404, detail="Nenhum sentimento encontrado")
    
    except (Exception, SQLAlchemyError) as e:
        raise HTTPException(status_code=500, detail=f"Erro ao fazer a busca dos sentimentos no banco: {e}")
    
    
