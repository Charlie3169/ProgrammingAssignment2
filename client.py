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
                self.message(str(data,'utf-8'))
            except Exception:
                pass

    def _create_socket(self):

        if self.sender:
            self.sender.close()
            
        try:
            self.sender = socket.create_connection((self.ipAddress.get(),TCP_PORT))
            self.message("Connecting to {0}...".format(self.ipAddress.get()))

            threading.Thread(target=self.receiveData).start()            
        except Exception as e:
            self.message("Connection failed! " + repr(e))
                    
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
    
    def enter_btn(self):
        self.enter(None)

    def enter(self, event):
        message = self.entry_text.get().strip()
        if message != "":
            if not self.sender:
                self.message("Error: You aren't connected!")
                return
            
            try:
                #print(bytes(text,'utf-8'))
                self.sender.send(bytes(message,'utf-8'))
            except:
                self.message("Error: message failed to send!")

            print(message)
            self.entryBox.delete(0,len(self.entryBox.get()))
            
    def message(self,text):
        self.chatBox.config(state=NORMAL)
        self.chatBox.insert(INSERT,text + "\n")
        self.chatBox.config(state=DISABLED)
            
app = BulletinClientApp()
app.mainloop()
#root.mainloop()
