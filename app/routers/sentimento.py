from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas
from ..database import get_db
from ..services import services_sentimentos

router = APIRouter(
    prefix="",
    tags=["sentimento"]
)

# POST /sentimento
@router.post("/sentimento/create")
def create_sentimento(acao: schemas.Acao, db: Session = Depends(get_db)):

    # realizar a requisição com a outra api para gerar a requisição com a coluna "sentimento" com valor
    new_sentimento = models.AnaliseSentimento(**acao.model_dump())


    db.add(new_sentimento)
    db.commit()
    db.refresh(new_sentimento)
    return new_sentimento

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
