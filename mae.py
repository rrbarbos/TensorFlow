import cv2
import numpy as np
import os
os.environ["OPENCV_FFMPEG_CAPTURE_OPTIONS"] = "rtsp_transport;udp"

#variaveis globais
width = 0
height = 0
ContadorEntradas = 0
ContadorSaidas = 0
AreaContornoLimiteMin = 300  #este valor eh empirico. Ajuste-o conforme sua necessidade 
ThresholdBinarizacao =30  #este valor eh empirico, Ajuste-o conforme sua necessidade
OffsetLinhasRef = 340  #este valor eh empirico. Ajuste- conforme sua necessidade.


def calculaDiferenca(img1, img2, img3):
  d1 = cv2.absdiff(img3, img2)
  d2 = cv2.absdiff(img2, img1)
  imagem = cv2.bitwise_and(d1, d2)
  s,imagem = cv2.threshold(imagem, 30, 255, cv2.THRESH_TOZERO)
  return cv2.bitwise_and(d1, d2)

#Função para facilitar a escrita nas imagem
def escreve(img, texto, cor=(255,0,0)):
    fonte = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, texto, (10,20), fonte, 0.5, cor, 0,
     cv2.LINE_AA)


vcap = cv2.VideoCapture("rtsp://rrbarbos:petro1492@@192.168.1.105/cam/realmonitor?channel=6&subtype=0",
                        cv2.CAP_FFMPEG)
janela = "Tela de captura"
janela2 = "Tela Normal"
cv2.namedWindow(janela, cv2.WINDOW_AUTOSIZE) #cria uma janela
cv2.namedWindow(janela2, cv2.WINDOW_AUTOSIZE)

#faz a leitura inicial de imagens
frame_cap = vcap.read()[1]
ultima        = cv2.cvtColor(frame_cap, cv2.COLOR_RGB2GRAY)
penultima     = ultima
antepenultima = ultima

while(1):
    frame_cap = vcap.read()[1]
    antepenultima = penultima
    penultima     = ultima
    
     #converte frame para escala de cinza e aplica efeito blur (para realcar os contornos)
    ultima        = cv2.cvtColor(frame_cap, cv2.COLOR_RGB2GRAY)
#    ultima = cv2.GaussianBlur(ultima, (21, 21), 0)
    
#    ret, frame = vcap.read()
    # if ret == False:
    #     print("Frame is empty")
    #     break;
    # else:
#        cv2.imshow('VIDEO', frame)
    
    movimento = calculaDiferenca(antepenultima,penultima,ultima)
    escreve(movimento, str(sum(sum(movimento))), 255)
    
    # FrameGray = cv2.GaussianBlur(ultima, (21, 21), 0)
    FrameThresh = cv2.threshold(ultima, ThresholdBinarizacao, 255, cv2.THRESH_BINARY)[1]
    FrameThresh = cv2.dilate(FrameThresh, None, iterations=2)
    _, cnts, _ = cv2.findContours(FrameThresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    QtdeContornos = 0
    
   
    
    #Varre todos os contornos encontrados
    for c in cnts:
        #contornos de area muto pequena sao ignorados.
        if cv2.contourArea(c) < 70:
            continue
    
        #Para fins de depuracao, contabiliza numero de contornos encontrados
        QtdeContornos = QtdeContornos+1    
    
        #obtem coordenadas do contorno (na verdade, de um retangulo que consegue abrangir todo ocontorno) e
        #realca o contorno com um retangulo.
        (x, y, w, h) = cv2.boundingRect(c) #x e y: coordenadas do vertice superior esquerdo
                                           #w e h: respectivamente largura e altura do retangulo
    
        cv2.rectangle(frame_cap, (x, y), (x + w, y + h), (0, 255, 0), 2)
    
        #determina o ponto central do contorno e desenha um circulo para indicar
        CoordenadaXCentroContorno = int((x+x+w)/2)
        CoordenadaYCentroContorno = int((y+y+h)/2)
        PontoCentralContorno = (CoordenadaXCentroContorno,CoordenadaYCentroContorno)
        cv2.circle(frame_cap, PontoCentralContorno, 1, (0, 0, 0), 5)
        
    
        # Se necessario, descomentar as lihas abaixo para mostrar os frames utilizados no processamento da imagem
#        cv2.imshow("Frame binarizado", FrameThresh)

#        cv2.imshow(janela, movimento)
        cv2.imshow(janela2, frame_cap)

    k=cv2.waitKey(33)
    
    if k==27:    # Esc key to stop
        break
    elif k==-1:  # normally -1 returned,so don't print it
        continue
    else:
        print(k) # else print its value        
            
            
vcap.release()
# cv2.destroyAllWindows()