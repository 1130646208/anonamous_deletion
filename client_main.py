import threading
from client.client import Client
import base64 as b64


def start_some_clients(n):

    client1 = Client("http://127.0.0.2:5001")
    client2 = Client("http://127.0.0.2:5002")
    client3 = Client("http://127.0.0.2:5003")

    client1.register_node(client1.ip, client1.ring_sig_public_key, client1.rsa_public_key_tuple)
    client2.register_node(client2.ip, client2.ring_sig_public_key, client2.rsa_public_key_tuple)
    client3.register_node(client3.ip, client3.ring_sig_public_key, client3.rsa_public_key_tuple)

    secret = b64.b64encode(b'weather changes for nothing!')
    pieces = client3.split_secret(secret, 2, 3)
    pieces_encoded = [b64.b64encode(piece.encode()) for piece in pieces]
    rsa_pks = client3.get_rsa_pks_from_pool()
    wrapped_secret = client3.rsa_handler.encrypt_secrets(rsa_pks, pieces_encoded, True)

    client3.new_transaction(transaction_type="txdata", content=str(wrapped_secret))


if __name__ == '__main__':
    start_some_clients(5)

