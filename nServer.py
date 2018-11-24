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

# manage userList
#def update_userList():

# determine which client receives what message

# accept incoming client connection
# allow client's connection to send and receive freely
def accept_connect(sock):
    client_socket, address = sock.accept()
    print("received connection from ", address)
    client_socket.setblocking(False)
    data = types.SimpleNamespace(addr=address, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(client_socket, events, data=data)
    message = 'Connection Accepted\nHello ' + str(data.addr) + '\nPlease LOGIN or create a NEWUSER'
    userList.append((default_name, client_socket))
    client_socket.send(message.encode())


def handle_connection(key, mask):
    client_socket = key.fileobj
    data = key.data
    # Client has sent data, so we need to read it.
    # If there is no data, then the connection was closed
    if mask & selectors.EVENT_READ:
        try:
            recv_data = client_socket.recv(4096)
            if recv_data:
                data_to_send = my_parser.read_data(recv_data.decode())
                data.outb += data_to_send.encode()
                # print(data.addr, "'s inbound data: ", recv_data.decode())
            else:
                print('closing connection to', data.addr)
                sel.unregister(client_socket)
                client_socket.shutdown(socket.SHUT_RDWR)
                client_socket.close()
        except IOError:
            # print('closing connection to', data.addr)
            print("Connection lost with: ", data.addr)
            sel.unregister(client_socket)
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()

    # there is data to send to the client.
    if mask & selectors.EVENT_WRITE:
        try:
            if data.outb:
                sent = client_socket.send(data.outb)
                data.outb = data.outb[sent:]
        except IOError:
            # print('closing connection to', data.addr)
            print("Connection lost with: ", data.addr)
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
