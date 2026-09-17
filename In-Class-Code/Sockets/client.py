import socket

clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# target machine and port
clientsocket.connect(('localhost', 8089))

message = "hello"

# transfer message as binary
clientsocket.sendall(message.encode())

response = clientsocket.recv(2048).decode()
print(response)

clientsocket.close()