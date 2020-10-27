from threading import Thread
from client.client import Client
from flask import Flask, jsonify
import requests
from pools import POOL_PORT, POOL_URL
import time

app = Flask(__name__)
CLIENT_URL = '127.0.0.1'
# CLIENT_PORT = '5003'
from argparse import ArgumentParser
parser = ArgumentParser()
parser.add_argument('-p', '--port', default=5003, type=int, help='port to listen on')
args = parser.parse_args()
port = args.port
client = Client('http://' + CLIENT_URL + ':' + str(port))


def block_chain_run():
    client.register_node(client.ip, client.ring_sig_public_key, client.rsa_public_key_tuple)

    # secret = b64.b64encode(b'weather changes for nothing!')
    # pieces = client1.split_secret(secret, 2, 3)
    # pieces_encoded = [b64.b64encode(piece.encode()) for piece in pieces]
    # rsa_pks = client1.get_rsa_pks_from_pool()
    # wrapped_secret = client1.encrypt_secrets(rsa_pks, pieces_encoded, True)

    # others, wanted = client3.get_a_secret_from_wrapped(wrapped_secret, client1.rsa_private_key_origin)

    # client2.new_transaction(transaction_type="txdata", content='wrapped_secret')
    while True:
        time.sleep(0.05)
        if client.get_transactions_to_pack():
            client.block_chain.resolve_conflicts()
            client.mine()
        client.block_chain.resolve_conflicts()
        client.get_obliged_secrets()


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': client.block_chain.chain,
        'length': len(client.block_chain.chain),
    }
    return jsonify(response), 200
# @app.route('/view/transactions', methods=['GET'])
# def view_transaction_pool():
#     r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/view/transactions")
#     if r.status_code == 201:
#         return r.json(), 201
#     else:
#         return 'Error', 500
#
#
# @app.route('/view/ring', methods=['GET'])
# def view_ring_sig_pk_pool():
#     r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/view/ring_sig_key")
#     if r.status_code == 201:
#         return r.json(), 201
#     else:
#         return 'Error', 500
#
#
# @app.route('/view/rsa', methods=['GET'])
# def view_rsa_pk_pool():
#     r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/view/rsa_pub_key")
#     if r.status_code == 201:
#         return r.json(), 201
#     else:
#         return 'Error', 500


def start_server(_port):
    app.run(host=CLIENT_URL, port=_port)


if __name__ == '__main__':

    t = Thread(target=start_server, args=(port, ))
    t.start()

    block_chain_run()
