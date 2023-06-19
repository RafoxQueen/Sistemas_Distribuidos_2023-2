import socket, threading, sys

s = socket.socket()
print("Socket succefully created")
port = 9009

s.connect(("127.0.0.1", port))

print(s.recv(1024).decode())

def aceitarConexao(c):
    while True:
        try:
            text = input("text: ")
            msg = c.send(text.encode())
            if msg == "Encerrar2":
                s.closer()
            else:
                print(msg)
        except:
            return

aceitarConexao(s)