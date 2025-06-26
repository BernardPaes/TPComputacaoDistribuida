import socket
import pickle
import threading
import queue
import subprocess
import os
import time
import struct

HOST = '0.0.0.0'
PORT = 8000
MAX_WORKERS = 5
WORKER_START_PORT = 9001
TIMEOUT = 5

fila = queue.Queue()
workers_ativos = {}  # {porta: ocupado (bool)}
lock = threading.Lock()

def receber_n(sock, n):
    dados = b''
    while len(dados) < n:
        parte = sock.recv(n - len(dados))
        if not parte:
            raise EOFError("Conexão encerrada prematuramente")
        dados += parte
    return dados

def receber_payload(sock):
    """Lê cabeçalho (4 bytes) com o tamanho e depois os dados"""
    cabecalho = receber_n(sock, 4)
    tamanho = struct.unpack('>I', cabecalho)[0]
    return receber_n(sock, tamanho)

def iniciar_worker(porta):
    print(f"[Servidor] Iniciando worker na porta {porta}")
    subprocess.Popen(['python', 'worker.py', str(porta)])
    time.sleep(1)
    workers_ativos[porta] = False

def gerenciar_workers():
    with lock:
        if len(workers_ativos) < MAX_WORKERS:
            nova_porta = WORKER_START_PORT + len(workers_ativos)
            iniciar_worker(nova_porta)

def distribuir_tarefas():
    while True:
        dados = fila.get()
        enviado = False

        while not enviado:
            with lock:
                portas_disponiveis = [porta for porta, ocupado in workers_ativos.items() if not ocupado]

            if not portas_disponiveis:
                time.sleep(1)
                continue

            for porta in portas_disponiveis:
                try:
                    workers_ativos[porta] = True
                    with socket.create_connection(('localhost', porta), timeout=TIMEOUT) as s:
                        dados_serializados = pickle.dumps(dados)
                        tamanho = struct.pack('>I', len(dados_serializados))
                        s.sendall(tamanho + dados_serializados)
                    print(f"[Servidor] Tarefa enviada para worker na porta {porta}")
                    enviado = True
                    break
                except Exception as e:
                    print(f"[Servidor] Erro ao enviar para worker {porta}: {e}")
                    workers_ativos[porta] = False

            if not enviado:
                print("[Servidor] Nenhum worker disponível. Recolocando na fila.")
                time.sleep(1)

        def liberar_worker(porta):
            time.sleep(3)
            with lock:
                workers_ativos[porta] = False

        threading.Thread(target=liberar_worker, args=(porta,), daemon=True).start()

def aceitar_conexoes():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as servidor:
        servidor.bind((HOST, PORT))
        servidor.listen()
        print(f"[Servidor] Aguardando conexões em {HOST}:{PORT}...")

        while True:
            conn, addr = servidor.accept()
            print(f"[Servidor] Conexão recebida de {addr}")
            with conn:
                try:
                    dados_recebidos = receber_payload(conn)
                    payload = pickle.loads(dados_recebidos)
                    fila.put(payload)
                    print(f"[Servidor] Tarefa adicionada à fila: {payload['nome']}")
                    gerenciar_workers()
                except Exception as e:
                    print(f"[Servidor] Erro ao processar dados recebidos: {e}")

if __name__ == '__main__':
    print("[Servidor] Iniciando sistema de distribuição de tarefas...")
    threading.Thread(target=distribuir_tarefas, daemon=True).start()
    aceitar_conexoes()
