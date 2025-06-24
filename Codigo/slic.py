def aplicar_slic(caminho_imagem):
    from PIL import Image
    from skimage.io import imread
    from skimage.segmentation import slic
    from skimage.color import label2rgb
    import numpy as np

    imagem = imread(caminho_imagem)
    segmentos = slic(imagem, n_segments=250, compactness=10, start_label=1)
    imagem_segmentada = label2rgb(segmentos, imagem, kind='avg')
    
    # Retorna imagem PIL
    return Image.fromarray((imagem_segmentada * 255).astype(np.uint8)), segmentos
