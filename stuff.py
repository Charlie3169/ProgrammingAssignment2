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

    def display(self) -> str:
        return "{0} {1} {2} {3}".format(self.id, self.sender, self.postdate, self.subject)

class Group:
    def __init__(self) -> None:
        self.current_messages: dict[int, Message] = dict()
        self.users: dict[socket.socket, str] = dict()

    def add_user(self, name: str) -> None:
        self.users.append(name)

    def remove_user(self, name: str) -> None:
        self.users.remove(name)

    def add_message(self, msg: Message) -> None:
        self.current_messages[msg.id] = msg
    

    pass

