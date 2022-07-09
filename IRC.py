import socket
import threading


menu = '/join, /exit, /create, /left'


def create_channel(channel, username):
    server.channels.update({channel: [username]})
    server.users[username][1] = channel
    server.channel_msg(username, client=server.users[username][0], data=f'{username} created {channel} \n'.encode())
    return f'{username} created {channel}'


def exit_server(client, addr, username):
    client.send('Exiting\n\n'.encode())
    print(str([0]) + ':' + str(addr[1]), "disconnected")
    server.connections.remove(client)
    server.users.pop(username)
    client.close()


def left_channel(username, channel):
    server.channels[channel].remove(username)
    server.channel_msg(username, client=server.users[username][0], data=f'{username} left channel \n'.encode())
    # for user in server.channels[server.users[username][1]]:
    #     server.users[user][0].send(f'<{username}> left channel')
    server.users[username][1] = None
    return f'{username} left {channel}'


def join_channel(channel, username):
    if channel not in server.channels:
        print('no such room')
        return 'No such room'
    server.users[username][1] = channel
    server.channels[channel].append(username)
    server.channel_msg(username, client=server.users[username][0], data=f'{username} joined {channel} \n'.encode())
    return f'{username} joined {channel}'


# commands = {
#     '/join': join_channel,
#     '/create': create_channel,
#     '/left': left_channel,
#     '/exit': exit_server
# }

# def create_user(username):
#     user_obj = User(username, id=random.randint(1, 100000))
#     print(user_obj.id)


class Server:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def __init__(self):
        self.sock.bind(('0.0.0.0', 10000))
        self.sock.listen(1)
        self.channels = {}
        self.users = {}
        self.connections = []

    def client_handler(self, client):
        while True:
            client.send("Enter login: ".encode())
            username_request = client.recv(1024)
            username = username_request.decode().replace('\n', '')
            if username in self.users:
                client.send('User already exist\n'.encode())
                continue
            if len(username) > 0:
                break
        self.users.update({username: [client, None]})
        client.send(f'\n\n\n{menu}\n\n\n'.encode())
        return username

    def handler(self, client, addr):
        username = self.client_handler(client)
        try:
            while True:
                data = client.recv(1024)
                message = data.decode().replace('\n', '')
                if len(message) == 0:
                    continue
                match message.split():
                    case ['/create', channel]:
                        create_channel(channel=channel, username=username)
                        continue
                    case ['/join', channel]:
                        join_channel(channel=channel, username=username)
                        continue
                    case ['/left']:
                        left_channel(username=username, channel=self.users[username][1])
                        continue
                    case ['/exit']:
                        exit_server(client, addr, username)
                        continue
                    case ['/users']:
                        print(*self.users.keys())
                    case ['/channels']:
                        print(*self.channels.keys())
                self.channel_msg(username, client, data=data)
                if not data:
                    print(str([0]) + ':' + str(addr[1]), "disconnected")
                    self.connections.pop(client)
                    client.close()
                    break
        except OSError as error:
            print(error)

    def channel_msg(self, username, client, data=None):
        if self.users[username][1] is not None:
                for user in self.channels[self.users[username][1]]:
                    self.users[user][0].send(f'<{username}>'.encode() + data)
        else:
            pass
            # client.send(' '.encode())

    def run(self):
        while True:
            client, addr = self.sock.accept()
            cThread = threading.Thread(target=self.handler, args=(client, addr))
            cThread.daemon = True
            cThread.start()
            print(str([0]) + ':' + str(addr[1]), "connected")
            self.connections.append(client)


class Channel:
    members_online = []
    all_members = []

    def __init__(self, room_name, type):
        self.room_name = room_name
        self.type = type

    def user_join(self, user):
        self.members_online.append(user)

    def check_member(self, user):
        if user in self.all_members:
            print('tes')
            return True
        else:
            print('no')
            return False

    def show_members(self):
        for member in self.members_online:
            print(member)


class User:
    def __init__(self, username, password=None, group='user', channel=None, id=None):
        self.id = id
        self.username = username
        self.password = password
        self.group = group
        self.channel = channel


server = Server()
server.run()
