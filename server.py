import socket
from stuff import *
import threading

TCP_PORT = 25565

class BulletinServer:
    def __init__(self) -> None:
        self.master_socket: socket.socket = socket.create_server(("", TCP_PORT), family=socket.AF_INET6)

        self.clients: dict[str, socket.socket] = dict() # This would link IP addresses to connections.
        self.group: Group = Group()

        print("Server is running!")

    def _handle_client(self, conn: socket.socket) -> None:
        input_buffer: bytes = bytes()
        conn.sendall(bytes("You have successfully connected!", 'utf-8'))

        while True:
            try:
                input_buffer = conn.recv(8192) # Safe to assume that any given input won't be this large?

                if not input_buffer: # This will kill the handler thread when connection closes.
                    break

                input_str: str = str(input_buffer, 'utf-8')
                print(input_str) # As debug.

                self._process_command(client = conn, input=input_str)
                # conn.sendall(bytes(output_str, 'utf-8'))
            except OSError as e:
                print("Connection closing...")
                break
            except Exception as e:
                print(repr(e))
                #raise e # For debugging, since this shows the stack trace at the cost of killing a connection.
    
    def join(self, new_user: socket.socket, username: str):
        actual_username = username
        clone = 1

        while self.group.users.get(username):
            actual_username = username + "({0})".format(clone)
            clone += 1
        
        self.group.users[new_user] = actual_username

        for user in self.group.users.keys():
            user.sendall(bytes("{0} has joined the public group!".format(actual_username), 'utf-8'))

    def leave(self, leaving_user: socket.socket):
        for user in self.group.users.keys():
            user.sendall(bytes("{0} has left the public group!".format(self.group.users[leaving_user]), 'utf-8'))

        self.group.users.pop(leaving_user)

    def users(self, caller: socket.socket):
        if caller in self.group.users.keys():
            user_list: str = "Users:\n" + "\n".join([v for v in self.group.users.values()])
            print(user_list)
            caller.sendall(bytes(user_list, 'utf-8'))
        else:
            caller.sendall(bytes("You are not in the public group!", 'utf-8'))

    def message(self, caller: socket.socket, id: int):
        if caller not in self.group.users.keys():
            caller.sendall(bytes("You are not in the public group!", 'utf-8'))
            return
        if id < 0 or id >= len(self.group.current_messages):
            caller.sendall(bytes("Invalid ID! Most recent message is ID#{0}".format(len(self.group.current_messages)-1), 'utf-8'))
            return
        
        msg: Message = self.group.current_messages[id]

        caller.sendall(bytes(msg))
    
    def exit(self, caller: socket.socket):
        if caller in self.group.users.keys():
            self.group.users.pop(caller)
        
        caller.close()

    def _process_command(self, client: socket.socket, input: str) -> None:
        if(input.startswith('%')):
            commands = input.split(" ")            
            match commands[0][1:]: #Removes %, code was ugly otherwise
                #case 'connect':
                    #self.connect(self, commands[1], commands[2])
                case 'join':
                    self.join(new_user=client, username=commands[1])
                case 'post':
                     #Needs some extra stuff to parse correctly
                    subject = ""
                    body = ""                    
                    self.post(self, subject, body)
                case 'users':
                    self.users(caller=client)
                case 'leave':
                    self.leave(leaving_user=client)
                case 'message':
                    self.message(caller=client, id=int(commands[1]))
                case 'exit':
                    self.exit(caller=client)
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
    
    def serve_forever(self):
        while True:
            try:
                connection, address = self.master_socket.accept()

                # print(connection.getpeername()[0] + " is connecting!")

                self.clients[connection.getpeername()[1]] = connection
                print("{0} has connected.".format(connection.getpeername()[1]))
                threading.Thread(target=self._handle_client, args=(connection,), daemon=True).start()
            except KeyboardInterrupt as e:
                print("Server stopping!")
            except Exception as e:
                print(repr(e))

if __name__ == "__main__":
    b = BulletinServer()
    b.serve_forever()