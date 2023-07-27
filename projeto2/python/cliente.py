# -*- coding: utf-8 -*-
#@author: Rafox

#Importacao de bliotecas
import socket, random, threading

#Declaracao de variaveis globais
contador = 0
clienteON = True
armazanamentoLocal = {}
#armazanamentoLocal = {'erro':['erro','100000000000000']}#Força a uma informacao desatualizada no servidor

#Definicao de funcao do contador do timestemp
def timeStamp():
    global contador, servidorON
    while clienteON == True:
        contador += 1
    

#Definicao da funcao principal
def main():
    #Declaracoa das variaveis globais
    global contador, armazanamentoLocal
    #Inicializacao da thread do timestemp
    timestamp = threading.Thread(target=timeStamp)
    timestamp.start()
    
    #Declaracao da lista que armazenara os servidores
    servidores = []
    #servidores = [('127.0.0.1',10097),('127.0.0.1',10098),('127.0.0.1',10099)]#Mantem os 3 servidores locais com as postas padoes
    
    
    while True:
        #Opcoes de entrada do cliente
        entrada1 = int(input("\nQual ação deseja tomar?\n1 -> Adicionar servidores\n2 -> Inserir dados no sistema\n3 -> Pegar dados do servidor\nSua escolha > "))
        
        #Condicao para adicionar servidores a lista de servidores que o cliente conhece
        if entrada1 == 1:
            while True:
                entrada2 = int(input("\nVocê deseja adicionar IP/Porta de servidor?\n1 -> Sim\n2 ->Não\nEscolha >"))
                if entrada2 == 1:
                    ip = input("\nDigite o IP do servidor > ")
                    port = int(input("Digite a porta do servidor > "))
                    servidores.append((ip,port))
                elif entrada2 == 2:
                    if len(servidores) == 0:
                        print("\nPor favor, insira pelo menos 1 servidor.")
                    else:
                        break
                else:
                    print("\nPor favor, digite algo válido.")
        
        #Condicao para fazer requisicoes PUT ao servidor
        elif entrada1 == 2:
            #Inicializacao do socket para conexao e entradas de key e value
            coneccao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            key = input("\nDigite a chave >")
            valor = input("\nDigite o valor >")
            
            #Se conecta de forma aleatória com um dos servidores
            serv = (random.randrange(1,100))%len(servidores)
            coneccao.connect(servidores[serv])
            #Formatacao da mensagem
            msg = f"PUT;{key}:{valor};{contador}"
            #Envia mensagem
            coneccao.send(msg.encode())
            #Espera resposta do servidor
            res = coneccao.recv(1024).decode()
            res = res.split(";")
            #Se receber o PUT_OK, armazena a Key e Value com o timestemp do servidor lider, que o cliente não conhece
            if res[0] == "PUT_OK":
                armazanamentoLocal[key] = [valor, res[1]]                
                print(f"PUT_OK key: {key} value {valor} timestamp {res[1]} realizada no servidor {servidores[serv][0],servidores[serv][1]}")
            
            coneccao.close()
        
        #Condicao para fazer a requisicao GET
        elif entrada1 == 3:
            #Inicializacao do socket para conexao e entrada da key
            coneccao = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            key = input("\nDigite a chave >")
            
            #Se conecta de forma aleatória com um dos servidores
            serv = (random.randrange(1,100))%len(servidores)
            coneccao.connect(servidores[serv])
            
            #Se a key já está salva localmente, envia o timestemp associado a ela
            if key in armazanamentoLocal:
                tempK = armazanamentoLocal[key][1]
            
            #Se não envia 0
            else:
                tempK = 0
            
            #Formatacao da mensagem
            msg = f"GET;{key};{tempK}"
            #Envia mensagem
            coneccao.send(msg.encode())
            #Espera resposta do servidor
            res = coneccao.recv(1024).decode()
            
            #Resposta cosa o servidor possua uma chave com valor de timestemp menor que o do cliente
            if res == "TRY_OTHER_SERVER_OR_LATER":
                print(res)
            
            #Armazenamento e apresentação da resposta do servidor
            else:
                res = res.split(";")
                print (f"GET key: {res[0]} value: {res[1]} obtido do servidor {servidores[serv][0],servidores[serv][1]}, meu timestamp {contador} e do servidor {res[2]}")
                armazanamentoLocal[key] = [res[1],res[2]]
            
            coneccao.close()
        
        else:
            print("Por favor, digite um valor válido")

main()