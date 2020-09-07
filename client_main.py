import threading
from client.client import Client


def start_some_clients(n):
    for i in range(n):
        a_client = Client()
        a_client.register_node('http://127.0.0.2:500' + str(i), a_client.ring_sig_public_key)


if __name__ == '__main__':
    start_some_clients(5)

