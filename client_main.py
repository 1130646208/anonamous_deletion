import threading
from client.client import Client


def start_some_clients(n):

    client1 = Client("http://127.0.0.2:5001")
    client2 = Client("http://127.0.0.2:5002")
    client3 = Client("http://127.0.0.2:5003")

    client1.register_node(client1.ip, client1.ring_sig_public_key, client1.rsa_public_key)
    client2.register_node(client2.ip, client2.ring_sig_public_key, client2.rsa_public_key)
    client3.register_node(client3.ip, client3.ring_sig_public_key, client3.rsa_public_key)

    # pks = [client3.ring_sig_public_key, client2.ring_sig_public_key, client1.ring_sig_public_key]
    # sig = client1.gen_membership_proof(pks, "1234568")
    # client3.verify_ring_signature(sig, "1234568")

    client3.new_transaction(transaction_type="txdata", content="this is wrapped secret")


if __name__ == '__main__':
    start_some_clients(5)

