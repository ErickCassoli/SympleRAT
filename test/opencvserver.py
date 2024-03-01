import cv2
import socket
import pickle
import struct

# Configurações do socket
host = '0.0.0.0'
port = 9999

# Inicializa o socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("Socket criado")

# Associa o socket ao endereço e à porta
s.bind((host, port))
print("Socket associado ao endereço e à porta")

# Coloca o socket em modo de escuta
s.listen(5)
print("Socket em modo de escuta")

# Aceita a conexão
print("Aguardando conexão...")
conn, addr = s.accept()
print(f"Conexão estabelecida com {addr}")

data = b''  # Inicializa os dados recebidos como bytes vazios
payload_size = struct.calcsize("Q")  # Tamanho do cabeçalho
print(f"Tamanho do cabeçalho: {payload_size}")

while True:
    while len(data) < payload_size:
        # Continua recebendo dados até que o cabeçalho esteja completo
        packet = conn.recv(4*1024)  # Recebe 4KB de dados
        if not packet: 
            break
        data += packet
    print("Cabeçalho recebido")

    # Extrai o tamanho do frame do cabeçalho
    packed_msg_size = data[:payload_size]
    data = data[payload_size:]
    # Desempacota o tamanho do frame como um inteiro de 64 bits
    msg_size = struct.unpack("Q", packed_msg_size)[0]
    print(f"Tamanho do frame: {msg_size}")

    # Recebe os dados do frame
    while len(data) < msg_size:
        # Continua recebendo dados até que o frame esteja completo
        packet = conn.recv(4*1024)  # Recebe 4KB de dados
        if not packet: 
            break
        data += packet
    
    # Agora temos todos os dados do frame, podemos processá-lo
    frame_data = data[:msg_size]
    data = data[msg_size:]
    frame = pickle.loads(frame_data)
    # Faça o que quiser com o frame, como exibí-lo ou salvá-lo em disco

    # Exibe o frame
    cv2.imshow('frame', frame)
    print("Frame exibido")

    if cv2.waitKey(1) == 27:
        break

# Fecha a conexão e a janela
conn.close()
print("Conexão fechada")
cv2.destroyAllWindows()
print("Janela fechada")
