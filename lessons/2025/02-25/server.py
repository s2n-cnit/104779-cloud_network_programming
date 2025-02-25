import json
import socket
import sys
from datetime import datetime
from threading import Thread

from data import server_addr

clients = {}


def main():
    try:
        # create a TCP socket (SOCK_STREAM)
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0)
        s.bind(server_addr)
        s.listen(5)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while True:
            c_sock, c_addr = s.accept()
            clients[c_addr] = c_sock

            c_name = c_sock.recv(200).decode()
            dt = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
            msg = "joins the chat"
            print(f"{c_name} ({dt}) > {msg}")
            for c_addr_other, c_sock_other in clients.items():
                if c_addr_other != c_addr and c_sock_other != c_sock:
                    d = {"name": c_name, "msg": msg, "timestamp": dt}
                    c_sock_other.send(json.dumps(d).encode())
            Thread(
                target=client_manager,
                kwargs={"name": c_name, "sock": c_sock, "addr": c_addr},
            ).start()
        s.close()
    except socket.error as err:
        print("Error during creation of the socket")
        print(f"Reason: {err}")
        sys.exit()


def client_manager(name, sock, addr):
    msg = "x"
    while msg != "end":
        msg = sock.recv(200).decode()
        dt = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        if msg != "end":
            print(f"{name} ({dt}) >", msg)
            for c_addr, c_sock in clients.items():
                if c_addr != addr:
                    d = {"name": name, "msg": msg, "timestamp": dt}
                    c_sock.send(json.dumps(d).encode())
    msg = "leaves the chat"
    print(f"{name} ({dt}) > {msg}")
    del clients[c_addr]
    for c_addr, c_sock in clients.items():
        d = {"name": name, "msg": msg, "timestamp": dt}
        c_sock.send(json.dumps(d).encode())
    sock.close()


main()
