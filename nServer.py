# Referencing https://realpython.com/python-sockets/

import socket
import selectors
import types
import nCommand

# init TCP socket
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = socket.gethostname()
port = 34555
serverSocket.bind((host, port))

# max number of incoming connections
serverSocket.listen(10)
serverSocket.setblocking(False)

# event selector to handle multiplexed I/0
sel = selectors.DefaultSelector()
sel.register(serverSocket, selectors.EVENT_READ, data=None)

# init userLists and the message parser
# userList contains client_name and socket binding key to match easily with the selector
# by default, the client_name will be @-DEFAULT, a client_name that should not be allowed.
my_parser = nCommand.ParseInput()
userList = []
default_name = "@-DEFAULT"
print("server is listening for connections on ", (host, port))


# server maintenance things
def server_command(data):
    if data == "SHUTDOWN":
            sel.unregister(serverSocket)
            serverSocket.close()
            exit()


#close the connection
def close_conn(client_socket):
    key = sel.get_key(client_socket)
    data = key.data
    print('closing connection to', data.addr)
    sel.unregister(client_socket)
    client_socket.shutdown(socket.SHUT_RDWR)
    client_socket.close()


# manage userList
# only done if a user is added or removed from the server
def update_userList(c_sock, c_name, message_tokens):
    try:
        print(c_sock,c_name,message_tokens)
        if message_tokens[0] == "@-LOSTCON":
            userList.remove((c_name, c_sock))
        if message_tokens[0] == "LOGOUT":
            for key, value in enumerate(userList):
                # print(value, " vs ", (c_name, c_sock))
                if (value[1] == c_sock) & (value[0] == c_name):
                    userList.remove(value)
                    # close_conn(c_sock)
                    print("removed: ", value)
        elif (message_tokens[0] == 'NEWUSER') | (message_tokens[0] == 'LOGIN'):
            for key, value in enumerate(userList):
                # print(value, " vs ", (c_name, c_sock))
                if (value[1] == c_sock) & (value[0] != c_name):
                    userList.remove(value)
                    userList.append((c_name, c_sock))
            print(userList)
    except LookupError:
        print("update_userList: failed")
    #        if v[0] == client_name:
    #            flag = False
    #    if flag:
    #        userList.append(c_name)


# determine which client receives what message
# go through the target_list and compare against the userList
# all matches except for the client should receive data
def message_sender(c_name, message_tokens, target_list):
    try:
        # print("MESSAGE_SENDER(CLIENT):",c_name)
        # target_list.append("test")
        # print("MESSAGE_SENDER(RECEIVER):", target_list)
        matched_users = []
        for user in target_list:
            for key, value in enumerate(userList):
                # print(value[0], " vs ", user)
                if (value[0] != c_name) & (value[0] == user):
                    # print("val[0]: ", value[0], " cname: ", c_name, " user: ", user)
                    receiver = sel.get_key(value[1])
                    data = receiver.data
                    data_to_send = c_name + ' '.join(message_tokens)
                    data.outb += data_to_send.encode()
                    matched_users.append(user)
                elif value[0] == c_name:
                    client_key = sel.get_key(value[1])
            if (user not in matched_users) & ("#" not in user) & (user != c_name):
                print("MESSAGE_SENDER: Failed to send to ", user)
                notify_client = client_key.data
                notification = "Failed to send to " + user
                notify_client.outb += notification.encode()
        print("MESSAGE_SENDER matched_users:", matched_users)

    except:
        print("message_sender: failed.")


# accept incoming client connection
# allow client's connection to send and receive freely
def accept_connect(sock):
    client_socket, address = sock.accept()
    print("received connection from ", address)
    client_socket.setblocking(False)
    data = types.SimpleNamespace(addr=address, name=default_name, receiver=[], inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(client_socket, events, data=data)
    message = 'Connection Accepted\nHello ' + str(data.addr) + '\nPlease LOGIN or create a NEWUSER'
    userList.append((default_name, client_socket))
    client_socket.send(message.encode())


# handles the server's read and writes to clients
def handle_connection(key, mask):
    client_socket = key.fileobj
    data = key.data
    # Client has sent data, so we need to read it.
    # If there is no data, then the connection was closed
    if mask & selectors.EVENT_READ:
        try:
            recv_data = client_socket.recv(4096)
            if recv_data:
                c_name, message_tokens, target_list = my_parser.read_data(recv_data.decode(), data.name)
                data.name = c_name
                update_userList(client_socket, c_name, message_tokens)
                # if there is a message to send to other users.
                # otherwise ECHO for the user to know things worked
                # change the target list to the internal list as needed
                if ('@-DEFAULT_SEND' in target_list) & (len(data.receiver) < 1):
                    data_to_send = ' '.join(message_tokens)
                    echo ="ECHO: " + data_to_send
                    data.outb += echo.encode()
                elif len(target_list) > 0:
                    if '@-DEFAULT_SEND' in target_list:
                        add_id = data.receiver[0]
                        # print("ADD this to message tokens for better convention", add_id)
                        # "#" is reserved for groups.
                        if "#" in add_id:
                            string = "(" + add_id + "):"
                            new_message = [string]
                            new_message += message_tokens
                            update_target_list = ["NAME", add_id]
                            data.receiver = my_parser.g_name(update_target_list)
                        else:
                            new_message = ["(WHISPER):"]
                            new_message += message_tokens
                        message_sender(c_name, new_message, data.receiver)
                    else:
                        data.receiver = target_list
                        message_sender(c_name, message_tokens, data.receiver)
                # data_to_send = my_parser.read_data(recv_data.decode(), data.name)
                else:
                    data_to_send = ' '.join(message_tokens)
                    data.outb += data_to_send.encode()
                # print(data.addr, "'s inbound data: ", recv_data.decode())
            else:
                update_userList(client_socket, data.name, "LOGOUT")
                close_conn(client_socket)
                # print('closing connection to', data.addr)
                # sel.unregister(client_socket)
                # client_socket.shutdown(socket.SHUT_RDWR)
                # client_socket.close()
        except IOError:
            # print('closing connection to', data.addr)
            print("Connection lost with: ", data.addr)
            update_userList(client_socket, data.name, "@-LOSTCON".split())
            my_parser.logout(data.name)
            sel.unregister(client_socket)
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()

    # there is data to send to the client.
    if mask & selectors.EVENT_WRITE:
        try:
            if data.outb:
                sent = client_socket.send(data.outb)
                data.outb = data.outb[sent:]
        except:
            # print('closing connection to', data.addr)
            print("Connection lost with: ", data.addr)
            update_userList(client_socket, data.name, "@-LOSTCON".split())
            my_parser.logout(data.name)
            sel.unregister(client_socket)
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()


# event loop that creates a list of (key, events), or sockets
# key.fileobj is the socket object
# mask is an event mask of operations that are ready
def main():
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            if key.data is None:
                accept_connect(key.fileobj)
            else:
                handle_connection(key, mask)


main()
