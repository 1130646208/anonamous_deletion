from flask_cors import CORS
from flask import Flask, jsonify, request
import json

from pools import public_ip_pool, public_tx_pool, public_ring_sig_pk_pool, POOL_URL, POOL_PORT
from helpers import str_vector_to_tuple

app = Flask(__name__)
CORS(app)


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.json
    data = json.loads(values)
    # 从client_main 传过来的是ImmutableMultiDict('ip':aaa, 'ring_sig_pk': xxx, 'ring_sig_pk': yyy)
    # 所以要用getlist才能获得所有的ring_sig_pk,但是变成str类型的了，需要转化成int类型
    ip = data.get("ip")
    ring_sig_pk = data.get("ring_sig_pk")

    if ip is None:
        return "Error: Please supply a valid ip.", 400

    if ring_sig_pk is None:
        return "Error: Please supply a valid ring_sig_pk.", 400

    public_ip_pool.add_ip(ip)
    # because 'str_vector_to_tuple' returns list, it is necessary to write [0]
    public_ring_sig_pk_pool.add_pk(str_vector_to_tuple(ring_sig_pk)[0])

    response = {
        "message": "New nodes have been added.",
        "total_nodes": [ip for ip in public_ip_pool.ips],
        "total_ring_sig_pks": [ring_sig_pk for ring_sig_pk in public_ring_sig_pk_pool.pks]
    }
    return jsonify(response), 201


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    print(values)
    # Create a new Transaction
    try:
        public_tx_pool.submit_transaction(values.get("membership_proof"), values.get("transaction_type"),
                                          values.get("content"))
        response = {"message": "Transaction will be added to public tx pool"}
        return jsonify(response), 201

    except ValueError as ve:
        print(ve)
        response = {"message": "Invalid Transaction!"}
        return jsonify(response), 406


@app.route('/transactions/all', methods=['GET'])
def view_all_transactions():
    response = {"transactions": str(public_tx_pool.txs)}
    return jsonify(response), 201


@app.route('/nodes/all', methods=['GET'])
def view_all_nodes():
    response = {"message": "all registered nodes:" + str(public_ip_pool.ips) + '\n' +
                           str(public_ring_sig_pk_pool.pks)}
    return jsonify(response), 201


@app.route('/nodes/ring_sig_key', methods=['GET'])
def get_ring_sig_pk_pool():
    # 'get_all_pks' returns str
    return public_ring_sig_pk_pool.get_all_pks(), 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=POOL_PORT, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host=POOL_URL, port=port)
