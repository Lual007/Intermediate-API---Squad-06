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


class Acao(BaseModel):
    acao_id: int
    event_id: int
    descricao: str
    agent_id: Optional[int]
    user_id: Optional[int]
    data_acao: Optional[datetime]

    model_config = {
            "from_attributes": True
    }

class AnaliseSentimento(BaseModel):
    analise_id: int
    acao_id: int
    user_id: int
    agent_id: int
    sentimento: str
    score: float
    data_analise: datetime
    acao: Optional[Acao]

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
