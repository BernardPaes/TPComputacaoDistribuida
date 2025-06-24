from skimage.segmentation import slic
from skimage.color import label2rgb
from skimage.io import imread, imsave
import numpy as np
import os

def aplicar_slic(caminho_imagem, n_segmentos=250, compacidade=10):
    """
    Aplica o algoritmo SLIC a uma imagem e retorna a imagem segmentada.
    
    Parâmetros:
        caminho_imagem (str): Caminho para a imagem de entrada.
        n_segmentos (int): Número desejado de superpixels.
        compacidade (float): Parâmetro de compacidade do SLIC.
        
    Retorna:
        imagem_segmentada (np.ndarray): Imagem com os superpixels aplicados.
        segmentos (np.ndarray): Mapa de rótulos dos segmentos.
    """
    imagem = imread(caminho_imagem)
    segmentos = slic(imagem, n_segments=n_segmentos, compactness=compacidade, start_label=1)
    imagem_segmentada = label2rgb(segmentos, imagem, kind='avg')
    return imagem_segmentada, segmentos

def salvar_segmentacao(imagem_segmentada, caminho_saida, nome_base):
    """
    Salva a imagem segmentada no diretório especificado.
    
    Parâmetros:
        imagem_segmentada (np.ndarray): Imagem a ser salva.
        caminho_saida (str): Diretório de saída.
        nome_base (str): Nome base para o arquivo.
    """
    os.makedirs(caminho_saida, exist_ok=True)
    caminho_completo = os.path.join(caminho_saida, f"{nome_base}_slic.png")
    imsave(caminho_completo, (imagem_segmentada * 255).astype(np.uint8))
    return caminho_completo
