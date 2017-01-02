

#Jean VanNoppen
#Kaitlyn McKnight
#test connection for centreChat protocol
import centreChat
import thread
import time

#only need main
def main():
	S = centreChat.chatServer()
	port = 12000
	C = centreChat.chatClient("127.0.0.1", port, "Bill")
	thread.start_new_thread(S.listening,())
	print "started server thread from MAIN  " + "\n"


	thread.start_new_thread(C.handleMessages,())
	print "started client thread from MAIN" + "\n"

	time.sleep(2)
	
	print S.getClients()
	#assert(S.getClients()=={"Bill": "127.0.0.1"})
	
	C1 = centreChat.chatClient("127.0.0.1", port, "Sandy")
	thread.start_new_thread(C1.handleMessages,())
	time.sleep(2)
	#assert (S.getClients()==["Bill", "Sandy"])
	print S.getClients()
	"""
	C2 = centreChat.chatClient("127.0.0.1", port, "Bob")
	thread.start_new_thread(C2.handleMessages,())
	time.sleep(1)

	print S.getClients()
	assert(S.getClients()==["Bill", "Sandy", "Bob"])

	
	C.disconnect()
	time.sleep(1)
	print S.getClients()
	assert(S.getClients()==["Sandy", "Bob"])

	C1.disconnect()
	time.sleep(1)
	assert(S.getClients()==["Bob"])
	C2.disconnect()
	time.sleep(1)
	assert(S.getClients()==[])
	print S.getClients()"""
	
	

	time.sleep(2)
	C.sendMessage("HI IM PAUL")
	time.sleep(5)
	C1.sendMessage("fuckers")
	time.sleep(2)

	print "server: "
	print S.getAllMessages()
	print "client: "
	print C.getMessages()
	time.sleep(2)
	#assert (S.getAllMessages()==["HI IM PAUL"])









main()
