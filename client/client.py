import requests

from .block_chain import BlockChain
from pools import public_ip_pool, public_tx_pool, POOL_URL, POOL_PORT


blockchain = BlockChain()


class Client:

    def __init__(self, ip=None):
        self.__ip = ip
        self.__public_key = None
        self.__private_key = None
        self.__ring_sig_public_key = None
        self.__ring_sig_private_key = None
        self.chain = blockchain
        pass

    def gen_proof(self):
        pass

    def register_node(self, ip):
        form = {
            "ip": ip,
        }
        try:
            r = requests.post("http://" + POOL_URL + ":" + POOL_PORT + "/nodes/register", data=form)
            print(r)
        except Exception as e:
            print("client register error", e)

    def new_transaction(self, membership_proof, transaction_type, content):
        form = {
            "membership_proof": membership_proof,
            "transaction_type": transaction_type,
            "content": content
        }
        try:
            r = requests.post("http://" + POOL_URL + ":" + POOL_PORT + "/transactions/new", data=form)
            print(r)
        except Exception as e:
            print("client submit transaction error", e)

