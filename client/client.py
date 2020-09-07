import requests
from hashlib import md5

from .block_chain import BlockChain
from pools import POOL_URL, POOL_PORT
from ring_signature.ring_signature_handler import RingSigHandler


class Client:

    def __init__(self, ip=None):
        self.chain = BlockChain()
        self.__ring_sig_handler = RingSigHandler()
        self.__ip = ip
        self.__rsa_public_key = None
        self.__rsa_private_key = None

        self.ring_sig_public_key = self.__ring_sig_handler.key_pair.get('pk')
        self.__ring_sig_private_key = self.__ring_sig_handler.key_pair.get('sk')
        # ring_sig_key_pair : first is pk, later is sk
        self.__ring_sig_key_pair = [self.ring_sig_public_key, self.__ring_sig_private_key]

    def register_node(self, ip, ring_sig_pk: tuple):
        form = {
            "ip": ip,
            "ring_sig_pk": ring_sig_pk
        }
        try:
            r = requests.post("http://" + POOL_URL + ":" + POOL_PORT + "/nodes/register", data=form)
            print(r)
        except Exception as e:
            print("client register error", e)

    def new_transaction(self, ring_sig_pks, transaction_type, content: str):

        membership_proof = self.gen_membership_proof(ring_sig_pks, content)
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

    def gen_membership_proof(self, pks: tuple, msg: str):
        msg_digest = md5(msg.encode()).digest()
        msg_in_int = int.from_bytes(msg_digest, byteorder='big')
        try:
            ring_sig = self.__ring_sig_handler.ring_signaturer((pks, self.__ring_sig_key_pair), msg_in_int)
            return ring_sig

        except:
            print('client {} failed gen_membership_proof.'.format(self.__ip))
            return False

    def verify_ring_signature(self, sig, msg: str):
        msg_digest = md5(msg.encode()).digest()
        msg_in_int = int.from_bytes(msg_digest, byteorder='big')
        try:
            self.__ring_sig_handler.verify_ring_signature(sig, msg_in_int)
            return True

        except:
            print('invalid proof: {} for message {}.'.format(sig, msg))
            return False
