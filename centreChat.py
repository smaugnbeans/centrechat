

#Jean VanNoppen
#Kaitlyn McKnight
#CentreChat protocol
from socket import *
import select
import time

#creates the client
class chatClient:
	posts = []


	#client constructor 
	def __init__(self, name, port, handle):
		print "client created"
		self.handle = handle
		self.serverName = name 
		self.serverPort = port
		self.clientSocket = socket(AF_INET, SOCK_DGRAM)
		self.clientSocket.bind( ("",0))
		self.myAddress = ("127.0.0.1", self.clientSocket.getsockname()[1])
		self.message1 = "Message-Type: Connect"+"\n"+"Handle: "+handle+"\n"+"\r\n"
		self.clientSocket.sendto(self.message1, (self.serverName, self.serverPort))
		time.sleep(1)


	#master while loop
	def handleMessages(self):
		self.state = "ACK"
		while (True):
			if (self.state=="ACK"):
				self.state = self.handleACK()
			if (self.state=="WAIT"):
				self.state = self.mainWait()
			if (self.state == "DONE"):
				return


	#send message to the server
	def sendMessage(self, msg):
		#need sequence number
		message = "Message-Type: Post"+"\n"+"Handle: "+self.handle+"\n"+"\r\n"+msg
		self.clientSocket.sendto(message, self.myAddress)
		print "client send to self: "+message
		#return


	#get messages recv from server
	def getMessages(self):
		return self.posts



	#wait for user input or server message
	def mainWait(self):
		self.clientSocket.setblocking(0)
		ready = select.select([self.clientSocket], [], [], 100)
		if ready[0]:
			message, serverAddress = self.clientSocket.recvfrom(2048)
			packet = message.find("\r\n")
			header = message[0:packet+2]
			messageType = header.find('Message-Type: ')
			tempEndLine = header.find('\n', messageType)#finds index e end of line
			pktType = header[messageType+14:tempEndLine]#gets lttrs btwn :and\n
			name = header.find("Handle: ")
			name = name+16
			tempEnd = header.find('\n', name)
			tempEnd = tempEnd - 2
			if pktType == "Disconnect":
				message="Message-Type: Disconnect"+"\n"+"Handle: "+self.handle+"\n"+"\r\n"
				self.clientSocket.sendto(message, (self.serverName, self.serverPort))
				return "ACK"
			if pktType == "Post":
				data = message[packet+2:]
				print "pkt Data: "+data
				self.posts.append(data)
				handleFrom = header[name-8:tempEnd]
				if (handleFrom == self.handle):
					self.clientSocket.sendto(message, (self.serverName, self.serverPort))
				else:
					msg = "Message-Type: Acknowledge-Post"+"\n"+"Handle: "+self.handle+"\n"+"\r\n"
					self.clientSocket.sendto(msg, (self.serverName, self.serverPort))
				return "WAIT"





	#wait for ack
	def handleACK(self):
		print "WAIT FOR ACK FUNC"
		self.clientSocket.setblocking(0)
		ready = select.select([self.clientSocket], [], [], 100)
		if ready[0]:
			print "client wait for ack"
			message, serverAddress = self.clientSocket.recvfrom(2048)
			packet = message.find("\r\n")
			header = message[0:packet+2]
			messageType = header.find('Message-Type: ')
			tempEndLine = header.find('\n', messageType)#finds index e end of line
			pktType = header[messageType+14:tempEndLine-1]#gets lttrs btwn :and\n
			print pktType+"E"
			if pktType == "Acknowledge-Connect":#stop timer?
				print "client recv CONNECT ACK from server"
				return "WAIT" 
			if pktType == "Acknowledge-Disconnect":
				print message + "client recv DISCONNECT ACK"
				self.clientSocket.close()
				return "DONE"
			if pktType == "Acknowledge-Post":
				print message + "client recv POST ACK"
				return "WAIT" 


		else:
			#self.clientSocket.sendto(self.message1, (self.serverName, self.serverPort))
			return "ACK"
		


	#leave server
	def disconnect(self):
		message="Message-Type: Disconnect"+"\n"+"Handle: "+self.handle+"\n"+"\r\n"
		self.clientSocket.sendto(message, self.myAddress) #sends disconnect to self
		return

		

	
		




#creates the chat server
class chatServer:
	#need both ip address and port num??(tuple address)
	clients = {}
	messages = []

	#server constructor 
	def __init__(self):
		self.serverPort = 12000			  #once get message, 
		self.serverSocket = socket(AF_INET, SOCK_DGRAM)#then bind client
		self.serverSocket.bind(('', self.serverPort))	  #to specified server?


	#returns list of clients
	def getClients(self):
		return self.clients


	#adds client to list
	def addClient(self, string, clientAddress):
		print "server ADD client"
		#self.clients.append(string)
		self.clients[string] = clientAddress


	#only state,listens
	def listening(self):
		while 1:
			#while(self.serverSocket.recvfrom(2048)):
			print "server LISTENING for packet"
			message, clientAddress = self.serverSocket.recvfrom(2048)
			packet = message.find("\r\n")
			header = message[0:packet+2]
			messageType = header.find('Message-Type: ')
			tempEndLine = header.find('\n', messageType)#finds index e end of line
			pktType = header[messageType+14:tempEndLine]#gets lttrs btwn :and\n
			name = header.find("Handle: ")
			name = name+16
			tempEnd = header.find('\n', name)
			tempEnd = tempEnd - 2
			handle = header[name-8:tempEnd]
			if pktType == "Connect":
				print "server recv CONNECT  pkt"
				
				#print "handle: " + handle
				self.addClient(handle, clientAddress)
				self.makePacket('Acknowledge-Connect', clientAddress, handle)
			
			if pktType == "Disconnect":
				print "server recv DISCONNECT pkt"
				#print handle
				self.makePacket('Acknowledge-Disconnect', clientAddress, handle)
				self.removeClient(handle)

			if pktType == "Post":
				time.sleep(2)
				print "server recv POST pkt"
				self.makePacket('Acknowledge-Post', clientAddress, handle)
				time.sleep(2)
				data = message[packet+2:]
				self.messages.append(data)
				self.broadcastMessage(message)



	#return all the messages from the clients
	def getAllMessages(self):
		return self.messages

	#removes client from list, client closes socket
	#@peram: client handle name
	def removeClient(self, handle):
		del self.clients[handle]
		

	def broadcastMessage(self, pkt):
		print "pkt post: "+pkt
		adds = self.clients.values()
		print adds
		for i in adds:
			self.serverSocket.sendto(pkt, i)

	#Makes and sends the packets
	#@peram: packet type, and client address
	def makePacket(self,typePkt, clientAddress, handle):
		if typePkt=="Acknowledge-Connect":
			print "server made CONNECT ACK"
			message = "Message-Type: Acknowledge-Connect "+"\n"+"\r\n"
			self.serverSocket.sendto(message, clientAddress)
		if typePkt=="Acknowledge-Disconnect":
			print "server made DISCONNECT ACK"
			message = "Message-Type: Acknowledge-Disconnect "+"\n"+"\r\n"
			self.serverSocket.sendto(message, clientAddress)
		if typePkt == "Acknowledge-Post":
			print "server made POST ACK"
			message = "Message-Type: Acknowledge-Post "+"\n"+"Handle: "+handle+"\n"+"\r\n"
			print message
			self.serverSocket.sendto(message, clientAddress)
			






