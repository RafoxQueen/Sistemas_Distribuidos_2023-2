import socket, threading, os

print("Olá, seja bem vindo!!")

serverOn = True

def main():
    while True:
        operacao = int(input("\nDigite a operação que deseja fazer:\n1 - JOIN\n2 - SEARCH\n3 - DOWNLOAD\nEscolha> "))
        
        if operacao == 1:
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
            
                #ip = input("Por favor, digite o IP do servidor para conexão> ")
                #port = int(input("Insira o número da porta> "))
            
                portaServ = int(input("\nDigite a porta de conexão a esta máquina> "))
                print("Se estiver no windows use \\ para representar os diretórios, para uma pasta anterior a desse arquivo (../) ou (../Pasta_desejada)")
                print("Não se esqueça de colocar \\ ou / apos o nome do último diretório")
                diretorioD = input("Digite o diretório para armazenar arquivos compartilhaveis> ")
                
                ip = "127.0.0.1"
                port = 1099
                #portaServ = 9123
                #diretorioD = "B:\\test"
                
                server.connect((ip, port))
                
                msg = ""
                ip_conec = f"JOIN;{portaServ}:"
                
                arquivos = os.listdir(diretorioD)
                
                for arquivo in arquivos:
                    msg += f"{arquivo},"
                
                arquivos = msg
                
                msg = ip_conec + msg + ";fim"
                server.send(msg.encode())

                res = server.recv(1024).decode()
                if res == "JOIN_OK":
                    ip_local = server.getsockname()[0]
                    print(f"\nSou peer {ip_local}:{portaServ} com arquivos {arquivos}")
                
                server_thread = threading.Thread(target=servDownload, args=[portaServ,diretorioD])
                stop_event = threading.Event()
                server_thread.start()
                
                
            except:
                print("Erro no JOIN")
                
        elif operacao == 2:
            arq = input("\nInsira o nome do arquivo com a extenção do mesmo> ")
            msg = f"SEARCH;{arq};fim"
            server.send(msg.encode())
            res = server.recv(1024).decode()
            print(f"\npeers com arquivo solicitado: {res}")
            
        elif operacao == 3:
            peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            ip = input("Por favor, digite o IP do Peer para conexão> ")
            portaPeer = int(input("\nDigite a porta de conexão do Peer> "))
            
            peer.connect((ip, portaPeer))
            msg = f"DOWNLOAD;{arq};fim"
            peer.send(msg.encode())
            
            with open(diretorioD+arq, 'wb') as file:
                while True:
                    data = peer.recv(1000000)
                    if not data:
                        msg = f"UPDATE;{arq};{portaServ};fim"
                        server.send(msg.encode())
                        res = server.recv(1024).decode()
                        while res != "UPDATE_OK":
                            server.send(msg.encode())
                            res = server.recv(1024).decode()
                        
                        break
                    file.write(data)
            
            
        elif operacao == 4:
            print("\nDesligando programa")
            server.close()
            global serverOn
            serverOn = False
            break
        
        else:
            print("Por favor, digite algo válido")
        
    

def servDownload(porta, diretorio):
    try:
        servUp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = porta
        
        servUp.bind(("", port))
        servUp.listen(5)
        
    except:
        print("\n Não foi possivel criar servidor")
        
    while serverOn:
        c, addr = servUp.accept()
        
        msg = c.recv(1024).decode()
        msg = msg.split(";")
        if msg[0] == "DOWNLOAD":
            arquivo = msg[1]
            upload_thread = threading.Thread(target=uploadServ, args=[c, addr, arquivo,diretorio])
            upload_thread.start()
            
    servUp.close()
        
def uploadServ(c,addr,arquivo, diretorio):
    arquivos = os.listdir(diretorio)
    if arquivo in arquivos:
        with open(diretorio+arquivo, "rb") as uploadArquivo:
            for data in uploadArquivo.readlines():
                c.send(data)
                
            c.close()
                
main()