# Chat-Room
**Added Features**
-	Messages that are sent from a client application are correctly formatted to the right to indicate that it’s a client’s own message. This formatting also ensures that the entire message is to be indented in paragraph form, regardless of its length.
-	Tkinter window includes a title to indicate if process running is a server or client application.
-	Client and server can be configured to operate on separate hosts and ports, they are defaulted to run on an unused port and the loopback IP address.
-	An automatic scroll-down feature is added for each message sent and received. 
-	The GUI can also detect when it is closed, meaning the client OR server is now “disconnected”. When the clientGUI is closed, the client will let the server know to broadcast to the other clients that the client has left and then close down its own socket connection with the server. When the serverGUI is closed, the server will broadcast to ALL clients that the server has shut down and close its own socket connection.
-	Mutex lock is added in the server to allow for correct order of client messaging to occur.

**Bugs**
-	You must manually edit the serverName and serverPort values yourself to indicate where the clients should connect to.
-	In main, you must manually set how many client processes you would like. 
