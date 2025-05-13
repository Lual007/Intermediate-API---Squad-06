from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError, NoResultFound
from app.schemas import Agent, Atendimento, SentimentoRecorrente, User
from .. import models

# salvar analise 
def save_analise(db: Session, analise: models.AnaliseSentimento):
    try:
        
        db.add(analise)
        db.commit()
        db.refresh(analise)
    
    except Exception as e:
        db.rollback()
        raise Exception("Erro ao salvar a análise")

# Pegar sentimentos
def get_sentimentos(db: Session):
    """
    Recupera todos os sentimentos.

    Args:
        db (Session): A sessão do banco de dados SQLAlchemy.

    Returns:
        list[models.AnaliseSentimento]: Uma lista de todos os registros de AnaliseSentimento.
    """
    try: 
        return db.query(models.AnaliseSentimento).all()
    
    except NoResultFound:
        raise Exception("Nenhum sentimento encontrado")
    
    except SQLAlchemyError:
        raise Exception("Erro ao buscar os sentimentos")

# sentimentos recorrentes
def sentimentos_recorrentes(db: Session):
    """
    Recupera todos os sentimentos.

    Args:
        db (Session): A sessão do banco de dados SQLAlchemy.

    Returns:
        list[models.AnaliseSentimento]: Uma lista de todos os registros de AnaliseSentimento.
    """
    try: 
        results = db.query(
                models.AnaliseSentimento.sentimento,
                func.count(models.AnaliseSentimento.sentimento).label("count")
                ).group_by(models.AnaliseSentimento.sentimento)\
                        .order_by(func.count(models.AnaliseSentimento.sentimento).desc())\
                        .all()
    except NoResultFound: 
        raise Exception("Nenhum sentimento encontrado")
    
    except SQLAlchemyError:
        raise Exception("Erro ao buscar os sentimentos")

    return [SentimentoRecorrente(sentimento=sentimento, count=count) for sentimento, count in results]

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
    try: 
        if not id or id <= 0:
            raise Exception("ID inválido")
        
        return db.query(models.AnaliseSentimento).join(models.Acao).filter(models.Acao.agent_id == id).all()
    
    except NoResultFound: 
        raise Exception("Nenhum sentimento encontrado")
    
    except SQLAlchemyError:
        raise Exception("Erro ao buscar os sentimentos")

# retornar uma lista de atendimentos incluindo informações como conversa o sentimento.
def get_atendimento(db: Session):
    """
    Recupera informações de atendimento incluindo conversas, sentimentos, atendentes, etc.

    Args:
        db (Session): A sessão do banco de dados SQLAlchemy.

    Returns:
        list[tuple]: Uma lista de tuplas contendo informações de atendimento.
    """
    try: 
        results = db.query(
                models.Event.descricao.label("conversa"),
                models.AnaliseSentimento.score,
                models.AnaliseSentimento.sentimento.label("termo"),
                models.AnaliseSentimento.sentimento.label("sentimento_mais"),
                models.Agent.nome.label("atendente"),
                models.AnaliseSentimento.sentimento.label("sentimento_atendente")
                ).join(models.Acao, models.Acao.event_id == models.Event.event_id) \
                        .join(models.AnaliseSentimento, models.AnaliseSentimento.acao_id == models.Acao.acao_id) \
                        .join(models.Agent, models.Acao.agent_id == models.Agent.agent_id).all()
                        
    except NoResultFound: 
        raise Exception("Nenhum sentimento encontrado")
    
    except SQLAlchemyError:
        raise Exception("Erro ao buscar os sentimentos")

    return [Atendimento(**row._mapping) for row in results]

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
    try: 
        if not id or id <= 0:
            raise Exception("ID inválido")
        
        agente = db.query(
                models.Agent.nome.label("atendente"),
                models.AnaliseSentimento.sentimento.label("sentimento"),
                models.AnaliseSentimento.sentimento.label("sentimento_clientes"),
                models.AnaliseSentimento.sentimento.label("termo"),
                models.AnaliseSentimento.score
                ).join(models.Acao, models.Acao.agent_id == models.Agent.agent_id)\
                        .join(models.AnaliseSentimento, models.AnaliseSentimento.acao_id == models.Acao.acao_id)\
                        .filter(models.Agent.agent_id == id).first()

        
    except NoResultFound or agente == None: 
        raise Exception("Nenhum sentimento encontrado")
    
    except SQLAlchemyError:
        raise Exception("Erro ao buscar os sentimentos")

    return Agent(**agente._asdict())

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
    
    try: 
        if not id or id <= 0:
            raise Exception("ID inválido")
            
        cliente = db.query(
                models.User.name.label("cliente"),
                models.AnaliseSentimento.sentimento,
                models.AnaliseSentimento.sentimento.label("termo"),
                models.AnaliseSentimento.score
                ).join(models.Acao, models.Acao.user_id == models.User.user_id)\
                        .join(models.AnaliseSentimento, models.AnaliseSentimento.acao_id == models.Acao.acao_id)\
                        .filter(models.User.user_id == id).first()

    except NoResultFound or cliente == None: 
        raise Exception("Nenhum sentimento encontrado")
    
    except SQLAlchemyError:
        raise Exception("Erro ao buscar os sentimentos")

    return User(**cliente._asdict())
