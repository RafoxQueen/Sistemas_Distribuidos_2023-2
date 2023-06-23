#Servidor
import socket, threading, os

diretorio = "../teste/"

def main():
    conec = {}
    try:
        s = socket.socket()
        port = 1099
        
        s.bind(("", port))
        s.listen(5)
        
    except:
        print("\n Não foi possivel criar servidor")
        
    while True:
        c, addr = s.accept()
        
        c.send("Thank you for connectig".encode())
        
        aceitarConexao(c, addr, conec)
        
        #aceita_thread = threading.Thread(target=aceitarConexao, args=[c, addr, conec])
        #aceita_thread.start()


def gravaDados(arqvs,addr,porta,pasta=diretorio):
    data = ""
    for arq in arqvs:
        data += (arq+",")
    
    print(f"Peer {addr[0]}:{addr[1]} adicionado com arquivos {data}")
    conec = f"{addr[0]}:{porta}"
    data = conec +";"+data
    data += "\n"
    with open(pasta+"test.txt", "a") as arquivo:
        text = arquivo.write(f"{data}")


def pesquisaDados(arq, pasta=diretorio):
    arquivos = {}
    chaves = []
    
    with open(pasta+"test.txt", "r") as arquivo:
        linhas = arquivo.readlines()
    
    for linha in linhas:
        data = linha.split(";")
        arquivos[data[0]] = data[1].split(",")
    
    for chave, valor in arquivos.items():
        if str(arq) in str(valor):
            print(chave)
            chaves.append(chave)
    
    return str(chaves)

def atualizaDados(arq, addr, porta,pasta=diretorio):
    with open(pasta+"test.txt", "r") as arquivo:
        linhas = arquivo.readlines()
    
    for linha in linhas:
        if f"{addr[0]}:{porta}" in linha:
            mod = (linhas.index(linha))
    
    modLinha = linhas[mod]
    separa = modLinha.split(";")

    separa[1] = separa[1].split(",")
    if not(arq in separa[1]):
        separa[1][-1] = arq
        arq = ""
    
        for partes in separa[1]:
            arq += partes+','
        arq +="\n"
        novaLinha = f"{separa[0]};{arq}"
        linhas[mod] = novaLinha
            
        with open(pasta+"test.txt", "w") as arquivo:
            linha = arquivo.writelines(linhas)
        

def aceitarConexao(c, addr, conec):
    while True:
        try:
            msg = c.recv(1024).decode()
            
            if msg == "JOIN":
                arquivos = []
                c.send("A".encode())
                porta = c.recv(1024).decode()
                while True:
                    c.send("A".encode())
                    msg = c.recv(1024).decode()
                    if msg == "___":
                        conec[addr] = arquivos
                        c.send("JOIN_OK".encode())
                        gravaDados(arquivos,addr,porta)
                        break
                    else:
                        arquivos.append(msg)
                c.close()
                
            elif msg == "SEARCH":
                c.send("A".encode())
                arquivo = c.recv(1024).decode()
                print(f"Peer {addr[0]}:{addr[1]} solicitou arquivo {arquivo}")
                ips = pesquisaDados(arquivo)
                c.send(ips.encode())
                c.close()
                
            elif msg == "UPDATE":
                c.send("A".encode())
                arquivo = c.recv(1024).decode()
                c.send("A".encode())
                porta = c.recv(1024).decode()
                atualizaDados(arquivo,addr,porta)
                c.send("UPDATE_OK".encode())
                
            elif msg == "Encerrar conexão":
                c.close()
                break
            else:
                c.send("Reenvie a mensagem".encode())
        except:
            c.close()
            break


main()
