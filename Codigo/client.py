import socket
import pickle
import sys
import os

def enviar_imagem(caminho_imagem, host_servidor, porta):
    """Envia uma imagem serializada para o servidor central."""
    try:
        nome_imagem = os.path.basename(caminho_imagem)
        with open(caminho_imagem, "rb") as f:
            dados_imagem = f.read()

        pacote = {
            "nome": nome_imagem,
            "dados": dados_imagem
        }

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((host_servidor, int(porta)))
            s.sendall(pickle.dumps(pacote))
            print(f"[Cliente] Imagem '{nome_imagem}' enviada para {host_servidor}:{porta}")

    except Exception as e:
        print(f"[Cliente] Erro ao enviar imagem: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Uso: python client.py <caminho_imagem> <host_servidor> <porta>")
    else:
        caminho_imagem = sys.argv[1]
        host_servidor = sys.argv[2]
        porta = sys.argv[3]
        enviar_imagem(caminho_imagem, host_servidor, porta)
