# -*- coding: utf-8 -*-
#@author: Rafox

#Projeto de Programação – Napster com Sockets em Python

#Servidor

#Importação de bibliotecas
import socket, threading

#Definição do diretório onde ficara o arquivo com os registros dos Peers
entrada = input("Digite o local do diretório do registro do servidor> ")
diretorio = entrada+"servidor.txt"

#Criacao/limpesa do arquivo de registro
with open(diretorio, "w") as arquivo:
    text = arquivo.write("")

#Funcao principal para criacao do servidor
def main():
    try:
        #Criacao do socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        port = 1099
        
        #Iniciando a esculta do servidor
        s.bind(("", port))
        s.listen(5)
        
    except:
        #Mensagem de erro
        print("\n Não foi possivel criar servidor")
        
    while True:
        #Aceita conexão vinda de um Peer
        c, addr = s.accept()
        
        #Criar e iniciar thread para a conexao
        aceita_thread = threading.Thread(target=aceitarConexao, args=[c, addr])
        aceita_thread.start()

#Funcao para armazenar os dados dos Peers
def gravaDados(arqvs,addr,pasta=diretorio):
    #Tratamento da entrada dos dados do Peer
    arqvs = arqvs.split(":")
    porta = arqvs[0]
    data = arqvs[1]
    
    #Print no servifor informando o JOIN do Peer
    print(f"Peer {addr[0]}:{addr[1]} adicionado com arquivos {data}")
    
    #Formatação dos dados do Peer
    conec = f"{addr[0]}:{porta}"
    data = conec +";"+data
    data += "\n"
    
    #Gravação dos dados no arquivo do servidor
    with open(pasta, "a") as arquivo:
        text = arquivo.write(f"{data}")


def pesquisaDados(arq, pasta=diretorio):
    arquivos = {}
    chaves = []
    
    #Leitura do arquivo de registro do servidor
    with open(pasta, "r") as arquivoS:
        linhas = arquivoS.readlines()
    
    #Formatação em forma de dicionário para evitar duplicidade nos dados
    for linha in linhas:
        try:
            data = linha.split(";")
            arquivos[data[0]] = data[1].split(",")
        except:
            arquivos["erro"] = linha
    
    #Busca pelo nome do arquivo pedido
    for chave, valor in arquivos.items():
        if arq in valor:
            chaves.append(chave)
    
    return str(chaves)

#Funcao para realizar as atualizações nos dados
def atualizaDados(arq, addr, porta,pasta=diretorio):
    #Leitura do arquivo do servidor
    with open(pasta, "r") as arquivo:
        linhas = arquivo.readlines()
    
    #Busca da linha corre ao Peer que solicitou atualizacao
    for linha in linhas:
        if f"{addr[0]}:{porta}" in linha:
            mod = (linhas.index(linha))
    
    #Pega linha correspondente ao Peer e formata para modificacao
    modLinha = linhas[mod]
    separa = modLinha.split(";")
    separa[1] = separa[1].split(",")
    
    #Busca se o arquivo a ser adicionado existe no Peer
    if not(arq in separa[1]):
        #Se não existe adiciona na ultima posição da lista, geralmente corresponde a \n vem de arquivo
        separa[1][-1] = arq
        
        #Esvasia a variavel para ser reutilizada
        arq = ""
        
        #Formatacao dos arquivos do Peer
        for partes in separa[1]:
            arq += partes+','
        arq +="\n"
        
        #Formatacao da configuracao do servidor do Peer com os arquivos
        novaLinha = f"{separa[0]};{arq}"
        linhas[mod] = novaLinha
            
        #Reescreve o arquivo de registro do servidor com a modificacao
        with open(pasta, "w") as arquivo:
            linha = arquivo.writelines(linhas)
        
#Funcao responsavel por tratar as requisicoes do servidor
def aceitarConexao(c, addr):
    while True:
        try:
            #Espera requisicao do Peer
            msg = c.recv(2048).decode()
            #Trata e formata a requisicao entregue
            msg = msg.split(";")
            
            #Condicao caso a requisicao inclua JOIN
            if msg[0] == "JOIN":
                #Verifica se a mesnagem está completa
                if msg[-1] == "fim":
                    #Definicao da variavel com os arquivos enviados
                    arquivos = msg[1]
                    #Chamada da funcao para fazer o registro no servidor
                    gravaDados(arquivos,addr)
                    #Envia confirmacao de que ouve o JOIN
                    c.send("JOIN_OK".encode())
                
            #Condicao caso a requisicao seja um SEARCH
            elif msg[0] == "SEARCH":
                #Verifica se a mesnagem está completa
                if msg[-1]=="fim":
                    #Definicao da variavel com o arquivo solicitado para pesquisa
                    arquivo = msg[1]
                    #Print no servidor sobre a solicitacao
                    print(f"Peer {addr[0]}:{addr[1]} solicitou arquivo {arquivo}")
                    
                    #Variavel que recebe de retorno da funcao pesquisaDados uma lista de IP:Porta
                    #que tem o arquivo socilitado
                    ips = pesquisaDados(arquivo)
                    
                    #Envio da lista
                    c.send(ips.encode())

            #Condicao caso a requisicao seja um UPDATE
            elif msg[0] == "UPDATE":
                #Verifica se a mesnagem está completa
                if msg[-1]=="fim":
                    #Formatacao das variaveis
                    arquivo = msg[1]
                    porta = msg[2]
                    #Chamada da funcao para fazer atualizacao no registro do servidor
                    atualizaDados(arquivo,addr,porta)
                    #Envio da confirmacao de que ocorreu o UPDATE
                    c.send("UPDATE_OK".encode())
                
            else:
                #Caso a requisicao venha errado envia erro para o Peer
                c.send("Reenvie a mensagem".encode())
        except:
            #Caso ocorra um problema na conexao entre o Peer e o Servidor, encerra o while e a thread
            break

#Chamada da funcao main
main()
