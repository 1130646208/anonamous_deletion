from flask_cors import CORS
from flask import Flask, jsonify, request

from pools import public_ip_pool, public_tx_pool, POOL_URL, POOL_PORT

app = Flask(__name__)
CORS(app)


@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.form
    nodes = values.get('ip').replace(" ", "").split(',')

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        public_ip_pool.add_ip(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': [node for node in public_ip_pool.ips],
    }
    return jsonify(response), 201


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.form
    print(values)
    # Create a new Transaction
    try:
        public_tx_pool.submit_transaction(values.get('membership_proof'), values.get('transaction_type'), values.get('content'))
        response = {'message': 'Transaction will be added to public tx pool'}
        return jsonify(response), 201

    except ValueError as ve:
        print(ve)
        response = {'message': 'Invalid Transaction!'}
        return jsonify(response), 406


@app.route('/transactions/all', methods=['GET'])
def view_all_transactions():
    response = {'message': 'all transactions:' + str(public_tx_pool.txs)}
    return jsonify(response), 201


@app.route('/nodes/all', methods=['GET'])
def view_all_nodes():
    response = {'message': 'all registered nodes:' + str(public_ip_pool.ips)}
    return jsonify(response), 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=POOL_PORT, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port
    app.run(host=POOL_URL, port=port)
