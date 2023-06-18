import socket

s = socket.socket()
print("Socket succefully created")
port = 9000

s.connect(("10.9.0.10", port))

print(s.recv(1024).decode())

s.close()
