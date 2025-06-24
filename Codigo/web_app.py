from flask import Flask, request, render_template
import socket
import pickle
import os

app = Flask(__name__)

# IP e porta do servidor central
SERVER_IP = "127.0.0.1"  # ← troque para o IP real do server.py
SERVER_PORT = 8000

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    imagem = request.files["imagem"]
    if not imagem:
        return "Nenhuma imagem enviada.", 400

    nome = imagem.filename
    dados = imagem.read()
    pacote = {"nome": nome, "dados": dados}

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((SERVER_IP, SERVER_PORT))
            s.sendall(pickle.dumps(pacote))
        return f"<h3>Imagem '{nome}' enviada com sucesso!</h3>"
    except Exception as e:
        return f"<h3>Erro ao enviar: {e}</h3>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)  # acessível via IP local

