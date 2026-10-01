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

        self.send("A: Hello.")

        response = self.receive()
        print(response)

        self.disconnect()


client = Client()
client.main()



# clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # target machine and port
# clientsocket.connect(('localhost', 8089))

# message = "hello"

# # transfer message as binary
# clientsocket.sendall(message.encode())

# response = clientsocket.recv(2048).decode()
# print(response)

# clientsocket.close()