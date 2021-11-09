from socket import *
import json

clientSocket = socket(AF_INET, SOCK_STREAM)
clientSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

hostIp = "127.0.0.1"
portNumber = 9090

clientSocket.connect((hostIp, portNumber))
print('Ожидание другого игрока')

try:
    serverMessage = json.loads(clientSocket.recv(1024).decode("utf-8"))  # введите ход
    print(serverMessage)

    serverMessage = ''
    while serverMessage != 'Ваш ход принят. Ждите пока соперник ответит':
        clientMessage = input()
        clientSocket.send(json.dumps(clientMessage).encode("utf-8"))

        serverMessage = json.loads(clientSocket.recv(1024).decode("utf-8"))  # ожидайте или ход не распознан
        print(serverMessage)

    serverMessage = json.loads(clientSocket.recv(1024).decode("utf-8"))  # ход соперника
    print(serverMessage)

    serverMessage = json.loads(clientSocket.recv(1024).decode("utf-8"))  # исход игры
    print(serverMessage)

    clientSocket.close()
except Exception as e:
    print('Возникла ошибка, отключение игры')
