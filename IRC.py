import socket
import threading
import sys


class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connections = []

    def __init__(self):
        self.sock.bind(('0.0.0.0', 10000))
        self.sock.listen(1)

    def handler(self, client, addr):
        while True:
            data = client.recv(1024)
            for connection in self.connections:
                connection.send(data)
            if not data:
                print(str([0]) + ':' + str(addr[1]), "disconnected")
                self.connections.remove(client)
                client.close()
                break

    def run(self):
        while True:
            client, addr = self.sock.accept()
            cThread = threading.Thread(target=self.handler, args=(client,addr))
            cThread.daemon = True
            cThread.start()
            self.connections.append(client)
            print(str([0]) + ':' + str(addr[1]), "connected")


class Client:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def send_msg(self):
        while True:
            self.sock.send(bytes(input(""), 'utf-8'))

    def __init__(self, address):
        self.sock.connect((address, 10000))

        iThread = threading.Thread(target=self.send_msg())
        iThread.daemon = True
        iThread.start()

        while True:
            data = self.sock.recv(1024)
            if not data:
                break
            print(data)

if (len(sys.argv) > 1):
    client = Client(sys.argv[1])
else:
    server = Server()
    server.run()

