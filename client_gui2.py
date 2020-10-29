import tkinter as tk
from tkinter import *
from threading import Thread
from client.client import Client
from flask import Flask, jsonify
import requests
import json
import base64 as b64
from pools import POOL_PORT, POOL_URL

CLIENT_URL = '127.0.0.1'
CLIENT_PORT = '5002'

app = Flask(__name__)
client = Client('http://' + CLIENT_URL + ':' + CLIENT_PORT)


def start_server():
    @app.route('/chain', methods=['GET'])
    def full_chain():
        response = {
            'chain': client.block_chain.chain,
            'length': len(client.block_chain.chain),
        }
        return jsonify(response), 200

    app.run(host=CLIENT_URL, port=CLIENT_PORT)


class ClientGui:

    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry('400x400+200+200')
        self.root.rowconfigure(0, weight=1)
        self.root.columnconfigure(0, weight=1)
        # self.root.rowconfigure(2, weight=1)
        # self.root.rowconfigure(3, weight=1)
        # self.root.rowconfigure(4, weight=1)
        self.root.title('[BlockChain!]' + client.ip)
        # txt_frame
        self.txt_frame = tk.LabelFrame(self.root, text='信息输出')
        self.txt_frame.grid(row=0, column=0, padx=8, pady=8, sticky=NSEW)
        self.txt_frame.rowconfigure(0, weight=1)
        self.txt_frame.columnconfigure(0, weight=1)
        self.txt_frame.columnconfigure(1, weight=1)
        self.txt_frame.columnconfigure(3, weight=1)
        self.txt_frame.columnconfigure(4, weight=1)
        # btn_frame
        self.btn_frame = tk.LabelFrame(self.root, text='进行操作')
        self.btn_frame.grid(row=1, column=0, padx=8, pady=8, sticky=NSEW)
        self.btn_frame.rowconfigure(0, weight=1)
        self.btn_frame.columnconfigure(list(range(0, 4)), weight=1)
        # self.btn_frame.columnconfigure(1, weight=1)
        # self.btn_frame.columnconfigure(2, weight=1)
        # self.btn_frame.columnconfigure(3, weight=1)

        # define 2 text area with scroll bar
        self.view_area = tk.Text(self.txt_frame, font="Times12")
        self.view_area.grid(row=0, column=0, columnspan=2, padx=8, pady=8, sticky=NSEW)
        self.sb = tk.Scrollbar(self.txt_frame)
        self.sb.grid(row=0, column=2, sticky=W+N+S)
        self.view_area.config(yscrollcommand=self.sb.set)
        self.sb.config(command=self.view_area.yview)

        self.view_area2 = tk.Text(self.txt_frame, font="Times12")
        self.view_area2.grid(row=0, column=3, columnspan=2, padx=8, pady=8, sticky=NSEW)
        self.sb2 = tk.Scrollbar(self.txt_frame)
        self.sb2.grid(row=0, column=5, sticky=W+N+S)
        self.view_area2.config(yscrollcommand=self.sb2.set)
        self.sb2.config(command=self.view_area2.yview)

        self.secret = b64.b64encode(b'weather changes for nothing!')
        # define buttons
        tk.Button(self.btn_frame, text='   查看交易池   ', fg='black',
                  command=lambda: self.view_transaction_pool()).grid(row=0, column=0, padx=8, pady=8)
        tk.Button(self.btn_frame, text='  查看区块链  ', fg='black',
                  command=lambda: self.full_chain()).grid(row=0, column=1, padx=8, pady=8)
        tk.Button(self.btn_frame, text='查看RSA公钥', fg='black',
                  command=lambda: self.view_rsa_pk_pool()).grid(row=0, column=2, padx=8, pady=8)
        tk.Button(self.btn_frame, text='查看环签名公钥', fg='black',
                  command=lambda: self.view_ring_sig_pk_pool()).grid(row=0, column=3, padx=8, pady=8)
        tk.Button(self.btn_frame, text='解决区块链冲突', fg='black',
                  command=self.rsv_con).grid(row=1, column=0, padx=8, pady=8)
        tk.Button(self.btn_frame, text=' 发  送  交  易 ', fg='black',
                  command=self.new_tx).grid(row=1, column=1, padx=8, pady=8)
        tk.Button(self.btn_frame, text='打  包  交  易', fg='black',
                  command=self.pk_tx).grid(row=1, column=2, padx=8, pady=8)
        tk.Button(self.btn_frame, text='   挖        矿   ', fg='black',
                  command=self.mn).grid(row=1, column=3, padx=8, pady=8)
        tk.Button(self.btn_frame, text='   节点注册   ', fg='black',
                  command=self.register).grid(row=2, column=1, padx=8, pady=8)
        tk.Button(self.btn_frame, text='   加密信息   ', fg='black',
                  command=self.enc_sec).grid(row=3, column=0, padx=8, pady=8)
        tk.Button(self.btn_frame, text='分散加密的信息', fg='black',
                  command=self.send_sec_txs).grid(row=3, column=1, padx=8, pady=8)
        tk.Button(self.btn_frame, text='获取给我的秘密', fg='black',
                  command=self.get_ob_sec).grid(row=3, column=2, padx=8, pady=8)
        tk.Button(self.btn_frame, text=' 撤销我的秘密 ', fg='black',
                  command=self.send_revoke_txs).grid(row=3, column=3, padx=8, pady=8)

        tk.Button(self.btn_frame, text=' 请求恢复秘密 ', fg='black',
                  command=self.send_recover_txs).grid(row=2, column=2, padx=8, pady=8)

        tk.Button(self.btn_frame, text=' 恢复我的秘密 ', fg='black',
                  command=self.reconstruct_secret).grid(row=2, column=3, padx=8, pady=8)

        self.root.mainloop()

    def full_chain(self):
        self.view_area.delete('1.0', 'end')
        response = {
            'chain': client.block_chain.chain,
            'length': len(client.block_chain.chain),
        }
        text = json.dumps(response, indent=2)
        self.view_area.insert('end', text)

    def view_transaction_pool(self):
        self.view_area.delete('1.0', 'end')
        r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/view/transactions")
        if r.status_code == 201:
            text = json.dumps(r.json(), indent=2)
        else:
            text = 'Error'

        self.view_area.insert('end', text)

    def view_ring_sig_pk_pool(self):
        self.view_area.delete('1.0', 'end')
        r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/view/ring_sig_key")
        if r.status_code == 201:
            text = json.dumps(r.json(), indent=2)
        else:
            text = 'Error'
        self.view_area.insert('end', text)

    def view_rsa_pk_pool(self):
        self.view_area.delete('1.0', 'end')
        r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/view/rsa_pub_key")
        if r.status_code == 201:
            text = json.dumps(r.json(), indent=2)
        else:
            text = 'Error'
        self.view_area.insert('end', text)

    def register(self):
        client.register_node(client.ip, client.ring_sig_public_key, client.rsa_public_key_tuple)

    def new_tx(self, transaction_type="txdata", content='secret'):
        client.new_transaction(transaction_type=transaction_type, content=content)

    def pk_tx(self):
        client.get_transactions_to_pack()

    def mn(self):
        mine_message = client.mine()
        print(mine_message)

    def rsv_con(self):
        client.block_chain.resolve_conflicts()

    def enc_sec(self):
        pieces = client.split_secret(self.secret, 2, 3)
        all_pks = client.get_rsa_pks_from_pool()
        assert (len(all_pks) >= len(pieces))

        pieces_encoded = [item.encode() for item in pieces]
        result = client.encrypt_secrets_parallel(all_pks[0:len(pieces_encoded)], pieces_encoded)
        print('Encrypted 3 secrets.')
        return result

    def send_sec_txs(self):
        result = self.enc_sec()
        result_str = [str(item) for item in result]
        for item in result_str:
            self.new_tx(transaction_type='txdata', content=item)
            print('Sent secret {} to a tx'.format(item))

    def send_revoke_txs(self):
        for pk, secret_md5 in client.rsa_pk_and_secret_piece_mapping.items():
            content_bytes = client.rsa_handler.rsa_enc_long_bytes(secret_md5.encode(), pk)
            self.new_tx(transaction_type='txdelete', content=str(content_bytes))
            print('Sent revoke requests for secret_md5: {}'.format(secret_md5))
        client.rsa_pk_and_secret_piece_mapping.clear()

    def send_recover_txs(self):
        client.recover_secret_tx()

    def reconstruct_secret(self):
        print('秘密恢复成功：', client.recover_secret(client.recovered_secret_pieces))

    def get_ob_sec(self):
        client.get_obliged_secrets()


if __name__ == "__main__":
    t1 = Thread(target=start_server)
    t1.start()
    g = ClientGui()
