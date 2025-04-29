from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models, schemas, database

router = APIRouter(
    prefix="",
    tags=["sentimento"]
)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

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
    sentimentos = db.query(models.AnaliseSentimento).all()
    return sentimentos

# GET /sentimentosRecorrentes
@router.get("/sentimento/recorrente")
def sentimentos_recorrentes(db: Session = Depends(get_db)):
    result = db.query(
        models.AnaliseSentimento.sentimento,
        func.count(models.AnaliseSentimento.sentimento).label("count")
    ).group_by(models.AnaliseSentimento.sentimento).order_by(-func.count(models.AnaliseSentimento.sentimento)).all()
    return result

# GET /sentimento/tecnico/{id}
@router.get("/sentimento/tecnico/{id}")
def get_sentimento_by_tecnico(id: int, db: Session = Depends(get_db)):
    sentimentos = db.query(models.AnaliseSentimento).join(models.Acao)\
        .filter(models.Acao.agent_id == id).all()
    return sentimentos

# DELETE /sentimento/{id}
@router.delete("/sentimento/{id}")
def delete_sentimento(id: int, db: Session = Depends(get_db)):
    sentimento = db.query(models.AnaliseSentimento).filter(models.AnaliseSentimento.analise_id == id).first()
    if not sentimento:
        raise HTTPException(status_code=404, detail="Sentimento não encontrado")
    db.delete(sentimento)
    db.commit()
    return {"ok": True}

# GET /atendimento
@router.get("/atendimento")
def get_atendimento(db: Session = Depends(get_db)):
    # Mockup join query - we would JOIN eventos, ações, analises, agentes, clientes
    atendimentos = db.query(
        models.Event.descricao.label("conversa"),
        models.AnaliseSentimento.score,
        models.AnaliseSentimento.sentimento.label("termo"),
        models.AnaliseSentimento.sentimento.label("sentimento_mais"),
        models.Agent.nome.label("atendente"),
        models.AnaliseSentimento.sentimento.label("sentimento_atendente")
    ).join(models.Acao, models.Acao.event_id == models.Event.event_id)\
     .join(models.AnaliseSentimento, models.AnaliseSentimento.acao_id == models.Acao.acao_id)\
     .join(models.Agent, models.Acao.agent_id == models.Agent.agent_id).all()

    return atendimentos

# GET /tecnico/{id}
@router.get("/tecnico/{id}")
def get_tecnico(id: int, db: Session = Depends(get_db)):
    tecnico = db.query(
        models.Agent.nome.label("atendente"),
        models.AnaliseSentimento.sentimento.label("sentimento"),
        models.AnaliseSentimento.sentimento.label("sentimento_clientes"),
        models.AnaliseSentimento.sentimento.label("termo"),
        models.AnaliseSentimento.score
    ).join(models.Acao, models.Acao.agent_id == models.Agent.agent_id)\
     .join(models.AnaliseSentimento, models.AnaliseSentimento.acao_id == models.Acao.acao_id)\
     .filter(models.Agent.agent_id == id).first()

    if not tecnico:
        raise HTTPException(status_code=404, detail="Técnico não encontrado")
    
    return tecnico

# GET /cliente/{id}
@router.get("/cliente/{id}")
def get_cliente(id: int, db: Session = Depends(get_db)):
    cliente = db.query(
        models.User.name.label("cliente"),
        models.AnaliseSentimento.sentimento,
        models.AnaliseSentimento.sentimento.label("termo"),
        models.AnaliseSentimento.score
    ).join(models.Acao, models.Acao.user_id == models.User.user_id)\
     .join(models.AnaliseSentimento, models.AnaliseSentimento.acao_id == models.Acao.acao_id)\
     .filter(models.User.user_id == id).first()

    if not cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    
    return cliente
