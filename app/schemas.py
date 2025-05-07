from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    # name: str
    # email: Optional[str]
    # username: Optional[str]
    # user_id: int

    cliente: str
    sentimento: str
    termo: str
    score: float

    model_config = {
            "from_attributes": True
    }

class Agent(BaseModel):
    # agent_id: int
    # nome: str
    # email: Optional[str]
    # username: Optional[str]

    atendente: str
    sentimento: str
    sentimento_clientes: str
    termo: str
    score: float

    model_config = {
            "from_attributes": True
    }


class EventBase(BaseModel):
    descricao: str
    data_abertura: datetime
    status_id: int
    data_baixa: Optional[datetime]

class Event(EventBase):
    event_id: int

    model_config = {
            "from_attributes": True
    }


class AcaoBase(BaseModel):
    event_id: int
    descricao: str
    agent_id: Optional[int]
    user_id: Optional[int]
    data_acao: Optional[datetime]

class Acao(AcaoBase):
    acao_id: int

    model_config = {
            "from_attributes": True
    }

class AnaliseSentimento(BaseModel):
    acao_id: int
    sentimento: str
    score: float
    modelo: Optional[str]
    data_analise: datetime
    analise_id: int

    model_config = {
            "from_attributes": True
    }

class Atendimento(BaseModel):
    conversa: str
    score: float
    termo: str
    sentimento_mais: str
    atendente: str
    sentimento_atendente: str

class SentimentoRecorrente(BaseModel):
    sentimento: str
    count: int
