import socket
import threading
import pickle
import os

# Configurações do servidor
HOST = "0.0.0.0"
PORTA = 8000

# Lista de workers disponíveis (IP e porta)
workers_disponiveis = [
    ("127.0.0.1", 9001),
    # Adicione mais workers conforme necessário
]

# Diretório onde serão salvas as imagens temporárias
os.makedirs("images", exist_ok=True)

def lidar_com_cliente(conexao, endereco):
    try:
        print(f"[Servidor] Conexão de {endereco}")
        dados_recebidos = b""
        while True:
            parte = conexao.recv(4096)
            if not parte:
                break
            dados_recebidos += parte

        dados = pickle.loads(dados_recebidos)
        nome_arquivo = dados["nome"]
        conteudo = dados["dados"]

        # Salva imagem temporariamente
        caminho = os.path.join("images", nome_arquivo)
        with open(caminho, "wb") as f:
            f.write(conteudo)
        print(f"[Servidor] Imagem '{nome_arquivo}' salva temporariamente.")

        # Envia para um dos workers disponíveis
        enviado = False
        for ip, porta in workers_disponiveis:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as ws:
                    ws.connect((ip, porta))
                    ws.sendall(pickle.dumps({
                        "nome": nome_arquivo,
                        "dados": conteudo
                    }))
                print(f"[Servidor] Imagem '{nome_arquivo}' enviada para {ip}:{porta}")
                enviado = True
                break
            except Exception as e:
                print(f"[Servidor] Erro ao enviar para {ip}:{porta} — {e}")
        
        if not enviado:
            print(f"[Servidor] Nenhum worker disponível para '{nome_arquivo}'")

    except Exception as e:
        print(f"[Servidor] Erro ao lidar com cliente {endereco}: {e}")
    finally:
        conexao.close()

def iniciar_servidor():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORTA))
        servidor.listen()
        print(f"[Servidor] Aguardando conexões em {HOST}:{PORTA}...")

        while True:
            conexao, endereco = servidor.accept()
            thread = threading.Thread(target=lidar_com_cliente, args=(conexao, endereco))
            thread.start()

if __name__ == "__main__":
    iniciar_servidor()
