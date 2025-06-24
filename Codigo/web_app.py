from flask import Flask, request, render_template, send_from_directory
import socket
import pickle
import os
import time

app = Flask(__name__)
UPLOAD_FOLDER = "results"  # Local onde workers salvam imagens segmentadas
SERVER_IP = "127.0.0.1"
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

        # Aguarda o processamento (simples delay)
        time.sleep(2)

        # Caminho esperado da imagem segmentada
        nome_saida = f"{os.path.splitext(nome)[0]}_segmentada.png"
        caminho_saida = os.path.join(UPLOAD_FOLDER, nome_saida)

        if os.path.exists(caminho_saida):
            return render_template("resultado.html", imagem_saida=nome_saida)
        else:
            return "<h3>Imagem enviada, mas ainda não processada. Tente novamente em instantes.</h3>"

    except Exception as e:
        return f"<h3>Erro ao enviar: {e}</h3>"

@app.route("/resultados/<nome_arquivo>")
def resultados(nome_arquivo):
    return send_from_directory(UPLOAD_FOLDER, nome_arquivo)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
