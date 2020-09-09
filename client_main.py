import threading
from client.client import Client


def start_some_clients(n):

    client1 = Client()
    client2 = Client()
    client3 = Client()

    client1.register_node("http://127.0.0.2:5001", client1.ring_sig_public_key)
    client2.register_node("http://127.0.0.2:5002", client2.ring_sig_public_key)
    client3.register_node("http://127.0.0.2:5003", client3.ring_sig_public_key)

    pks = [client3.ring_sig_public_key, client2.ring_sig_public_key, client1.ring_sig_public_key]
    sig = client3.gen_membership_proof(pks, "1234568")
    client3.verify_ring_signature(sig, "1234568")

    # client3.new_transaction(transaction_type="txdata", content="1234568")
    pass


if __name__ == '__main__':
    start_some_clients(5)

