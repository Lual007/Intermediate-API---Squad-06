from sqlalchemy import Column, Integer, String, Text, ForeignKey, TIMESTAMP, DECIMAL
from sqlalchemy.orm import relationship
from .database import Base

class User(Base):
    __tablename__ = "cs_user"
    
    user_id = Column(Integer, primary_key=True, index=True)
    name = Column(String(150), nullable=False)
    email = Column(String(70))
    username = Column(String(255))

    acoes = relationship("Acao", back_populates="user")


class Agent(Base):
    __tablename__ = "cs_agents"
    
    agent_id = Column(Integer, primary_key=True, index=True)
    nome = Column(String(150))
    email = Column(String)
    username = Column(String)

    acoes = relationship("Acao", back_populates="agent")


class Event(Base):
    __tablename__ = "cs_events"
    
    event_id = Column(Integer, primary_key=True, index=True)
    descricao = Column(String, nullable=False)
    data_abertura = Column(TIMESTAMP, nullable=False)
    data_baixa = Column(TIMESTAMP)
    status_id = Column(Integer, nullable=False)

    acoes = relationship("Acao", back_populates="event")


class Acao(Base):
    __tablename__ = "cs_acoes"
    
    acao_id = Column(Integer, primary_key=True, index=True)
    event_id = Column(Integer, ForeignKey("cs_events.event_id"), nullable=False)
    descricao = Column(Text, nullable=False)
    agent_id = Column(Integer, ForeignKey("cs_agents.agent_id"))
    user_id = Column(Integer, ForeignKey("cs_user.user_id"))
    data_acao = Column(TIMESTAMP)

    event = relationship("Event", back_populates="acoes")
    agent = relationship("Agent", back_populates="acoes")
    user = relationship("User", back_populates="acoes")
    analises = relationship("AnaliseSentimento", back_populates="acao")


class AnaliseSentimento(Base):
    __tablename__ = "cs_analise_sentimento"
    
    analise_id = Column(Integer, primary_key=True, index=True)
    acao_id = Column(Integer, ForeignKey("cs_acoes.acao_id"), nullable=False)
    sentimento = Column(String(50), nullable=False)
    score = Column(DECIMAL(5,2))
    modelo = Column(String(100))
    data_analise = Column(TIMESTAMP)

    acao = relationship("Acao", back_populates="analises")
