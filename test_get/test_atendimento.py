from utils import medir_tempo

def testar_get_atendimento():
    url = "http://127.0.0.1:8000/atendimento"
    duracao, resposta = medir_tempo(url)

    print(f"\nGET {url}")
    print(f"Status: {resposta.status_code}")
    print(f"Tempo de resposta: {duracao:.4f} segundos")
    try:
        print("Dados:", resposta.json())
    except Exception as e:
        print("Erro ao interpretar JSON:", e)

if __name__ == "__main__":
    testar_get_atendimento()
