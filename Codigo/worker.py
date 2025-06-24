import socket
import pickle
import os
from slic import aplicar_slic, salvar_segmentacao

HOST = '0.0.0.0'  # Escuta em todas as interfaces de rede
PORT = 9001       # Porta configurável para o worker

def processar_imagem_serializada(pacote, pasta_saida="resultados_worker"):
    """
    Processa a imagem recebida via rede.
    
    Parâmetros:
        pacote (dict): Contém 'nome' e 'dados' (bytes da imagem).
        pasta_saida (str): Diretório para salvar as imagens processadas.
    """
    nome_arquivo = pacote['nome']
    dados = pacote['dados']

    # Salva temporariamente a imagem recebida
    os.makedirs("tmp", exist_ok=True)
    caminho_temp = os.path.join("tmp", nome_arquivo)
    with open(caminho_temp, 'wb') as f:
        f.write(dados)

    # Aplica SLIC e salva resultado
    imagem_segmentada, _ = aplicar_slic(caminho_temp)
    caminho_final = salvar_segmentacao(imagem_segmentada, pasta_saida, os.path.splitext(nome_arquivo)[0])
    print(f"[Worker] Imagem processada e salva em: {caminho_final}")

def iniciar_worker():
    """
    Inicia o servidor worker que escuta requisições do servidor central.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[Worker] Aguardando conexões em {HOST}:{PORT}...")

        while True:
            conn, addr = s.accept()
            with conn:
                print(f"[Worker] Conexão recebida de {addr}")
                dados_recebidos = b""
                while True:
                    buffer = conn.recv(4096)
                    if not buffer:
                        break
                    dados_recebidos += buffer

                try:
                    pacote = pickle.loads(dados_recebidos)
                    processar_imagem_serializada(pacote)
                except Exception as e:
                    print(f"[Worker] Erro ao processar imagem: {e}")

if __name__ == "__main__":
    iniciar_worker()
