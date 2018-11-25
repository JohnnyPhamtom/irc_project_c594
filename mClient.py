import socket
import selectors
import types
import asyncio
import functools

host = socket.gethostname()
port = 34555
sel = selectors.DefaultSelector()
target_addr = (host, port)
target_name = 'server'

def handle_connection(key, mask):
    client_socket = key.fileobj
    data = key.data
    if mask & selectors.EVENT_READ:
        try:
            recv_data = client_socket.recv(4096)
            if recv_data:
                print(recv_data.decode())
            else:
                print('closing connection to', data.addr)
                sel.unregister(client_socket)
                client_socket.shutdown(socket.SHUT_RD)
                client_socket.close()
        except IOError:
            # print('closing connection to', data.addr)
            print("Connection lost with: ", data.addr)
            sel.unregister(client_socket)
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()
    if mask & selectors.EVENT_WRITE:
        try:
            if data.outb:
                sent = client_socket.send(data.outb.encode())
                data.outb = data.outb[sent:]
        except IOError:
            sel.unregister(client_socket)
            client_socket.shutdown(socket.SHUT_RDWR)
            client_socket.close()


def update_target(message, default):
    string_tokens = message.split()
    if len(string_tokens) > 1:
        if (string_tokens[0] == '/w') | (string_tokens[0] == '/g'):
            return string_tokens[1]
    return default


def get_input(key):
    while True:
        #await asyncio.sleep(0.01)
        client_socket = key.fileobj
        data = key.data
        # prompt = data.prompt
        try:
            # message = input("To " + prompt + ": ")
            message = input()
            if len(message) > 0:
                client_socket.send(message.encode())
                #data.prompt = update_target(message, prompt)
            if message == "LOGOUT":
                # finish the connection
                client_socket.shutdown(socket.SHUT_WR)
                break
        except IOError:
            print("GET_INPUT failed")

async def read_from_server():
    # print("established read")
    while True:
        await asyncio.sleep(0)
        # client_socket = key.fileobj
        try:
            events = sel.select(timeout=None)
            if events:
                for key, mask in events:
                    handle_connection(key, mask)
            if not sel.get_map():
                break
        except IOError:
            print("read_from_server: lost connection")


def user_connect():
    try:
        server_addr = (host, port)
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(server_addr)
        # client_socket.connect_ex(server_addr) non-blocking connect
        client_socket.setblocking(False)
    except ConnectionRefusedError:
        print("server not found..")
        exit(-1)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    data = types.SimpleNamespace(addr=server_addr, prompt=target_name, inb=b'', outb=b'')
    sel_key = sel.register(client_socket, events, data=data)
    # kb_event_sel.register(sys.stdin, selectors.EVENT_READ, get_input(sel_key))
    return sel_key


def main():
    loop = asyncio.get_event_loop()
    sel_key = user_connect()
    try:
        # get_input(sel_key)
        asyncio.sleep(0.01)
        asyncio.ensure_future(read_from_server())
        # asyncio.ensure_future(get_input(sel_key))
        loop.run_in_executor(None, functools.partial(get_input,sel_key))
        loop.run_forever()
    except:
        print("disconnected from server")
    finally:
        loop.close()
        exit(0)


asyncio.ensure_future(main())