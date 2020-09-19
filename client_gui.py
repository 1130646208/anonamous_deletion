import tkinter as tk
from threading import Thread
from client.client import Client
from flask import Flask, jsonify
import requests
from pools import POOL_PORT, POOL_URL


app = Flask(__name__)
client2 = Client("http://127.0.0.1:5002")

root = tk.Tk()
root.title('BlockChain!')

frame = tk.Frame(root)
frame.pack(side=tk.LEFT, padx=10, pady=10)


def register():
    client2.register_node(client2.ip, client2.ring_sig_public_key, client2.rsa_public_key_tuple)


def new_tx():
    client2.new_transaction(transaction_type="txdata", content='wrapped_secret')


def pk_tx():
    client2.get_transactions_to_pack()


def mn():
    print(client2.mine())


def rsv_con():
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
        print("view_rsa_pk_pool")
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


# function callers
view_tx_pool = tk.Button(frame, text='   查看交易池   ', fg='black',
                         command=lambda: view_transaction_pool()).grid(row=0, column=0, padx=8, pady=8)
view_block_chain = tk.Button(frame, text='  查看区块链  ', fg='black',
                             command=lambda: full_chain()).grid(row=0, column=1, padx=8, pady=8)
view_rsa_pk = tk.Button(frame, text='查看RSA公钥', fg='black',
                        command=lambda: view_rsa_pk_pool()).grid(row=0, column=2, padx=8, pady=8)
view_ring_sig_pk = tk.Button(frame, text='查看环签名公钥', fg='black',
                             command=lambda: view_ring_sig_pk_pool()).grid(row=0, column=3, padx=8, pady=8)
resolve_conflict = tk.Button(frame, text='解决区块链冲突', fg='black',
                             command=rsv_con).grid(row=1, column=0, padx=8, pady=8)
send_tx = tk.Button(frame, text=' 发  送  交  易 ', fg='black',
                    command=new_tx).grid(row=1, column=1, padx=8, pady=8)
pack_tx = tk.Button(frame, text='打  包  交  易', fg='black',
                    command=pk_tx).grid(row=1, column=2, padx=8, pady=8)
mine_block = tk.Button(frame, text='   挖        矿   ', fg='black',
                       command=mn).grid(row=1, column=3, padx=8, pady=8)
register_node = tk.Button(frame, text='   节点注册   ', fg='black',
                          command=register).grid(row=2, column=1, padx=8, pady=8)









root.mainloop()


