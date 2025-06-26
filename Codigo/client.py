import socket
import pickle
import os
import struct

SERVER_HOST = 'localhost'
SERVER_PORT = 8000

def enviar_com_cabecalho(sock, payload):
    dados_serializados = pickle.dumps(payload)
    tamanho = struct.pack('>I', len(dados_serializados))
    sock.sendall(tamanho + dados_serializados)

def enviar_para_servidor(nome_arquivo, caminho_completo):
    try:
        with open(caminho_completo, 'rb') as f:
            imagem_binaria = f.read()

        dados = {
            'nome': nome_arquivo,
            'dados': imagem_binaria
        }

        with socket.create_connection((SERVER_HOST, SERVER_PORT), timeout=10) as s:
            enviar_com_cabecalho(s, dados)
            print(f"[Cliente] Imagem '{nome_arquivo}' enviada com sucesso.")
    except Exception as e:
        print(f"[Cliente] Erro ao enviar '{nome_arquivo}': {e}")

def enviar_varias_imagens(pasta_imagens):
    for nome_arquivo in os.listdir(pasta_imagens):
        if nome_arquivo.lower().endswith(('.png', '.jpg', '.jpeg')):
            caminho_completo = os.path.join(pasta_imagens, nome_arquivo)
            enviar_para_servidor(nome_arquivo, caminho_completo)

if __name__ == "__main__":
    pasta = 'static/uploads'
    if os.path.exists(pasta):
        enviar_varias_imagens(pasta)
    else:
        print(f"[Cliente] Pasta '{pasta}' não encontrada.")

