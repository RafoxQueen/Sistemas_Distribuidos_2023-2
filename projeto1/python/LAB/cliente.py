import socket, threading, os

s = socket.socket()
print("Socket succefully created")
port = 9000

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
            	msg = c.recv(1024).decode()
            	print(msg)
            	if msg == "Encerrando conexão":
                	c.close()
                	return "a"
        except:
            return

aceitarConexao(s)
