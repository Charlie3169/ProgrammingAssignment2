from tkinter import *
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import socket
#import _thread as thread
import threading

fonty = ("Courier",11)
TCP_PORT = 25565

class BulletinClientApp(Tk):
    def __init__(self, master=None):
        Tk.__init__(self, master)
        self.geometry("600x405")
        self.title("Bulletin Board Client")

        self._create_widgets()

        self.IP = ""
        self.sender = None
        self.bound = False
        
    def receiveData(self):
        while True:
            try:
                data = self.sender.recv(1024)
                if not data: break
                self.displayMessage(str(data,'utf-8'))
            except Exception:
                pass

    def _create_socket(self):

        if self.sender:
            self.sender.close()
            
        try:
            self.sender = socket.create_connection((self.ipAddress.get(),TCP_PORT))
            self.displayMessage("Connecting to {0}...".format(self.ipAddress.get()))

            threading.Thread(target=self.receiveData).start()            
        except Exception as e:
            self.displayMessage("Connection failed! " + repr(e))
                    
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

    def displayMessage(self, text):
        self.chatBox.config(state=NORMAL)
        self.chatBox.insert(INSERT,text + "\n")
        self.chatBox.config(state=DISABLED)
       
    def enter_btn(self):
        self.enter(None)
           
    def enter(self, event):
        message = self.entry_text.get().strip()
        self.commands(message) #test purposes

        if message != "":
            if not self.sender:
                self.displayMessage("Error: You aren't connected!")
                return
            
            try:
                #print(bytes(text,'utf-8'))
                self.sender.send(bytes(message,'utf-8'))
            except:
                self.displayMessage("Error: message failed to send!")

            print(message)
            self.entryBox.delete(0,len(self.entryBox.get()))
    
    def commands(self, input):
        if(input.startswith('%')):
            commands = input.split(" ")            
            match commands[0][1:]: #Removes %, code was ugly otherwise
                case 'connect':
                    self.connect(self, commands[1], commands[2])
                case 'join':
                    self.join(self, commands[1])
                case 'post':
                     #Needs some extra stuff to parse correctly
                    subject = ""
                    body = ""                    
                    self.post(self, subject, body)
                case 'users':
                    self.users(self)
                case 'leave':
                    self.leave(self)
                case 'message':
                    self.message(self, commands[1])
                case 'exit':
                    self.exit(self)
                case 'groups':
                    self.groups(self)
                case 'groupjoin':
                    self.groupjoin(self, commands[1])
                case 'grouppost':
                    #Needs some extra stuff to parse correctly
                    groupSubject = ""
                    groupBody = "" 
                    self.grouppost(self, commands[1], groupSubject, groupBody)
                case 'groupusers':
                    self.groupusers(self, commands[1])
                case 'groupleave':
                    self.groupleave(self, commands[1])
                case 'groupmessage':
                    self.groupmessage(self, commands[1], commands[2])
    
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
    
            
    

        
            
app = BulletinClientApp()
app.mainloop()
#root.mainloop()
