import socket
import sys
from threading import Thread

def client_management(c_sock, c_addr):
    print(f"Client connected from f{c_addr}")
    d = c_sock.recv(100000)
    print(f"Data received {d}")
    c_sock.send("Hello from server".encode())
    c_sock.close()


def main():
    try:
        # create a TCP socket (SOCK_STREAM)
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0)
    except socket.error as err:
        print("Error during creation of the socket")
        print(f"Reason: {err}")
        sys.exit()

    print("Socket created")

    target_host = "0.0.0.0"  # 127.0.0.1 is the same
    target_port = 32002
    addr = (target_host, target_port)
    s.bind(addr)
    s.listen(5)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
 
    while True:
        print("Waiting for new connection")
        c_sock, c_addr = s.accept()
        t = Thread(target=client_management, args=(c_sock, c_addr))
        t.start()

main()
