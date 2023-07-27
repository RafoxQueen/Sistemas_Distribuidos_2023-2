# -*- coding: utf-8 -*-
#@author: Rafox

#Importando bibliotecas
import socket, threading

#Definido variaveis globais do sistema
contador = 0
servidorON = True
sLider = False
armazanamentoLocal = {}
servidores = []
#servidores = [('127.0.0.1',10097),('127.0.0.1',10098),('127.0.0.1',10099)]
servLider = 0

#Funcao responsavel por definir o timestamp do servidor, é um contador
def timeStamp():
    global contador, servidorON
    while servidorON == True:
        contador += 1

#Função responsável por tratar as requisicoes
def aceitarConexao(c,addr):
    #Identificando as variaveis globais
    global contador,sLider,servidores
    while True:
        try:
            #Espera requisicao do cliente
            msg = c.recv(1024).decode()
            #Trata e formata a requisicao entregue
            msg = msg.split(";")
            
            #Tratamento de uma requisicao PUT
            if msg[0] == "PUT":
                #Se o servidor não for lider, encaminha a mensagem de PUT para o lider
                if sLider == False:
                    repassa(msg,c,addr)
                
                #Se o servidor é lider comeca a tratar a requisicao
                else:
                    #Armazena a chave localmente
                    dado = msg[1].split(":")
                    armazanamentoLocal[dado[0]] = [dado[1], contador]
                    print(f"Cliente {addr[0]}:{addr[1]} PUT key:{dado[0]} value:{dado[1]}")
                    repOK = 0
                    
                    #Loop para fazer a replicacao da informacao para os outros servidores da rede
                    for serv in servidores:
                        if not(serv[0] == servLider[0] and serv[1] == servLider[1]):
                            coneccao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            coneccao.connect(serv)
                            rep = f"REPLICATION;{msg[1]};{armazanamentoLocal[dado[0]][1]}"
                            coneccao.send(rep.encode())
                            res = coneccao.recv(1024).decode()
                            if res == "REPLICATION_OK":
                                repOK += 1
                                coneccao.close()
                    
                    #Se todos os servidores já tiverem com a nova informacao, responde com PUT_OK a quem fez a requisicao
                    if repOK == len(servidores)-1:
                        print(f"Enviando PUT_OK ao Cliente {addr[0]}:{addr[1]} da key:{dado[0]} ts:{contador}")
                        res = f"PUT_OK;{armazanamentoLocal[dado[0]][1]}"
                        c.send(res.encode())
                            
            #Tratamento de uma requisicao REPLICATION
            elif msg[0] == "REPLICATION":
                #Armazena os dados localmente
                dado = msg[1].split(":")
                armazanamentoLocal[dado[0]] = [dado[1], msg[2]]
                print(f"REPLICATION key:{dado[0]} value:{dado[1]} ts:{msg[2]}")
                #Responde ao servidor com REPLICATION_OK
                res = "REPLICATION_OK"
                c.send(res.encode())
                
            #Tratamento de uma requisicao GET
            elif msg[0] == "GET":
                if msg[1] in armazanamentoLocal:
                    #Se a chave existe, e seu timestemp é maior que a do cliente , responde com o valor armazenado no servidor
                    if int(armazanamentoLocal[msg[1]][1]) >= int(msg[2]):
                        res = f"{msg[1]};{armazanamentoLocal[msg[1]][0]};{armazanamentoLocal[msg[1]][1]}"
                        print(f"Cliente {addr[0]}:{addr[1]} GET key:{msg[1]} ts:{msg[2]}. Meu ts é {armazanamentoLocal[msg[1]][1]}, portanto devolvendo {armazanamentoLocal[msg[1]][0]}")
                        c.send(res.encode())
                    
                    #Se o timestemp associado a chave for menor que a do cliente, responde TRY_OTHER_SERVER_OR_LATER
                    else:
                        res = "TRY_OTHER_SERVER_OR_LATER"
                        print(f"Cliente {addr[0]}:{addr[1]} GET key:{msg[1]} ts:{msg[2]}. Meu ts é {armazanamentoLocal[msg[1]][1]}, portanto devolvendo {res}")
                        c.send(res.encode())
                
                #Se a chave não existe localmente, responde como NULL
                else:
                    print(f"Cliente {addr[0]}:{addr[1]} GET key:dado[0] ts:{msg[2]}. Não há registro dessa chave, devolvendo NULL")
                    #Condicao para usar o timestemp do servidor lider
                    if not(sLider):
                        coneccao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        coneccao.connect(servLider)
                        #Encaminhando requisicao PUT
                        rep = "TIMESTEMP"
                        coneccao.send(rep.encode())
                        #Esperando resposta do servidor
                        timeL = coneccao.recv(1024).decode()
                        coneccao.close()
                    else:
                        #Usa timestemp local se for o lider
                        timeL = contador
                        
                    res = f"{msg[1]};NULL;{timeL}"
                    c.send(res.encode())
                    
            elif msg[0] == "TIMESTEMP":
                res = f"{contador}"
                c.send(res.encode())
                
        except:
            #Caso ocorra um problema na conexao entre o Cliente e o Servidor, encerra o while e a thread
            break

#Funcao responsavel por repassar a mesagem para o lider
def repassa(msg,c,addr):
    #Definicao de variaveis globais
    global servLider, contador
    #Criacao do socket e conexao com o lider
    coneccao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    coneccao.connect(servLider)
    dado = msg[1].split(":")
    #Encaminhando requisicao PUT
    print(f"Encaminhando PUT key:{dado[0]} value:{dado[1]} ")
    rep = f"PUT;{msg[1]};{contador}"
    coneccao.send(rep.encode())
    #Esperando resposta do servidor
    msg = coneccao.recv(1024).decode()
    msg = msg.split(";")
    if msg[0] == "PUT_OK":
        #Se recebeu PUT_OK, responde ao cliente que houve PUT_OK
        res = f"{msg[0]};{msg[1]}"
        c.send(res.encode())
        coneccao.close()


#Função principal do servidor
def main():
    #Define variaveis globais
    global contador, servidorON,sLider, servidores, servLider
    #Thread para o contador do timestemp
    timestamp = threading.Thread(target=timeStamp)
    timestamp.start()
    
    #Inicializacao do servidor
    ipP = input("Insira o IP deste servidor > ")
    portP = int(input("Insira a porta deste servidor > "))
    servidores.append((ipP,portP))
    
    ipL =  input("Insira o IP do lider > ")
    portL = int(input("Insira a porta do lider > "))
    
    servLider = (ipL, portL)
    
    if ipP == ipL and portP == portL:
        sLider = True
    #Se é lider, prescisa conhecer os outros servidores da rede para replicar informacao
    while sLider == True:
        entrada = int(input("\nVocê deseja adicionar outros servidores?\n1 -> Sim\n2 -> Não\nSua escolha > "))
        if entrada == 1:
            ip = input("\nDigite o IP do servidor > ")
            port = int(input("Digite a porta do servidor > "))
            servidores.append((ip,port))
        elif entrada == 2:
            break
        
        else:
            print("Digite um valor valido.")
            
    #Criando socket para receber requisicoes
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ipP, portP))
    s.listen(25)
    
    while True:
        #Tratamento das conexoes
        c, addr = s.accept()
        
        #Criar e iniciar thread para a conexao
        aceita_thread = threading.Thread(target=aceitarConexao, args=[c, addr])
        aceita_thread.start()
    

main()