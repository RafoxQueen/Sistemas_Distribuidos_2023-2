#Servidor
import socket

s = socket.socket()
print("Socket succefully created")
port = 9000

s.bind(("", port))
print("socket binded to %s"%(port))

s.listen(5)
print("Socket is listening")

while True:
	c, addr = s.accept()
	print("Got connection from ", addr)
	c.send("Thank you for connectig".encode())
	c.close()
	
	break
