# This file defines and implements Group and Message classes.
import datetime
import socket
from collections import deque

class Message:
    def __init__(self, sender: str, subject: str, contents: str) -> None:
        self.sender = sender
        self.postdate: datetime.datetime = datetime.datetime.now()
        self.subject = subject
        self.contents = contents

    def __str__(self) -> str:
        return "{0} {1} {2}".format(self.sender, self.postdate.strftime("%d/%m/%y %H:%M"), self.subject)
    
    def __bytes__(self) -> bytes:
        return bytes(str(self), 'utf-8')
    

class Group:
    def __init__(self, name: str = "Public") -> None:
        self.current_messages: list[Message] = list()
        self.users: dict[socket.socket, str] = dict()
        self.name: str = name

    def add_message(self, msg: Message) -> None:
        self.current_messages.append(msg)

    pass

