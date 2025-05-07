from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: Optional[str]
    score_cliente: float
    username: Optional[str]

class User(UserBase):
    user_id: int

    class Config:
        from_attributes = True


class AgentBase(BaseModel):
    nome: str
    email: Optional[str]
    score_agente: float
    username: Optional[str]

class AgentCreate(AgentBase):
    pass

class Agent(AgentBase):
    agent_id: int

    class Config:
        from_attributes = True


class EventBase(BaseModel):
    descricao: str
    data_abertura: datetime
    status_id: int
    data_baixa: Optional[datetime]

class EventCreate(EventBase):
    pass

class Event(EventBase):
    event_id: int

    class Config:
        from_attributes = True


class AcaoBase(BaseModel):
    event_id: int
    descricao: str
    agent_id: Optional[int]
    user_id: Optional[int]
    data_acao: Optional[datetime]

class Acao(AcaoBase):
    acao_id: int

    class Config:
        from_attributes = True


class AnaliseSentimentoBase(BaseModel):
    acao_id: int
    sentimento: str
    score: float
    modelo: Optional[str]
    data_analise: datetime

class AnaliseSentimento(AnaliseSentimentoBase):
    analise_id: int

    class Config:
        from_attributes = True
