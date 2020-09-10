from hashlib import md5
import json
import requests

from crypto_rsa.crypto_rsa import RSAHandler
from helpers import str_vector_to_tuple, tuple_vector_to_str, int_to_bn128_FQ
from pools import POOL_URL, POOL_PORT
from ring_signature.ring_signature_handler import RingSigHandler
from .block_chain import BlockChain


class Client:

    def __init__(self, ip=None):
        self.chain = BlockChain()
        self.__ring_sig_handler = RingSigHandler()
        self.__rsa_handler = RSAHandler()
        self.__ip = ip

        # rsa_public_key is type :rsa.key.PublicKey
        self.rsa_public_key = self.__rsa_handler.key_pair.get('pk')
        # 'ring_sig_public_key'虽然能够正确注册，看起来是tuple类型，但是其中含有bn128_FQ类型的数据
        self.ring_sig_public_key = self.__ring_sig_handler.key_pair.get('pk')
        self.__ring_sig_private_key = self.__ring_sig_handler.key_pair.get('sk')
        # ring_sig_key_pair : first is pk tuple(int, int), later is sk (int)
        self.__ring_sig_key_pair = [self.ring_sig_public_key, self.__ring_sig_private_key]

    def register_node(self, ip: str, ring_sig_pk: tuple, rsa_pk: tuple):
        ring_sig_pk_str = tuple_vector_to_str([ring_sig_pk])
        rsa_pk_str = tuple_vector_to_str([rsa_pk])
        form = json.dumps({
            "ip": ip,
            "ring_sig_pk": ring_sig_pk_str,
            "rsa_pk": rsa_pk_str
        })
        try:
            r = requests.post("http://" + POOL_URL + ":" + POOL_PORT + "/nodes/register", json=form)
            print(r)
        except Exception as e:
            print("Client register error", e)

    def new_transaction(self, transaction_type: str, content: str):
        # 注意，这里的ring_sig_pks类型是[(int, int), (int, int)...]
        # 要转化成[(bn128_FQ, bn128_FQ), (bn128_FQ, bn128_FQ)...]
        # md卡了一天
        ring_sig_pks = []
        ring_sig_pks_raw = self.get_ring_sig_pks_from_pool()

        for pk_tuple in ring_sig_pks_raw:
            ring_sig_pks.append(tuple(int_to_bn128_FQ(xy) for xy in pk_tuple))

        membership_proof = self.gen_membership_proof(ring_sig_pks, content)

        form = json.dumps({
            "membership_proof": str(membership_proof),
            "transaction_type": transaction_type,
            "content": content
        })
        try:
            r = requests.post("http://" + POOL_URL + ":" + POOL_PORT + "/transactions/new", json=form)
            print(r)
        except Exception as e:
            print("client submit transaction error", e)

    def gen_membership_proof(self, pks: list, msg: str):
        msg_digest = md5(msg.encode()).digest()
        msg_in_int = int.from_bytes(msg_digest, byteorder='big')
        try:
            ring_sig = self.__ring_sig_handler.ring_signature((pks, self.__ring_sig_key_pair), msg=msg_in_int)
            return ring_sig

        except:
            print('client {} failed gen_membership_proof.'.format(self.__ip))
        return None

    def verify_ring_signature(self, sig, msg: str):
        msg_digest = md5(msg.encode()).digest()
        msg_in_int = int.from_bytes(msg_digest, byteorder='big')
        try:
            self.__ring_sig_handler.verify_ring_signature(sig, msg_in_int)
            return True

        except:
            print('Invalid proof: {} for message {}.'.format(sig, msg))
            return False

    @staticmethod
    def get_ring_sig_pks_from_pool() -> list:
        r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/nodes/ring_sig_key")
        if not r.status_code == 201:
            return []

        return str_vector_to_tuple(r.text)

    @staticmethod
    def get_rsa_pks_from_pool() -> list:
        r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/nodes/rsa_pub_key")
        if not r.status_code == 201:
            return []

        return str_vector_to_tuple(r.text)
