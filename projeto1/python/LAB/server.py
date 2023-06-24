#Servidor
import socket, threading

diretorio = "../teste/"
with open(diretorio+"test.txt", "w") as arquivo:
    text = arquivo.write("")

def main():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 1099
        
        s.bind(("", port))
        s.listen(5)
        
    except:
        print("\n Não foi possivel criar servidor")
        
    while True:
        c, addr = s.accept()
        
        #aceitarConexao(c, addr)
        
        aceita_thread = threading.Thread(target=aceitarConexao, args=[c, addr])
        aceita_thread.start()


def gravaDados(arqvs,addr,pasta=diretorio):
    data = ""
    arqvs = arqvs.split(":")
    porta = arqvs[0]
    data = arqvs[1]
    
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
        try:
            data = linha.split(";")
            arquivos[data[0]] = data[1].split(",")
        except:
            arquivos["erro"] = linha

    arq=""+arq

    for chave, valor in arquivos.items():
        if arq in valor:
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
        

def aceitarConexao(c, addr):
    while True:
        try:
            msg = c.recv(2048).decode()
            msg = msg.split(";")
            if msg[0] == "JOIN":
                if msg[-1] == "fim":
                    arquivos = msg[1]
                    gravaDados(arquivos,addr)
                    c.send("JOIN_OK".encode())
                
            elif msg[0] == "SEARCH":
                arquivo = msg[1]
                if msg[-1]=="fim":
                    print(f"Peer {addr[0]}:{addr[1]} solicitou arquivo {arquivo}")
                    ips = pesquisaDados(arquivo)
                    c.send(ips.encode())

                
            elif msg[0] == "UPDATE":
                arquivo = msg[1]
                if msg[-1]=="fim":
                    porta = msg[2]
                    atualizaDados(arquivo,addr,porta)
                    c.send("UPDATE_OK".encode())
                
            else:
                c.send("Reenvie a mensagem".encode())
        except:
            break


main()
