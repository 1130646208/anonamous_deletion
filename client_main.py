from threading import Thread
from client.client import Client
from flask import Flask, jsonify
import requests
from pools import POOL_PORT, POOL_URL


app = Flask(__name__)
client2 = Client("http://127.0.0.1:5002")


def start_some_clients(n):
    client2.register_node(client2.ip, client2.ring_sig_public_key, client2.rsa_public_key_tuple)

    # secret = b64.b64encode(b'weather changes for nothing!')
    # pieces = client1.split_secret(secret, 2, 3)
    # pieces_encoded = [b64.b64encode(piece.encode()) for piece in pieces]
    # rsa_pks = client1.get_rsa_pks_from_pool()
    # wrapped_secret = client1.encrypt_secrets(rsa_pks, pieces_encoded, True)

    # others, wanted = client3.get_a_secret_from_wrapped(wrapped_secret, client1.rsa_private_key_origin)

    client2.new_transaction(transaction_type="txdata", content='wrapped_secret')

    client2.get_transactions_to_pack()
    print(client2.mine())
    client2.block_chain.resolve_conflicts()


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': client2.block_chain.chain,
        'length': len(client2.block_chain.chain),
    }
    return jsonify(response), 200


@app.route('/view/transactions', methods=['GET'])
def view_transaction_pool():
    r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/view/transactions")
    if r.status_code == 201:
        return r.json(), 201
    else:
        return 'Error', 500


@app.route('/view/ring', methods=['GET'])
def view_ring_sig_pk_pool():
    r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/view/ring_sig_key")
    if r.status_code == 201:
        return r.json(), 201
    else:
        return 'Error', 500


@app.route('/view/rsa', methods=['GET'])
def view_rsa_pk_pool():
    r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/view/rsa_pub_key")
    if r.status_code == 201:
        return r.json(), 201
    else:
        return 'Error', 500


def start_server():
    from argparse import ArgumentParser
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5002, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host=POOL_URL, port=port)


if __name__ == '__main__':
    t = Thread(target=start_server)
    t.start()
    start_some_clients(5)
