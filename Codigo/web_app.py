import os
import socket
import pickle
import struct
import time
from flask import Flask, render_template, request, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from datetime import datetime
import zipfile
import io

UPLOAD_FOLDER = 'static/uploads'
RESULT_FOLDER = 'static/results'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULT_FOLDER'] = RESULT_FOLDER

SERVER_HOST = 'localhost'
SERVER_PORT = 8000

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

def enviar_com_cabecalho(sock, payload):
    dados_serializados = pickle.dumps(payload)
    tamanho = struct.pack('>I', len(dados_serializados))
    sock.sendall(tamanho + dados_serializados)

def aguardar_segmentacao(nomes, timeout=30):
    print(f"[WebApp] Aguardando segmentações... ({len(nomes)} arquivos)")
    inicio = time.time()
    faltando = set(nomes)

    while time.time() - inicio < timeout:
        prontas = []
        for nome in faltando:
            nome_segmentado = nome.replace('.', '_final.')
            caminho = os.path.join(app.config['RESULT_FOLDER'], nome_segmentado)
            if os.path.exists(caminho):
                prontas.append(nome)

        for nome in prontas:
            faltando.discard(nome)

        if not faltando:
            print("[WebApp] Todas as imagens segmentadas detectadas.")
            return True

        print(f"[WebApp] Aguardando {len(faltando)} restantes...")
        time.sleep(0.5)

    print("[WebApp] Timeout ao aguardar segmentações:", faltando)
    return False

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'imagem' not in request.files:
        return "Nenhum arquivo enviado", 400

    arquivos = request.files.getlist('imagem')
    nomes_imagens = []

    for arquivo in arquivos:
        if arquivo.filename == '':
            continue

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        nome_seguro = secure_filename(arquivo.filename)
        nome_final = f"{timestamp}_{nome_seguro}"
        caminho = os.path.join(app.config['UPLOAD_FOLDER'], nome_final)
        arquivo.save(caminho)

        print(f"[WebApp] Imagem salva: {caminho}")
        nomes_imagens.append(nome_final)

        try:
            with socket.create_connection((SERVER_HOST, SERVER_PORT), timeout=10) as s:
                payload = {
                    'nome': nome_final,
                    'dados': open(caminho, 'rb').read()
                }
                enviar_com_cabecalho(s, payload)
                print(f"[WebApp] Tarefa enviada para o servidor: {nome_final}")
        except Exception as e:
            print(f"[WebApp] Falha ao enviar tarefa ao servidor: {e}")

    # Espera o processamento antes de redirecionar
    aguardar_segmentacao(nomes_imagens)

    return redirect(url_for('resultado', imagens=','.join(nomes_imagens)))

@app.route('/resultado')
def resultado():
    imagens_param = request.args.get('imagens', '')
    nomes = imagens_param.split(',') if imagens_param else []
    return render_template('resultado.html', nomes=nomes)

@app.route('/download_zip', methods=['POST'])
def download_zip():
    nomes = request.form.getlist('nomes')
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for nome in nomes:
            nome_segmentado = nome.replace('.', '_final.')
            caminho = os.path.join(app.config['RESULT_FOLDER'], nome_segmentado)
            if os.path.exists(caminho):
                zip_file.write(caminho, arcname=nome_segmentado)

    zip_buffer.seek(0)
    return send_file(zip_buffer, as_attachment=True, download_name="segmentadas.zip", mimetype='application/zip')

if __name__ == '__main__':
    app.run(debug=True)
