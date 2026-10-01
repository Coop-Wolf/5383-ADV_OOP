import socket


class Server:
    def __init__(self):
        self.sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def bind(self, name, port):
        self.sk.bind((name, port))

    def listen(self):
        self.sk.listen()

    def receive(self):
        client, address = self.sk.accept()

        message = client.recv(2048).decode()
        print(message)

        client.sendall("Hello from server".encode())

        client.close()

    def disconnect(self):
        self.sk.close()

    def main(self):
        self.bind("localhost", 8089)
        self.listen()
        self.receive()
        self.disconnect()


server = Server()
server.main()





# class worker(threading.Thread):
#     def run(self):
#         time.sleep(10)
#         print("Thread finished")


# # CONFIGURING SERVER
# # =======================================
# serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# # target machine and port
# serversocket.bind(('localhost', 8089))

# # listen for one connection
# serversocket.listen(1)
# # ========================================

# for i in range(5):
    
#     # Accept connection and read message
#     client, address = serversocket.accept()
#     message = client.recv(2048).decode()

#     # Print message
#     print(message)
    
#     worker().start()
    
#     client.sendall("Hello from server".encode())

#     # Close connections
#     client.close()
    
# serversocket.close()