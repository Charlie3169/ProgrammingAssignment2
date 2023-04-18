from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import socket
#import _thread as thread
import threading

fonty = ("Courier",11)
TCP_PORT = 25565

# Doing a graphical interface because extra credit. I don't want to make this in another language though.
class BulletinClientApp(Tk):
    def __init__(self, master=None):
        Tk.__init__(self, master)
        self.geometry("600x405")
        self.title("Bulletin Board Client")

        self._create_widgets()

        self.IP = ""
        self.sender = None
        self.bound = False
        
    # This function runs continuously, waiting to receive data from the server. It will print messages to the output.
    def receive_data(self):
        while True:
            try:
                data = self.sender.recv(1024)
                if not data: break
                self.displayMessage(str(data,'utf-8'))
            except ConnectionResetError as e:
                print(repr(e))
                break
            except Exception as e:
                print(repr(e))
                pass
        
        print("Connection closed...")
        self.displayMessage("You have been disconnected!")
        self.sender.close()
        self.sender = None

    # This creates the connection and makes receive_data run indefinitely.
    def _create_socket(self, address: tuple[str, int]):
        if self.sender:
            self.sender.close()
            
        try:
            self.displayMessage("Connecting to {0}:{1}...".format(address[0], address[1]))
            self.sender = socket.create_connection(address=address)

            threading.Thread(target=self.receive_data).start()
        except Exception as e:
            self.displayMessage("Connection failed! " + repr(e))
    
    # This creates the actual graphical interface.
    def _create_widgets(self):
        self.chatBox = ScrolledText(self,
                relief=GROOVE,font=fonty,state=DISABLED) #width=80,height=15)
        self.chatBox.place(height=375,width=600)

        self.entry_text = StringVar()
        self.entryBox = ttk.Entry(self,width=70,textvariable=self.entry_text)
        self.entryBox.place(width=595,height=30,y=375)
        self.entryBox.bind('<Return>',self.enter)

        self.sendBtn = ttk.Button(self, text="Send",command=self.enter_btn)
        self.sendBtn.place(width=80,height=30,x=520,y=375)
    
    # I don't remember tkinter that well so this function exists since it's duct-taping the send button.
    def enter_btn(self):
        self.enter(None)

    # This is the logic for input. When you press the send button, it takes whatever's in self.entryBox and tries to send it to the server.
    def enter(self, event):
        message = self.entry_text.get().strip()
        if message != "": # Don't send an empty string.
            if not self.sender: # If the connection hasn't been made yet...
                args = message.split(" ") # See if there's a command to parse.
                if args[0] == "%connect": # If the command is to connect...
                    address = "localhost" # Default connection args are localhost and the port constant.
                    port = TCP_PORT

                    if len(args) == 2: # But you can specify an IP and port.
                        ip_parts = message.split(" ")[1].split(":")
                        if len(ip_parts) == 2:
                            port = int(ip_parts[1])
                        address = ip_parts[0]

                    self._create_socket(address=(address, port))
                else: # Otherwise, tell the user that they aren't connected.
                    self.displayMessage("Error: You aren't connected!")

                self.displayMessage(">> " + message)
                self.entryBox.delete(0,len(self.entryBox.get()))
                return
            try:
                self.displayMessage(">> " + message)
                self.sender.send(bytes(message,'utf-8')) # Don't need a protocol, just make the server interpret commands.
            except ConnectionResetError as e:
                self.sender = None
                self.displayMessage("Error: You are disconnected! %%connect again!")
            except Exception as e:
                self.displayMessage("Error: message failed to send!")
                print(repr(e))

            print(message)
            self.entryBox.delete(0,len(self.entryBox.get()))
    
    def connect(self, address, portNumber):
        print(1)

    def join(self, board):
        print(2)
    
    # This one needs to be able to distinguish between the subject and the body
    def post(self, subject, body): 
        print(3)
    
    def users(self):
        # Print list of all users in current group
        print(4)

    def leave(self):        
        print(5)

    def message(self, messageID):
        print(6)
    
    def exit(self):
        print(7)

    def groups(self):
        # Print list of all groups
        print(8)
    
    def groupjoin(self, groupID):
        print(9)
        
    def grouppost(self, groupID, subject, body):
        print(10)

    def groupusers(self, groupID):
        # Print list of users in a specific group
        print(11)

    def groupleave(self, groupID):
        print(12)

    def groupmessage(self, groupID, messageID):
        print(13)
    
    # This sends incoming text to the output.
    def displayMessage(self,text):
        self.chatBox.config(state=NORMAL)
        self.chatBox.insert(INSERT,text + "\n")
        self.chatBox.config(state=DISABLED)
            
app = BulletinClientApp()
app.mainloop()
#root.mainloop()
