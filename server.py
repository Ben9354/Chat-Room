# Student Name: Benjamin Chung

from tkinter import *
from socket import *
import threading

class Gui:
    """
    This class implements the GUI for the server.
    It updates the chat history window with messages sent from each client.
    """
    def __init__(self, window, ChatServer):
        # Data fields for the window GUI
        self.window = window
        self.boxWidth = 55
        self.boxHeight = 15
        self.ChatServer = ChatServer
        self.launchGUI()

    # Creates the look of the GUI of the server applcation
    def launchGUI(self):
        
        # Title
        self.window.title("Server Application")
        
        # Labels
        self.serverLabel = Label(self.window, text = "Chat Server", anchor="w")
        self.serverLabel.pack(fill=X)
        self.historyLabel = Label(self.window, text = "Chat History:", anchor="w")
        self.historyLabel.pack(fill=X)
        
        # Creates text box for chat history
        self.historyBox = Text(self.window, height = self.boxHeight, width = self.boxWidth)
        self.historyBox.pack(fill=X, side=LEFT)
        self.historyBox.config(state=DISABLED)
        
        # Chat scrollbar
        self.scrollbar = Scrollbar(self.window, command=self.historyBox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.historyBox.config(yscrollcommand=self.scrollbar.set)
        
        # Private field to determine if server closes
        self.__closed = False
        self.window.protocol("WM_DELETE_WINDOW", self.close)
    
    # Method for updating the chat history box when a message is received
    def recievedMessage(self, message):
        
        # Display message from clients with automatic scroll down
        self.historyBox.config(state=NORMAL)
        self.historyBox.insert(END, f"{message}\n")
        self.historyBox.config(state=DISABLED)
        self.historyBox.see(END)
    
    # Method for closing the GUI window and terminating server
    def close(self):
        self.__closed = True
        self.window.destroy()
        self.ChatServer.closeConnection()

    # Method for checking if the server window has been closed
    def getClosed(self):
        return self.__closed

class ChatServer:
    """
    This class implements the chat server.
    It uses the socket module to create a TCP socket and act as the chat server.
    Each chat client connects to the server and sends chat messages to it. When 
    the server receives a message, it displays it in its own GUI and also sents 
    the message to the other client.  
    It uses the tkinter module to create the GUI for the server client.
    See the project info/video for the specs.
    """

    def __init__(self, window, serverName = "127.0.0.1", serverPort = 12000):
        
        # Data fields for holding client information
        self.clientList = []
        
        # Server Parameters
        self.serverName = serverName
        self.serverPort = serverPort
        
        # Server Objects
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        self.serverSocket.bind((self.serverName, self.serverPort))
        
        # GUI
        self.gui = Gui(window, self)
        
        # Lock for sending output messages so that we can only send one at a time
        self.mutex = threading.Lock()
        
        # Starts main server thread
        serverThread = threading.Thread(target = self.startServer, name = "Server Thread")
        serverThread.start()

    # Method for broadcasting messages to connected clients
    def broadcastMessage(self, message: str, clientSocket):
        
        # Send received message to all clients except for the sender
        try:
            for client in self.clientList:
                if (client != clientSocket):
                    # Creates output message to send to chatroom
                    outputMessage = f"{message}"
                    client.send(outputMessage.encode("UTF-8"))
        except:
            pass

    # Method for handling client thread operations; each client connection has it's own thread
    def clientHandler(self, clientSocket):
        
        # Client Handler Loop
        while True:
            # Tries to receive a message from the client
            try:
                data = clientSocket.recv(1024)
                if data:
                    # Receives and broadcasts message to all clients
                    message = data.decode("UTF-8")
                    clientName = message.split(":")[0]

                    # Acquires lock for editing GUI and broadcasting messages
                    self.mutex.acquire()

                    # Handles editing of chat history box with new message
                    self.gui.recievedMessage(message)
                    self.broadcastMessage(message, clientSocket)

                    # Releases lock for editing GUI and broadcasting
                    self.mutex.release()

            # If an error occurs, run the exception
            except:
                # Gets index of where this client is stored in lists and removes it
                listIndex = self.clientList.index(clientSocket)
                self.clientList.pop(listIndex)

                # Acquires lock for broadcasting messages and updating GUI
                self.mutex.acquire()

                # Broadcasts leaving message to the chatroom
                self.broadcastMessage(f"{clientName} has left the chat", clientSocket)
                self.gui.recievedMessage(f"{clientName} has left the chat")

                # Closes the connection with the client
                clientSocket.close()

                # Releases lock
                self.mutex.release()

                break
            
    # Main server method
    def startServer(self):
        # Sets socket in listening state
        self.serverSocket.listen()
        # Main server loop
        while True:
            try:
                # Accepts new connections from client
                connectionSocket, connectionAddress = self.serverSocket.accept()
                
                # Adds client to list
                self.clientList.append(connectionSocket)
                
                # Handles creating a new client thread for each new connection received
                clientThread = threading.Thread(target = self.clientHandler, args = (connectionSocket,), name = f"Client Thread {connectionSocket}")
                clientThread.start()
            
            # Detects if server shuts down
            except:
                break
    
    # Used by GUI to close socket if server shuts down
    def closeConnection(self):
        
        # Broadcasts message to ALL clients that server is shutting down
        self.broadcastMessage(f"Server shut down", self.serverSocket)
        self.serverSocket.close()


def main(): #Note that the main function is outside the ChatServer class
    window = Tk()
    ChatServer(window)
    window.mainloop()
    #May add more or modify, if needed

if __name__ == '__main__': # May be used ONLY for debugging
    main()