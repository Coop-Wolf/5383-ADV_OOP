import socket
import threading
import time

class worker(threading.Thread):
    def run(self):
        time.sleep(10)
        print("Thread finished")


# CONFIGURING SERVER
# =======================================
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# target machine and port
serversocket.bind(('localhost', 8089))

# listen for one connection
serversocket.listen(1)
# ========================================

for i in range(5):
    
    # Accept connection and read message
    client, address = serversocket.accept()
    message = client.recv(2048).decode()

    # Print message
    print(message)
    
    worker().start()
    
    client.sendall("Hello from server".encode())

    # Close connections
    client.close()
    
serversocket.close()