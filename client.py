# Student Name :Benjamin Chung

from tkinter import *
from socket import *
import threading
from multiprocessing import current_process #only needed for getting the current process name

# GUI Class for the implementation of the tkinter window
class Gui:
    """
    This class implements the GUI for the client's chat window.
    It reads inputs from the message box, updates the GUI with the chat history, and sends input messages
    to the chat client to be sent to the server. 
    Upon closing the GUI, the client will be disconnected and the socket connection will be terminated.
    """
    def __init__(self, ChatClient, window, clientName, serverPort):
        # Data fields for the window GUI
        self.window = window
        self.boxWidth = 55
        self.boxHeight = 15
        self.messageWidth = 30

        # Fields obtained from Client
        self.clientName = clientName
        self.serverPort = serverPort
        self.ChatClient = ChatClient
        self.launchGUI()

    # Method for starting the GUI of the client
    def launchGUI(self):
        # Title
        self.window.title("Client Application")

        # Labels
        self.clientLabel = Label(self.window, text = f"{self.clientName} @port #{self.serverPort}", anchor = "w")
        self.clientLabel.pack(fill=X)

        # Creates frame to hold chat message
        self.messageFrame = Frame(self.window)
        self.messageFrame.pack(fill=X)

        # Chat label
        self.chatLabel = Label(self.messageFrame, text = "Chat Message:")
        self.chatLabel.pack(side=LEFT)

        # Input message box
        self.messageBox = Entry(self.messageFrame, width = self.messageWidth)
        self.messageBox.pack(side = LEFT)

        # Detects when message is to be sent
        self.messageBox.bind("<Return>", self.sendMessage)

        # Chat history label
        self.historyLabel = Label(self.window, text = "Chat History:", anchor = "w")
        self.historyLabel.pack(fill=X)

        # Chat history box
        self.historyBox = Text(self.window, height = self.boxHeight, width = self.boxWidth, wrap="word")
        self.historyBox.pack(fill=X, side=LEFT)
        self.historyBox.tag_configure("indent", lmargin1=120, lmargin2=120)
        self.historyBox.config(state=DISABLED)

        # Chat scrollbar
        self.scrollbar = Scrollbar(self.window, command=self.historyBox.yview)
        self.scrollbar.pack(side=RIGHT, fill=Y)
        self.historyBox.config(yscrollcommand=self.scrollbar.set)

        # Private field to determine if client disconnects
        self.__closed = False
        self.window.protocol("WM_DELETE_WINDOW", self.close)

    # Method of reading the input from the text box and sending it to the server
    def sendMessage(self, e):
        
        # Obtains message and clears the message box
        message = self.messageBox.get()
        self.messageBox.delete(0, 'end')

        if(message !=""):
            
            # If message is valid, display on client's chat log
            self.historyBox.config(state=NORMAL)
            self.historyBox.insert(END, f"{self.clientName}: {message}\n", "indent")
            self.historyBox.config(state=DISABLED)

            # Automatic scroll down
            self.historyBox.see(END)

            # Send message
            self.ChatClient.transmitMessage(message)
    
    # Method for reading message from server and updating chat window
    def recievedMessage(self, message):

        # Display message from server in client's chat log
        self.historyBox.config(state=NORMAL)
        self.historyBox.insert(END, f"{message}\n")
        self.historyBox.config(state=DISABLED)
        self.historyBox.see(END)

    # Method for closing the GUI window and terminating connection to the server
    def close(self):
        self.__closed = True
        self.window.destroy()
        self.ChatClient.closeConnection()

    # Method for checking if the client window has been closed
    def getClosed(self):
        return self.__closed


# Chat client class
class ChatClient:
    """
    This class implements the chat client.
    It uses the socket module to create a TCP socket and to connect to the server.
    It uses the tkinter module to create the GUI for the chat client.
    """
    def __init__(self, window, serverName = "127.0.0.1", serverPort = 12000):
        
        # Data field for the window GUI
        self.window = window
        # Process name

        process = current_process()
        self.clientName = process.name
        
        # Parameters for the server we want to connect to
        self.serverName = serverName
        self.serverPort = serverPort
        
        # Client Object
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        
        # Connects to server
        self.clientSocket.connect((self.serverName, self.serverPort))
        self.clientSocket.send(f"{self.clientName}: has connected!".encode("UTF-8"))
        
        # Obtains the connection port
        serverAddress, serverPort = self.clientSocket.getsockname()
        
        # Creates GUI object
        self.gui = Gui(self, self.window, self.clientName, serverPort)
        
        # Starts thread for receiving messages
        receiveThread = threading.Thread(target = self.receiveMessage, name = "Receive Thread")
        receiveThread.start()
    
    # Method for receiving messages from the server
    def receiveMessage(self):
        # Client receive loop
        while True: 
            try:
                # Attempts to read data from server
                data = self.clientSocket.recv(1024)
                
                # Checks if we receive valid data
                if data:
                    # Decodes data to message and displays for client via GUI
                    message = data.decode("UTF-8")
                    self.gui.recievedMessage(message)
                
                # Checks if server disconnects
                elif not data:
                    self.gui.recievedMessage(f"You have been disconnected!")
                    break
            except:
                
                # For exception, checks if client disconnects. If not, continues loop
                if(self.gui.getClosed):
                    self.clientSocket.close()
                    break

    # Method for sending messages to the server
    def transmitMessage(self, message):
        
        # Tries to send message to server, if it fails, assume the server has been closed or bad connection and close the socket
        try:
            self.clientSocket.send(f"{self.clientName}: {message}".encode("UTF-8"))
        
        # Error occurs
        except:
            # Close the socket and terminate the window
            self.gui.recievedMessage(f"You have been disconnected!")
            self.gui.close()

    # Used by GUI to close socket connection if client disconnects
    def closeConnection(self):
        self.clientSocket.close()


def main(): #Note that the main function is outside the ChatClient class
    window = Tk()
    c = ChatClient(window)
    window.mainloop()
    #May add more or modify, if needed 


if __name__ == '__main__': # May be used ONLY for debugging
    main()