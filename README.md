Api intermediária - Squad-06
========

Para rodar a aplicação é necessário:

- Python
- Docker 

Para rodar a aplicação:

1.  Crie um ambiente virtual e entre nele
```
python -m venv venv
venv/Scripts/activate

```

2. Ambra o terminal e rode o docker.

```
docker compose up
```

3. Em outro terminal entre no bash do container docker e no psql rode o comando do data.sql

```
docker exec -it intermediate-api---squad-06-postgres-1 bash     
```

4. Entre no banco com psql

```
psql -U postgres
```

5. Copie o data.sql e coloque no terminal do psql para criar a data, depois rode \dt para verificar as tabelas

6. Volte para o terminal do ambiente virtual, e rode:

```
uvicorn main:app --reload
```