import json
import socket
import sys
from datetime import datetime
from threading import Thread
from typing import Dict, Tuple

from data import server_addr

clients = {}


def main() -> None:
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
            send_from(c_addr, {"name": c_name, "msg": "joins the chat", "timestamp": dt})
            Thread(
                target=client_manager,
                kwargs={"name": c_name, "sock": c_sock, "addr": c_addr},
            ).start()
        s.close()
    except socket.error as err:
        print("Error during creation of the socket")
        print(f"Reason: {err}")
        sys.exit()


def client_manager(name: str, sock: socket, addr: Tuple[str, int]) -> None:
    msg = "x"
    while msg != "end":
        msg = sock.recv(200).decode()
        dt = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        if msg != "end":
            send_from(addr, {"name": name, "msg": msg, "timestamp": dt})
    del clients[addr]
    send_from(addr, {"name": name, "msg": "leaves the chat", "timestamp": dt})
    sock.close()


def send_from(addr: str, data: Dict[str, any]) -> None:
    print(f"{data["name"]} ({data["timestamp"]}) >", data["msg"])
    for c_addr, c_sock in clients.items():
        if c_addr != addr:
            c_sock.send(json.dumps(data).encode())


main()
