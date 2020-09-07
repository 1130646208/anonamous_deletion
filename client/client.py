import requests

from .block_chain import BlockChain
from pools import POOL_URL, POOL_PORT
from ring_signature.ring_signature_handler import RingSigHandler


class Client:

    def __init__(self, ip=None):
        self.chain = BlockChain()
        self.ring_sig_handler = RingSigHandler()
        self.__ip = ip
        self.__rsa_public_key = None
        self.__rsa_private_key = None

        self.__ring_sig_public_key = self.ring_sig_handler.key_pair.get('pk')
        self.__ring_sig_private_key = self.ring_sig_handler.key_pair.get('sk')
        # ring_sig_key_pair : first is pk, later is sk
        self.__ring_sig_key_pair = [self.__ring_sig_public_key, self.__ring_sig_private_key]

    def register_node(self, ip):
        form = {
            "ip": ip,
        }
        try:
            r = requests.post("http://" + POOL_URL + ":" + POOL_PORT + "/nodes/register", data=form)
            # todo submit pk to pk pool
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

    def gen_membership_proof(self, pks: list, msg):
        try:
            ring_sig = self.ring_sig_handler.ring_signaturer((pks, self.__ring_sig_key_pair), msg)
            return ring_sig
        except:
            print('client {} failed gen_membership_proof.'.format(self.__ip))

    def verify_ring_signature(self, sig, msg):
        try:
            self.ring_sig_handler.verify_ring_signature(sig, msg)
            return True
        except:
            print('invalid proof: {} for message {}.'.format(sig, msg))
            return False
