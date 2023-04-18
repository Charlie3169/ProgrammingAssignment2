import socket
from stuff import *
import threading
import re
import time

TCP_PORT = 25565

class BulletinServer:
    def __init__(self) -> None:
        self.master_socket: socket.socket = socket.create_server(("", TCP_PORT), family=socket.AF_INET6)

        self.clients: dict[str, socket.socket] = dict() # This would link IP addresses to connections.
        self.group: Group = Group()
        self.private_groups: list[Group] = [Group("Idiot Club"), Group("Smart People Club"), 
                                            Group("Secret Club"), Group("Really Secret Club"), Group("Partido Comunista de Cuba")]
        
        self.group.add_message(Message("Chris Lee", "programming", "anyone else here like programming?"))
        self.group.add_message(Message("hello-man", "hi", "hiiiiiiiiiiiiiiiiiiiiiiii"))
        self.group.add_message(Message("Student #604976", "give me a good grade", "NOW"))

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
    
    def join(self, group: Group, new_user: socket.socket, username: str):
        actual_username = username
        clone = 1

        while group.users.get(username):
            actual_username = username + "({0})".format(clone)
            clone += 1
        
        group.users[new_user] = actual_username

        for user in group.users.keys():
            user.sendall(bytes("{0} has joined {1}!".format(actual_username, group.name), 'utf-8'))
        
        self.users(group=group, caller=new_user)

    def leave(self, group: Group, leaving_user: socket.socket):
        for user in group.users.keys():
            user.sendall(bytes("{0} has left {1}!".format(group.users[leaving_user], group.name), 'utf-8'))

        group.users.pop(leaving_user)

    def users(self, group: Group, caller: socket.socket):
        if caller in group.users.keys():
            user_list: str = "Users: " + ", ".join([v for v in group.users.values()])
            print(user_list)
            caller.sendall(bytes(user_list, 'utf-8'))
        else:
            caller.sendall(bytes("You are not in {0}!".format(group.name), 'utf-8'))

    def message(self, group: Group, caller: socket.socket, id: int):
        if caller not in group.users.keys():
            caller.sendall(bytes("You are not in {0}!".format(group.name), 'utf-8'))
            return
        if id < 0 or id >= len(group.current_messages):
            caller.sendall(bytes("Invalid ID! Most recent message is ID#{0}".format(len(group.current_messages)-1), 'utf-8'))
            return
        
        msg: Message = group.current_messages[id]

        caller.sendall(bytes("{0} - {1}".format(msg.sender, msg.postdate.strftime("%m/%d/%y %H:%M")), 'utf-8'))
        time.sleep(0.0001)
        caller.sendall(bytes("{0}: {1}".format(msg.subject, msg.contents), 'utf-8'))
    
    def exit(self, caller: socket.socket):
        if caller in self.group.users.keys():
            self.group.users.pop(caller)

        for group in self.private_groups:
            if caller in group.users.keys():
                group.users.pop(caller)
        
        caller.close()
    
    def get_post_preview(self, group: Group, id: int):
        return "{0}: {1} {2}".format(group.name, id, group.current_messages[id])

    def announce_new_post(self, group: Group):
        for user in group.users.keys():
            user.sendall(bytes(self.get_post_preview(group=group, id=len(group.current_messages)-1), 'utf-8'))

    def post(self, group: Group, caller: socket.socket, input: str):
        if caller not in group.users.keys():
            caller.sendall(bytes("You are not in {0}!".format(group.name), 'utf-8'))
            return
        
        args = re.findall('"([^"]*)"', input)

        if len(args) != 2:
            print(input)
            caller.sendall(bytes('%post "[topic]" "[body]"', 'utf-8'))
            return
        
        topic: str = args[0]
        body: str = args[1]

        group.current_messages.append(Message(group.users[caller], topic, body))
        caller.sendall(bytes("Post in {0} was successful.".format(group.name), 'utf-8'))
        self.announce_new_post(group=group)
    
    def groups(self, caller: socket.socket):
        caller.sendall(bytes("Groups:",'utf-8'))
        time.sleep(0.001) # cope for the fact that my gui fucks up multiline
        for id, group in enumerate(self.private_groups):
            caller.sendall(bytes("{0} {1}".format(id, group.name),'utf-8'))
            time.sleep(0.001)

    def get_group_by_name(self, group_name: str) -> Group:
        if group_name.isnumeric():
            return self.private_groups[int(group_name)]

        for group in self.private_groups:
            if group.name.lower().startswith(group_name.lower()):
                return group
            
        raise IndexError("Group {0} does not exist!".format(group_name))

    def _process_command(self, client: socket.socket, input: str) -> None:
        if(input.startswith('%')):
            commands = input.split(" ", maxsplit=1)            
            match commands[0][1:]: #Removes %, code was ugly otherwise
                #case 'connect':
                    #self.connect(self, commands[1], commands[2])
                case 'join':
                    self.join(group=self.group, new_user=client, username=commands[1])
                case 'post':            
                    self.post(group=self.group, caller=client, input=input)
                case 'users':
                    self.users(group=self.group, caller=client)
                case 'leave':
                    self.leave(group=self.group, leaving_user=client)
                case 'message':
                    self.message(group=self.group, caller=client, id=int(commands[1]))
                case 'exit':
                    self.exit(caller=client)
                case 'groups':
                    self.groups(caller=client)
                case 'groupjoin':
                    # all group commands need to validate name/id... bruh
                    args = re.findall('"([^"]*)"', commands[1])
                    if len(args) == 2: # assume this means name provided
                        self.join(group=self.get_group_by_name(args[0]), new_user=client, username=args[1])
                    elif len(args) == 1: # assume this means id provided
                        # this hack only works with single digit ids... that's okay!
                        self.join(group=self.private_groups[int(commands[1][0])], new_user=client, username=args[0])
                    else:
                        client.sendall(bytes(r'%groupjoin [id | "groupname"] "[username]"', 'utf-8'))
                case 'grouppost':
                    #Needs some extra stuff to parse correctly
                    args = re.findall('"([^"]*)"', commands[1])

                    if len(args) == 3: # group name provided
                        self.post(group=self.get_group_by_name(args[0]), caller=client, input=" ".join([args[1], args[2]]))
                    elif len(args) == 2:
                        self.post(group=self.private_groups[int(commands[1][0])], caller=client, input=" ".join(['"{0}"'.format(x) for x in [args[0], args[1]]]))
                    else:
                        client.sendall(bytes(r'%groupjoin [id | "groupname"] "[topic]" "[message]"', 'utf-8'))
                case 'groupusers':
                    self.users(caller=client, group=self.get_group_by_name(commands[1]))
                case 'groupleave':
                    self.leave(leaving_user=client, group=self.get_group_by_name(commands[1]))
                case 'groupmessage':
                    args = re.findall('"([^"]*)"', commands[1]) # get group by name is stupid
                    idstring = int(commands[1].split(" ")[-1])

                    if len(args) == 1:
                        self.message(group=self.get_group_by_name(args[0]), caller=client, id=idstring)
                    else:
                        self.message(group=self.get_group_by_name(commands[1]), caller=client, id=idstring)
                    
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
    print(re.findall('"([^"]*)"', '%post "Fuck Women." "Does anyone else here fucking hate women?"'))
    b = BulletinServer()
    b.serve_forever()