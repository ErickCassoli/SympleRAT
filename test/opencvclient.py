import struct
import cv2
import socket
import pickle

# Configurações do socket
host = '192.168.100.99'  # Substitua 'IP_da_máquina_B' pelo IP da máquina B
port = 9999

# Inicializa a captura de vídeo
cam = cv2.VideoCapture(0)

# Configuração do socket para enviar dados
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket criado")

try:
    # Estabelece conexão com o servidor
    s.connect((host, port))
    print("Conexão estabelecida com o servidor")
except socket.error as err:
    print(f"Erro ao conectar ao servidor: {err}")
    exit()

while True:
    ret, frame = cam.read()
    # Serializa o frame usando pickle
    data = pickle.dumps(frame)
    # Envia o tamanho do frame
    try:
        # Empacota o tamanho do frame como um inteiro de 64 bits (8 bytes)
        msg_size = struct.pack("Q", len(data))
        s.sendall(msg_size)
        # Envia os dados do frame
        s.sendall(data)
        print("Dados enviados ao servidor")
    except socket.error as err:
        print(f"Erro ao enviar dados ao servidor: {err}")
        break

    if cv2.waitKey(1) == 27:
        break

# Libera a câmera e fecha a conexão
cam.release()
cv2.destroyAllWindows()
s.close()
print("Conexão fechada")
