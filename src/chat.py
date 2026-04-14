import socket
import threading
import sys

clients = []
names = {}


def receive_messages(client):
    while True:
        try:
            message = client.recv(1024).decode()
            if message:
                print("\n" + message)
                print("[You]: ", end="", flush=True)
        except:
            print("\nПотеряно соединение")
            client.close()
            break


def send_messages(client):
    while True:
        msg = input("[You]: ")
        if msg.lower() == "exit":
            client.close()
            sys.exit()
        client.send(msg.encode())


def start_client():
    host = input("IP сервера подключения: ").strip()
    port = int(input("Порт сервера: ").strip())

    my_ip = input("Введите ваш исходящий IP : ").strip()
    my_port = int(input("Введите ваш порт: ").strip())
    name = input("Ваше имя: ").strip()

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.bind((my_ip, my_port))

    client.connect((host, port))
    client.send(name.encode("utf-8", errors="ignore"))

    print(f"\nДобро пожаловать, {name}!")
    print(f"Ваш адрес: {my_ip}")
    print("Введите 'exit' для выхода\n")

    threading.Thread(target=receive_messages, args=(client,), daemon=True).start()
    send_messages(client)


def broadcast(message, sender=None):
    for client in clients:
        if client != sender:
            try:
                client.send(message.encode())
            except:
                clients.remove(client)


def handle_client(client):
    try:
        name = client.recv(1024).decode()
        names[client] = name

        broadcast(f"{name} подключился к чату")

        while True:
            message = client.recv(1024).decode("utf-8", errors="ignore")
            if not message:
                break

            formatted = f"[{name}]: {message}"
            print(formatted)
            broadcast(formatted, client)

    except:
        pass

    finally:
        name = names.get(client, "Unknown")
        print(f"{name} отключился")

        if client in clients:
            clients.remove(client)
        if client in names:
            del names[client]

        broadcast(f"{name} покинул чат")
        client.close()


def start_server():
    host = input("Введите IP: ").strip()
    port = int(input("Введите порт: ").strip())

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server.bind((host, port))
    except OSError:
        print("Порт занят!")
        return

    server.listen()

    server.settimeout(1.0)

    print(f"Сервер запущен на {host}:{port}")
    print("Для выключения сервера нажмите Ctrl+C")

    try:
        while True:
            try:
                client, addr = server.accept()
                print(f"Подключение: {addr}")
                clients.append(client)
                thread = threading.Thread(target=handle_client, args=(client,), daemon=True)
                thread.start()
            except socket.timeout:
                pass

    except KeyboardInterrupt:
        print("\n! Остановка сервера")

    finally:
        print("Отключаем клиентов")
        for client in clients:
            try:
                client.send("Сервер завершил работу".encode())
                client.close()
            except:
                pass

        server.close()
        print("Сервер успешно выключен")
        sys.exit(0)


if __name__ == "__main__":
    print("Выберите режим:")
    print("1 - Сервер")
    print("2 - Клиент")

    choice = input("Введите 1 или 2: ")

    if choice == "1":
        start_server()
    elif choice == "2":
        start_client()
    else:
        print("Неверный выбор")