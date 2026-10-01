import socket


class Client:
    def __init__(self):
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, name, port):
        self.sk.connect((name, port))

    def send(self, message):
        self.sk.sendall(message.encode())

    def receive(self):
        return self.sk.recv(2048).decode()

    def disconnect(self):
        self.sk.close()

    def main(self):
        self.connect("localhost", 8089)

        self.send("B: Hello.")

        response = self.receive()
        print(response)

        self.disconnect()


client = Client()
client.main()