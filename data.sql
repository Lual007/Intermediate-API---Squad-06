-- ===========================================
-- ETAPA 1: Limpar tudo (executar só 1 vez)
-- ===========================================
DROP TABLE IF EXISTS cs_analise_sentimento CASCADE;
DROP TABLE IF EXISTS cs_acoes CASCADE;
DROP TABLE IF EXISTS cs_events CASCADE;
DROP TABLE IF EXISTS cs_agents CASCADE;
DROP TABLE IF EXISTS cs_user CASCADE;

-- ===========================================
-- ETAPA 2: Criar tabelas
-- ===========================================

-- TABELA DE USUÁRIOS
CREATE TABLE cs_user (
    user_id SERIAL PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(70) UNIQUE,
    username VARCHAR(255)
);

-- TABELA DE AGENTES TÉCNICOS
CREATE TABLE cs_agents (
    agent_id SERIAL PRIMARY KEY,
    nome VARCHAR(150),
    email VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL
);

-- TABELA DE EVENTOS
CREATE TABLE cs_events (
    event_id SERIAL PRIMARY KEY,
    descricao VARCHAR(255) NOT NULL,
    data_abertura TIMESTAMPTZ NOT NULL,
    data_baixa TIMESTAMPTZ,
    status_id INTEGER NOT NULL
);

-- TABELA DE AÇÕES
CREATE TABLE cs_acoes (
    acao_id SERIAL PRIMARY KEY,
    event_id INTEGER NOT NULL,
    descricao TEXT NOT NULL,
    agent_id INTEGER,
    user_id INTEGER,
    data_acao TIMESTAMPTZ,
    CONSTRAINT fk_event FOREIGN KEY (event_id) REFERENCES cs_events(event_id),
    CONSTRAINT fk_agent FOREIGN KEY (agent_id) REFERENCES cs_agents(agent_id),
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES cs_user(user_id)
);

-- TABELA DE ANÁLISE DE SENTIMENTO
CREATE TABLE cs_analise_sentimento (
    analise_id SERIAL PRIMARY KEY,
    acao_id INTEGER NOT NULL,
    sentimento VARCHAR(20) NOT NULL CHECK (sentimento IN ('positivo', 'neutro', 'negativo')),
    score DECIMAL(5,2),
    modelo VARCHAR(100),
    data_analise TIMESTAMPTZ,
    CONSTRAINT fk_acao FOREIGN KEY (acao_id) REFERENCES cs_acoes(acao_id)
);
