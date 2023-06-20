#Servidor
import socket, threading, os

clientes = []

def main():
    try:
        s = socket.socket()
        port = 9000
        
        s.bind(("", port))
        s.listen(5)
        
    except:
        print("\n Não foi possivel criar servidor")
        
    while True:
        c, addr = s.accept()
        
        print("Got connection from ", addr)
        
        c.send("Thank you for connectig".encode())
        
        clientes.append(c)
        
        aceita_thread = threading.Thread(target=aceitarConexao, args=[c])
        aceita_thread.start()


def aceitarConexao(c):
    while True:
        try:
            msg = c.recv(1024).decode()
            
            if msg == "JOIN":
            	c.send("JOIN_OK".encode())
            
            elif msg == "SEARCH":
            	c.send("Arquivos".encode())
            	
            elif msg == "UPDATE":
            	c.send("UPDATE_OK".encode())
            	
            else:
                c.send("Encerrando conexão".encode())
                c.close()
        except:
            c.close()

	
main()
