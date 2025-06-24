import socket
import pickle
import os
import io
from PIL import Image
from slic import aplicar_slic  # deve aceitar caminho de arquivo e retornar imagem segmentada

# Configurações do worker
HOST = "0.0.0.0"
PORTA = 9001

# Diretório onde serão salvas as imagens segmentadas
os.makedirs("results", exist_ok=True)

def processar_imagem(nome_arquivo, dados_imagem):
    # Caminho temporário da imagem recebida
    caminho_entrada = os.path.join("results", nome_arquivo)

    # Salva imagem temporária para ser processada
    with open(caminho_entrada, "wb") as f:
        f.write(dados_imagem)
    print(f"[Worker] Imagem recebida salva em '{caminho_entrada}'")

    # Aplica segmentação com base no caminho
    try:
        imagem_segmentada, _ = aplicar_slic(caminho_entrada)

        # Gera nome de saída
        nome_base = os.path.splitext(nome_arquivo)[0]
        nome_saida = f"{nome_base}_segmentada.png"
        caminho_saida = os.path.join("results", nome_saida)

        # Salva imagem segmentada
        imagem_segmentada.save(caminho_saida)
        print(f"[Worker] Segmentação concluída e salva em '{caminho_saida}'")
    except Exception as e:
        print(f"[Worker] Erro ao aplicar SLIC: {e}")

def iniciar_worker():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as worker:
        worker.bind((HOST, PORTA))
        worker.listen()
        print(f"[Worker] Aguardando imagens em {HOST}:{PORTA}...")

        while True:
            conexao, endereco = worker.accept()
            try:
                print(f"[Worker] Conexão recebida de {endereco}")
                dados_recebidos = b""
                while True:
                    parte = conexao.recv(4096)
                    if not parte:
                        break
                    dados_recebidos += parte

                pacote = pickle.loads(dados_recebidos)
                nome = pacote["nome"]
                dados = pacote["dados"]

                processar_imagem(nome, dados)

            except Exception as e:
                print(f"[Worker] Erro ao processar: {e}")
            finally:
                conexao.close()

if __name__ == "__main__":
    iniciar_worker()
