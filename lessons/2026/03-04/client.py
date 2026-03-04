import socket
import sys


def main():
    try:
        # create a TCP socket (SOCK_STREAM)
        s = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM, proto=0)
    except socket.error as err:
        print("Error during creation of the socket")
        print(f"Reason: {err}")
        sys.exit()

    print("Socket created")

    target_host = "130.251.42.5"  # "127.0.0.1" for local testing
    target_port = 32002
    addr = (target_host, target_port)
    try:
        s.connect(addr)
        print(f"Socket is connected to {target_host}:{target_port}")
    except ConnectionRefusedError as err:
        print(f"Connection refused from {target_host}:{target_port}")
        print(f"Details: {err}")
        sys.exit()
    except TimeoutError as t_err:
        print(f"Timeout error during connection to {target_host}:{target_port}")
        print(f"Details: {t_err}")
        sys.exit()

    req = "Hello from client"
    s.send(req.encode())
    d = s.recv(100000)
    print(f"Data received {d}")


main()
