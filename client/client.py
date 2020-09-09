import requests, json
from hashlib import md5
import binascii

from helpers import str_vector_to_tuple, tuple_vector_to_str
from .block_chain import BlockChain
from pools import POOL_URL, POOL_PORT
from ring_signature.ring_signature_handler import RingSigHandler
from crypto_rsa.crypto_rsa import RSAHandler


class Client:

    def __init__(self, ip=None):
        self.chain = BlockChain()
        self.__ring_sig_handler = RingSigHandler()
        self.__rsa_handler = RSAHandler()
        self.__ip = ip

        # rsa_public_key is type :rsa.key.PublicKey
        self.rsa_public_key = self.__rsa_handler.pk
        self.ring_sig_public_key = self.__ring_sig_handler.key_pair.get('pk')
        self.__ring_sig_private_key = self.__ring_sig_handler.key_pair.get('sk')
        # ring_sig_key_pair : first is pk tuple(int, int), later is sk (int)
        self.__ring_sig_key_pair = [self.ring_sig_public_key, self.__ring_sig_private_key]

    def register_node(self, ip, ring_sig_pk: tuple):
        ring_sig_pk_str = tuple_vector_to_str([ring_sig_pk])
        form = json.dumps({
            "ip": ip,
            "ring_sig_pk": ring_sig_pk_str
        })
        try:
            r = requests.post("http://" + POOL_URL + ":" + POOL_PORT + "/nodes/register", json=form)
            print(r)
        except Exception as e:
            print("client register error", e)

    def new_transaction(self, transaction_type: str, content: str):
        ring_sig_pks = self.get_ring_sig_pks_from_pool()
        membership_proof = self.gen_membership_proof(ring_sig_pks, content)
        form = json.dumps({
            "membership_proof": membership_proof,
            "transaction_type": transaction_type,
            "content": content
        })
        try:
            r = requests.post("http://" + POOL_URL + ":" + POOL_PORT + "/transactions/new", data=form)
            print(r)
        except Exception as e:
            print("client submit transaction error", e)

    def gen_membership_proof(self, pks: list, msg: str):
        msg_digest = md5(msg.encode()).digest()
        msg_in_int = int.from_bytes(msg_digest, byteorder='big')
        #try:
        ring_sig = self.__ring_sig_handler.ring_signaturer((pks, self.__ring_sig_key_pair), msg=msg_in_int)
        return ring_sig

        #except:
        print('client {} failed gen_membership_proof.'.format(self.__ip))
        return None

    def verify_ring_signature(self, sig, msg: str):
        msg_digest = md5(msg.encode()).digest()
        msg_in_int = int.from_bytes(msg_digest, byteorder='big')
        try:
            self.__ring_sig_handler.verify_ring_signature(sig, msg_in_int)
            return True

        except:
            print('invalid proof: {} for message {}.'.format(sig, msg))
            return False

    @staticmethod
    def get_ring_sig_pks_from_pool():
        r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/nodes/ring_sig_key")
        if not r.status_code == 201:
            return None

        return str_vector_to_tuple(r.text)
