from socket import *
import concurrent.futures
import json

clients = list()


def send_message(player, message):
    try:
        param_list[player][0].send(json.dumps(message).encode("utf-8"))
    except Exception as e:
        print('Не получилось отправить сообщение игроку', player)


def clientThread(clientParams):
    clientSocket, clientAddress = clientParams
    try:
        clientSocket.send(json.dumps('Выберите камень / ножницы / бумага: ').encode("utf-8"))
        while True:
            answer = json.loads(clientSocket.recv(1024).decode("utf-8"))
            if answer == 'камень' or answer == 'ножницы' or answer == 'бумага':
                clientSocket.send(json.dumps('Ваш ход принят. Ждите пока соперник ответит').encode("utf-8"))
                break
            else:
                clientSocket.send(json.dumps('Ход ' + answer + ' не распознан. Введите один из вариантов: камень / ножницы / бумага').encode("utf-8"))

    except (ConnectionAbortedError, ConnectionResetError):
        clients.remove(clientSocket)
        print(clientAddress[0] + ":" + str(clientAddress[1]) + " disconnected")
        answer = 'disconnected'
        clientSocket.close()

    return answer


hostSocket = socket(AF_INET, SOCK_STREAM)
hostSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

hostIp = "127.0.0.1"
portNumber = 9090
hostSocket.bind((hostIp, portNumber))
hostSocket.listen()
print("Waiting for connection...")

param_list = list()
for i in range(2):
    clientSocket, clientAddress = hostSocket.accept()
    clients.append(clientSocket)
    print("Connection established with: ", clientAddress[0] + ":" + str(clientAddress[1]))

    param_list.append((clientSocket, clientAddress))

with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = [executor.submit(clientThread, param) for param in param_list]

answers = [f.result() for f in futures]

a = {
    "камень": "ножницы",
    "ножницы": "бумага",
    "бумага": "камень"
}

b = answers[0]
c = answers[1]


if b == 'disconnected' and b != c:
    print('Один из игроков отключился, игра отменена')
    send_message(1, '\nСоперник отключился, игра отменена')
elif c == 'disconnected' and b != c:
    print('Один из игроков отключился, игра отменена')
    send_message(0, '\nСоперник отключился, игра отменена')
elif c == 'disconnected' and b == 'disconnected':
    print("Оба игрока отключились, игра отменена")
else:
    print('Ход игрока 1:', b)
    print('Ход игрока 2:', c)

    send_message(0, '\nХод соперника: ' + c)
    send_message(1, '\nХод соперника: ' + b)

    if b == c:
        print("Ничья")
        send_message(0, 'Ничья')
        send_message(1, 'Ничья')
    for i, j in a.items():
        if b == i and c == j:
            print("Победил Игрок 1")
            send_message(0, 'Вы победили')
            send_message(1, 'Вы проиграли')
        elif c == i and b == j:
            print("Победил Игрок 2")
            send_message(0, 'Вы проиграли')
            send_message(1, 'Вы победили')

    for i in range(len(clients)):
        try:
            clients[i].close()
        except Exception as e:
            pass

hostSocket.close()
