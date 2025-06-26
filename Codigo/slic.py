import numpy as np
from skimage.segmentation import slic
from skimage.color import label2rgb
from skimage.util import img_as_ubyte

def aplicar_slic(imagem_np):
    # Número fixo de segmentos
    num_segmentos = 150

    # Segmentação usando SLIC
    segmentos = slic(imagem_np, n_segments=num_segmentos, compactness=10, sigma=1, start_label=1)

    # Mapeia os rótulos dos segmentos de volta para cores médias
    imagem_segmentada = label2rgb(segmentos, imagem_np, kind='avg')

    # Converte para uint8 (imagem visualizável)
    return img_as_ubyte(imagem_segmentada)
