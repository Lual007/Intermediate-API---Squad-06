from sqlalchemy.orm import Session
from sqlalchemy import func
from .. import models
import datetime

# salvar analise 
def save_analise(db: Session, analise: models.AnaliseSentimento):
    
    db.add(analise)
    db.commit()
    db.refresh(analise)

# Pegar sentimentos
def get_sentimentos(db: Session):
    """
    Recupera todos os sentimentos.

    Args:
        db (Session): A sessão do banco de dados SQLAlchemy.

    Returns:
        list[models.AnaliseSentimento]: Uma lista de todos os registros de AnaliseSentimento.
    """
    return db.query(models.AnaliseSentimento).all()

# sentimentos recorrentes
def sentimentos_recorrentes(db: Session):
    """
    Recupera todos os sentimentos.

    Args:
        db (Session): A sessão do banco de dados SQLAlchemy.

    Returns:
        list[models.AnaliseSentimento]: Uma lista de todos os registros de AnaliseSentimento.
    """
    return db.query(
        models.AnaliseSentimento.sentimento,
        func.count(models.AnaliseSentimento).label("count")
    ).group_by(models.AnaliseSentimento.sentimento).order_by(-func.count(models.AnaliseSentimento.sentimento)).all()

# Sentimentos do técnico por id
def get_sentimentos_por_id(id: int, db: Session):
    """
    Recupera os sentimentos associados a um técnico específico.

    Args:
        db (Session): A sessão do banco de dados SQLAlchemy.
        tecnico_id (int): O ID do técnico.

    Returns:
        list[models.AnaliseSentimento]: Uma lista de registros de AnaliseSentimento associados ao técnico.
    """
    return db.query(models.AnaliseSentimento).join(models.Acao).filter(models.Acao.agent_id == id).all()

# returnar uma lista de atendimentos incluindo informações como conversa o sentimento.

def get_atendimento(db: Session):
    """
    Recupera informações de atendimento incluindo conversas, sentimentos, atendentes, etc.

    Args:
        db (Session): A sessão do banco de dados SQLAlchemy.

    Returns:
        list[tuple]: Uma lista de tuplas contendo informações de atendimento.
    """
    return  db.query(
        models.Event.descricao.label("conversa"),
        models.AnaliseSentimento.score,
        models.AnaliseSentimento.sentimento.label("termo"),
        models.AnaliseSentimento.sentimento.label("sentimento_mais"),
        models.Agent.nome.label("atendente"),
        models.AnaliseSentimento.sentimento.label("sentimento_atendente")
    ).join(models.Acao, models.Acao.event_id == models.Event.event_id)\
     .join(models.AnaliseSentimento, models.AnaliseSentimento.acao_id == models.Acao.acao_id)\
     .join(models.Agent, models.Acao.agent_id == models.Agent.agent_id).all()

# Buscar técnico por id

def get_tecnico(id: int, db: Session):
    """
    Recupera informações de um técnico específico.

    Args:
        db (Session): A sessão do banco de dados SQLAlchemy.
        tecnico_id (int): O ID do técnico.

    Returns:
        models.Agent | None: As informações do técnico ou None se não encontrado.
    """
    return db.query(
        models.Agent.nome.label("atendente"),
        models.AnaliseSentimento.sentimento.label("sentimento"),
        models.AnaliseSentimento.sentimento.label("sentimento_clientes"),
        models.AnaliseSentimento.sentimento.label("termo"),
        models.AnaliseSentimento.score
    ).join(models.Acao, models.Acao.agent_id == models.Agent.agent_id)\
     .join(models.AnaliseSentimento, models.AnaliseSentimento.acao_id == models.Acao.acao_id)\
     .filter(models.Agent.agent_id == id).first()


# Buscar cliente por id 

def get_cliente(id: int, db: Session):
    """
    Recupera informações de um cliente específico.

    Args:
        db (Session): A sessão do banco de dados SQLAlchemy.
        cliente_id (int): O ID do cliente.

    Returns:
        models.User | None: As informações do cliente ou None se não encontrado.
    """
    return db.query(
        models.User.name.label("cliente"),
        models.AnaliseSentimento.sentimento,
        models.AnaliseSentimento.sentimento.label("termo"),
        models.AnaliseSentimento.score
    ).join(models.Acao, models.Acao.user_id == models.User.user_id)\
     .join(models.AnaliseSentimento, models.AnaliseSentimento.acao_id == models.Acao.acao_id)\
     .filter(models.User.user_id == id).first()