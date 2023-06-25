# -*- coding: utf-8 -*-
#@author: Rafox

#Projeto de Programação – Napster com Sockets em Python

#Cliente

#Importacao de bibliotecas
import socket, threading, os

print("Olá, seja bem vindo!!")

#definicao de constante para mantes o sistema e threads funcionando
serverOn = True


def main():
    while True:
        #Criacao do menu do console
        operacao = int(input("\nDigite a operação que deseja fazer:\n1 - JOIN\n2 - SEARCH\n3 - DOWNLOAD\nEscolha> "))
        
        #Opcao para fazer JOIN no servidor
        if operacao == 1:
            #Criacao do socket
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                #Definicao de variaveis importantes para a conecao
                #IP do servidor
                ip = input("/nPor favor, digite o IP do servidor para conexão> ")
                #Porta do servidor
                port = int(input("Insira o número da porta(a padrão é 1099)> "))
                #Porta de esculta do cliente para outros Peers
                portaServ = int(input("Digite a porta de conexão a esta máquina> "))
                print("Se estiver no windows use \\\ para representar os diretórios, para uma pasta anterior a desse arquivo (../) ou (../Pasta_desejada)")
                print("Não se esqueça de colocar \\\ ou / apos o nome do último diretório")
                #Diretorio onde sera verificado a presensa de arquivos e para Download
                diretorioD = input("Digite o diretório para armazenar arquivos compartilhaveis> ")
                
                #Conecta-se ao servidor
                server.connect((ip, port))
                
                #Preparacao da requisicao para o servidor
                msg = ""
                #Informa a requisicao JOIN e a porta que o Peer recebe requisicao
                ip_conec = f"JOIN;{portaServ}:"
                #Lista arquivos no diretorio informado
                arquivos = os.listdir(diretorioD)
                
                #Formata arquivos para envio na requisicao
                for arquivo in arquivos:
                    msg += f"{arquivo},"
                
                arquivos = msg
                #Adiciona a informacao de que foi enviado a mensagem completa
                msg = ip_conec + msg + ";fim"
                
                #Envia mensagem
                server.send(msg.encode())
                
                #Espera resposta do servidor
                res = server.recv(1024).decode()
                
                #Se a conexao foi bem sucedida informa ao usuario
                if res == "JOIN_OK":
                    ip_local = server.getsockname()[0]
                    print(f"\nSou peer {ip_local}:{portaServ} com arquivos {arquivos}")
                
                #Inicia thread responsavel pelo servidor do Peer
                server_thread = threading.Thread(target=servDownload, args=[portaServ,diretorioD])
                server_thread.start()
                
            except:
                #Informa se houve algum erro no processo para fazer o JOIN
                print("Erro no JOIN")
        
        #Condicao para fazer requisicao SEARCH
        elif operacao == 2:
            #Pede o nome do arquivo
            arq = input("\nInsira o nome do arquivo com a extenção do mesmo> ")
            #Formatacao e envio da requisicao
            msg = f"SEARCH;{arq};fim"
            server.send(msg.encode())
            #Espera da resposta do servidor
            res = server.recv(1024).decode()
            #Informa ao usuario quais IP:Porta tem o arquivo
            print(f"\nPeers com arquivo solicitado: {res}")
        
        #Condicao para fazer a requisicao de DOWNLOAD
        elif operacao == 3:
            #Cria socket para se comunicar com outro peer
            peer = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            #Variaveis contendo dados do peer a ser conectado
            ip = input("Por favor, digite o IP do Peer para conexão> ")
            portaPeer = int(input("\nDigite a porta de conexão do Peer> "))
            
            #Faz conexao com outro peer
            peer.connect((ip, portaPeer))
            #Formata e envio da requisicao de pedido com o arquivo informado ao fazer a requisicao SEARCH
            msg = f"DOWNLOAD;{arq};fim"
            peer.send(msg.encode())
            
            #Prepara para o download do arquivo
            with open(diretorioD+arq, 'wb') as file:
                #Loop para receber os bytes do arquivo
                while True:
                    #Recebe pacotes do servidor
                    data = peer.recv(1000000)
                    #Condicao se não houver mais bytes
                    if not data:
                        #Informa que o arquivo foi baixado
                        print(f"Arquivo {arq} baixado com sucesso na pasta diretorioD")
                        
                        #Formataco e envio da requisicao UPDATE ao servidor
                        msg = f"UPDATE;{arq};{portaServ};fim"
                        server.send(msg.encode())
                        #Espera a resposta do servidor
                        res = server.recv(1024).decode()
                        #Se nao receber um UPDATE_OK reenvia a mensagem para o servidor
                        while res != "UPDATE_OK":
                            server.send(msg.encode())
                            res = server.recv(1024).decode()
                        
                        break
                    #Escreve o que foi recebido no arquivo local
                    file.write(data)
            
        #Opcao oculta para desligar o Peer
        elif operacao == 4:
            print("\nDesligando programa")
            server.close()
            global serverOn
            serverOn = False
            break
        
        #Condicao para informar ao usuario que foi digitado algo invalido
        else:
            print("Por favor, digite algo válido")
        
    
#Funcao responsavel pela creacao do servidor de UPLOAD no Peer
def servDownload(porta, diretorio):
    #Tenta criar servidor
    try:
        #Definicao do socket
        servUp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        #Inicia esculta do servidor
        servUp.bind(("", porta))
        servUp.listen(5)
        
        #Loop para aceitar as requisicoes
        while serverOn:
            c, addr = servUp.accept()
            #Recebimento e tratamento da mensagem recebida
            msg = c.recv(1024).decode()
            msg = msg.split(";")
            #Se for requisicao de DOWNLOAD prepara para o envio
            if msg[0] == "DOWNLOAD":
                arquivo = msg[1]
                #Criacao de thread para o envio do arquivo solicitado
                upload_thread = threading.Thread(target=uploadServ, args=[c, addr, arquivo,diretorio])
                upload_thread.start()

    #Informa se ouve problema na criacao do servidor
    except:
        print("\n Não foi possivel criar servidor")
        
#Funcao responsavel por enviar arquivos solicitados
def uploadServ(c,addr,arquivo, diretorio):
    #Lista os arquivos do direorio do Peer
    arquivos = os.listdir(diretorio)
    #Verifica se o arquivo existe no Peer
    if arquivo in arquivos:
        #Leitura e envio das informacoes presentes no arquivo solicitado
        with open(diretorio+arquivo, "rb") as uploadArquivo:
            for data in uploadArquivo.readlines():
                c.send(data)
                
            c.close()

#Chamada de funcao main iniciando o programa
main()