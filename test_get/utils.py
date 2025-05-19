import requests
import time

def medir_tempo(url):
    """Mede o tempo de resposta de uma requisição GET."""
    inicio = time.perf_counter()
    resposta = requests.get(url)
    fim = time.perf_counter()
    duracao = fim - inicio
    return duracao, resposta
