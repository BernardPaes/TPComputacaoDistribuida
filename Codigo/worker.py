import socket
import pickle
import sys
import os
import numpy as np
import struct
from io import BytesIO
from PIL import Image
from slic import aplicar_slic

PORTA_PADRAO = 9001  # Porta inicial padrão

def salvar_imagem(caminho, imagem):
    os.makedirs(os.path.dirname(caminho), exist_ok=True)
    imagem.save(caminho)

def receber_n(sock, n):
    dados = b''
    while len(dados) < n:
        parte = sock.recv(n - len(dados))
        if not parte:
            raise EOFError("Conexão encerrada prematuramente")
        dados += parte
    return dados

def receber_payload(sock):
    cabecalho = receber_n(sock, 4)
    tamanho = struct.unpack('>I', cabecalho)[0]
    return receber_n(sock, tamanho)

def processar_dados(recebido):
    try:
        nome_arquivo = recebido['nome']
        dados_imagem = recebido['dados']
        imagem = Image.open(BytesIO(dados_imagem)).convert("RGB")
        imagem_np = np.array(imagem)

        print(f"[Worker:{porta}] Processando imagem: {nome_arquivo}")

        imagem_segmentada = aplicar_slic(imagem_np)
        imagem_segmentada_pil = Image.fromarray(imagem_segmentada)

        caminho_resultado = os.path.join("static", "results", nome_arquivo.replace(".", "_final."))
        salvar_imagem(caminho_resultado, imagem_segmentada_pil)

        print(f"[Worker:{porta}] Imagem processada e salva em: {caminho_resultado}")

    except Exception as e:
        print(f"[Worker:{porta}] Erro ao processar imagem: {e}")

if __name__ == '__main__':
    porta = int(sys.argv[1]) if len(sys.argv) > 1 else PORTA_PADRAO

    print(f"[Worker:{porta}] Aguardando imagens em 0.0.0.0:{porta}...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind(('0.0.0.0', porta))
        servidor.listen()

        while True:
            conexao, endereco = servidor.accept()
            with conexao:
                print(f"[Worker:{porta}] Conexão recebida de {endereco}")
                try:
                    dados = receber_payload(conexao)
                    recebido = pickle.loads(dados)
                    processar_dados(recebido)
                except Exception as e:
                    print(f"[Worker:{porta}] Erro ao receber/processar: {e}")
