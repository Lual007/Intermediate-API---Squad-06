from sqlalchemy.orm import Session
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError

from app.schemas import Agent, Atendimento, SentimentoRecorrente, User
from app.producers.producer import RabbitMQProducer
from app.models import AnaliseSentimento
from .. import models
from .. import schemas
from fastapi.encoders import jsonable_encoder
import re
import unicodedata

def salvar_analise(db: Session, analise: models.AnaliseSentimento):
    """
    Salva a análise de sentimento no banco de dados.

    Args:
        db (Session): A sessão do banco de dados SQLAlchemy.
        analise (models.AnaliseSentimento): O objeto de análise de sentimento a ser salvo.

    Returns:
        models.AnaliseSentimento: O objeto salvo no banco de dados.
    """
    try:
        
        def normalize_word(word: str) -> str:
            # Convert to lowercase
            word = word.lower()
            # Normalize to NFD (decompose characters)
            word = unicodedata.normalize('NFD', word)
            # Remove diacritical marks
            word = re.sub(r'[\u0300-\u036f]', '', word)
            # Remove punctuation: ', ", ,, .
            word = re.sub(r"[\'\".,]", '', word)
            return word

        analise.sentimento = normalize_word(analise.sentimento)

        db.add(analise)
        db.commit()
        db.refresh(analise)
        return analise
    except SQLAlchemyError as e:
        db.rollback()
        raise Exception(f"Erro ao salvar a análise: {str(e)}")


# salvar analise 
def save_analise(db: Session, analise: models.AnaliseSentimento):

    publisher = RabbitMQProducer()
    
    publisher.send_menssage(db.descricao)
    
    publisher.close_connection()  

def enviar_mensagem(acao: schemas.Acao):

    publisher = RabbitMQProducer()
    
    publisher.send_menssage(jsonable_encoder(acao))

    publisher.close_connection()  
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
    
    except SQLAlchemyError:
        raise Exception("Erro ao buscar os sentimentos")

    data = [SentimentoRecorrente(sentimento=sentimento, count=count) for sentimento, count in results]
    return data

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
        sentimentos = db.query(models.AnaliseSentimento)\
                        .join(models.Acao)\
                        .filter(models.Acao.agent_id == id).all()
        
        if not sentimentos:
            raise Exception("Nenhum sentimento encontrado")

        return sentimentos
    
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
            models.AnaliseSentimento.sentimento.label("sentimento"),
            models.Agent.nome.label("atendente"),
            models.User.name.label("user"),
            models.Acao.data_acao,
            ).join(models.Acao, models.Acao.event_id == models.Event.event_id
            ).join(models.AnaliseSentimento, models.AnaliseSentimento.acao_id == models.Acao.acao_id
            ).join(models.Agent, models.Acao.agent_id == models.Agent.agent_id
            ).join(models.User, models.Acao.user_id == models.User.user_id
            ).all()
                        
    
    except SQLAlchemyError:
        raise Exception("Erro ao buscar os sentimentos")

    data = [Atendimento(**row._mapping) for row in results]
    return data

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

        if agente is None:
            raise Exception("Nenhum tecnico encontrado")
    
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

        if cliente is None:
            raise Exception("Nenhum cliente encontrado")
    
    except SQLAlchemyError:
        raise Exception("Erro ao buscar os sentimentos")

    return User(**cliente._asdict())

def get_tecnicos(db: Session):
    return db.query(models.Agent).all()

def get_clientes(db: Session):
    return db.query(models.User).all()

def get_sentimentos_by_score(min_score: float, max_score: float, db: Session):
    return db.query(models.AnaliseSentimento).filter(
        models.AnaliseSentimento.score >= min_score,
        models.AnaliseSentimento.score <= max_score
    ).all()

def get_sentimentos_by_data(start: str, end: str, db: Session):
    start_date = start
    end_date = end
    return db.query(models.AnaliseSentimento).filter(
        models.AnaliseSentimento.data_analise >= start_date,
        models.AnaliseSentimento.data_analise <= end_date
    ).all()

# Sentimento negativo com o menor score
def get_sentimento_mais_negativo(db: Session):
    sentimentos_negativos = ["raiva", "frustração", "confusão", "urgência"]
    
    total_count = db.query(func.count(models.AnaliseSentimento.analise_id)).scalar()

    if total_count == 0:
        return None

    resultado = db.query(models.AnaliseSentimento).filter(
        func.lower(models.AnaliseSentimento.sentimento).in_(
            [s.lower() for s in sentimentos_negativos]
        )
    ).order_by(models.AnaliseSentimento.score.asc()).first()

    if not resultado:
        return None

    count_sentimento = db.query(func.count(models.AnaliseSentimento.analise_id)).filter(
        func.lower(models.AnaliseSentimento.sentimento) == resultado.sentimento.lower()
    ).scalar()

    percentage = (count_sentimento / total_count) * 100

    return {
        "sentimento": resultado.sentimento,
        "score": resultado.score,
        "porcentagem": round(percentage, 2)
    }

def get_quantidade_sentimentos(db: Session):
    """
    Conta a quantidade de cada sentimento no banco de dados.
    """
    # Agrupar os sentimentos e contar a quantidade de cada um
    result = db.query(AnaliseSentimento.sentimento, func.count(AnaliseSentimento.sentimento).label('quantidade'))\
               .group_by(AnaliseSentimento.sentimento)\
               .all()
    
    return db.query(models.AnaliseSentimento).count()

def get_sentimento_mais_frequente(db):
    total = db.query(func.count(AnaliseSentimento.sentimento)).scalar()

    resultado = db.query(
        AnaliseSentimento.sentimento,
        func.count(AnaliseSentimento.sentimento).label("quantidade")
    ).group_by(
        AnaliseSentimento.sentimento
    ).order_by(
        func.count(AnaliseSentimento.sentimento).desc()
    ).first()

    if resultado:
        sentimento = resultado[0]
        quantidade = resultado[1]
        porcentagem = round((quantidade / total) * 100, 2) if total else 0

        return {
            "sentimento_predominante": sentimento, 
            "quantidade": quantidade,
            "porcentagem": porcentagem
        }
    else:
        return {"message": "Não há sentimentos registrados ainda."}
