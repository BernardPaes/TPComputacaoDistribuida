import socket
import threading
import pickle
import queue

# Configurações do servidor central
HOST = '0.0.0.0'
PORT = 8000

# Lista de workers disponíveis (host, porta)
workers_disponiveis = [
    ('localhost', 9001),
    # Adicione mais workers conforme necessário
    ('127.0.0.1', 9001),
]

# Fila para armazenar imagens recebidas dos clientes
fila_imagens = queue.Queue()

def encaminhar_para_worker(pacote, worker_host, worker_port):
    """Encaminha uma imagem serializada para um worker específico."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((worker_host, worker_port))
            s.sendall(pickle.dumps(pacote))
            print(f"[Servidor] Imagem '{pacote['nome']}' enviada para {worker_host}:{worker_port}")
    except Exception as e:
        print(f"[Servidor] Erro ao enviar imagem para {worker_host}:{worker_port}: {e}")

def despachante():
    """Thread responsável por despachar imagens para os workers em round-robin."""
    worker_idx = 0
    while True:
        pacote = fila_imagens.get()
        worker_host, worker_port = workers_disponiveis[worker_idx]
        encaminhar_para_worker(pacote, worker_host, worker_port)
        worker_idx = (worker_idx + 1) % len(workers_disponiveis)
        fila_imagens.task_done()

def lidar_com_cliente(conn, addr):
    """Recebe a imagem de um cliente e adiciona na fila de despacho."""
    print(f"[Servidor] Cliente conectado: {addr}")
    dados_recebidos = b""
    while True:
        buffer = conn.recv(4096)
        if not buffer:
            break
        dados_recebidos += buffer

    try:
        pacote = pickle.loads(dados_recebidos)
        fila_imagens.put(pacote)
        print(f"[Servidor] Imagem '{pacote['nome']}' recebida de {addr}")
    except Exception as e:
        print(f"[Servidor] Erro ao processar pacote de {addr}: {e}")
    finally:
        conn.close()

def iniciar_servidor():
    """Inicializa o servidor que aceita conexões de clientes."""
    threading.Thread(target=despachante, daemon=True).start()

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"[Servidor] Aguardando conexões de clientes em {HOST}:{PORT}...")

        while True:
            conn, addr = s.accept()
            threading.Thread(target=lidar_com_cliente, args=(conn, addr), daemon=True).start()

if __name__ == "__main__":
    iniciar_servidor()
