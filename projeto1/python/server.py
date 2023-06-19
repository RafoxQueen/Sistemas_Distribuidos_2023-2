#Servidor
import socket, threading, sys

clientes = []

def main():
    try:
        s = socket.socket()
        print("Socket succefully created")
        port = 9009

        s.bind(("", port))
        print("socket binded to %s"%(port))

        s.listen(5)
        print("Socket is listening")
    except:
        print("\n Não foi possivel criar servidor")
        
    while True:
        c, addr = s.accept()
        
        print("Got connection from ", addr)
        c.send("Thank you for connectig".encode())
        clientes.append(c)
        
        print("TRead")
        aceita_thread = threading.Thread(target=aceitarConexao, args=[c])
        aceita_thread.start()


def aceitarConexao(c):
    while True:
        try:
            msg = c.recv(1024).decode()
            if msg == "Encerrar2":
                return "a"
            else:
                print(msg)
        except:
            return "delete"

	
main()