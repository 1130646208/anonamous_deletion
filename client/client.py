from hashlib import md5
import json
import requests
import base64 as b64
from rsa.key import PrivateKey

from crypto_rsa.crypto_rsa import RSAHandler
from ring_signature.ring_signature_handler import RingSigHandler
from secret_sharing import Base64ToHexSecretSharer
from helpers import str_vector_to_tuple, tuple_vector_to_str, int_to_bn128_FQ, reconstruct_rsa_pk, strip_secret, \
    get_transactions_ids, tx_list_to_ordered
from pools import POOL_URL, POOL_PORT
from .block_chain import BlockChain


class Client:

    def __init__(self, ip: str = None):
        self.block_chain = BlockChain()
        self.__ring_sig_handler = RingSigHandler()
        self.rsa_handler = RSAHandler()
        self.b2hss = Base64ToHexSecretSharer()
        self.ip = ip

        # register variables
        self.rsa_public_key_tuple = self.rsa_handler.pk_tuple
        self.rsa_public_key_origin = self.rsa_handler.key_pair.get('pk')
        self.rsa_public_key_origin = self.rsa_handler.key_pair.get('pk')
        # test
        self.rsa_private_key_origin = self.rsa_handler.key_pair.get('sk')

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
            print("Client {} says: registered, response from pool is {}.".format(ip, r))
        except Exception as e:
            print("Client {} says register error {}.".format(ip, e))

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
            print("Client {} says: transaction submitted, response from pool is {}.".format(self.ip, r))
        except Exception as e:
            print("Client {} says: transaction submit error.".format(self.ip, e))

    def gen_membership_proof(self, pks: list, msg: str):
        msg_digest = md5(msg.encode()).digest()
        msg_in_int = int.from_bytes(msg_digest, byteorder='big')
        try:
            ring_sig = self.__ring_sig_handler.ring_signature((pks, self.__ring_sig_key_pair), msg=msg_in_int)
            return ring_sig

        except:
            print('Client {} failed gen_membership_proof.'.format(self.ip))
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
        tuple_rsa_pk = str_vector_to_tuple(r.text)
        return [reconstruct_rsa_pk(pk) for pk in tuple_rsa_pk]

    def split_secret(self, secret: bytes, threshold: int, total: int) -> list:
        # b'aGVsbG8gISEhIHNlY3JldCBzaGFyZSEhIQ===='(bytes) -> 'aGVsbG8gISEhIHNlY3JldCBzaGFyZSEhIQ'(str)
        """
        :param secret: base64 format
        :param threshold:
        :param total:
        :return:
        """

        secret_striped = str(secret)[2:-1].rstrip("=")
        return self.b2hss.split_secret(secret_striped, threshold, total)

    def recover_secret(self, shares: list) -> bytes:
        """
        recovery a secret from shamir pieces
        :param shares:
        :return: base64 format
        """

        secret_string = self.b2hss.recover_secret(shares)
        secret_b64 = bytes(secret_string.encode()) + b"===="
        return secret_b64

    def get_obliged_secrets(self):
        """
        find secrets that are supposed to be stored by me.
        :return:
        """
        # 记录完成交易的ID
        succeed_tx_ids = []
        decrypted_secret = None
        for block in self.block_chain.chain:
            transactions = block.get("transactions")
            if transactions:
                for transaction in transactions:
                    encrypted_secret = transaction.get("content")
                    tx_id = transaction.get("transaction_id")
                    if encrypted_secret and tx_id:
                        try:
                            decrypted_secret = self.rsa_handler.rsa_dec_long_bytes(eval(encrypted_secret),
                                                                                   self.rsa_private_key_origin)
                            succeed_tx_ids.append(tx_id)
                            print("Got secret {} from tx {}.".format(decrypted_secret, tx_id))
                        except Exception:
                            print("Not the secret, continue...")
                            pass
            else:
                print("No tx in block {}.".format(block.get("block_number")))

    def encrypt_secrets_parallel(self, pks, secrets_to_be_encrypted):
        """
        encrypt a secret with a rsa pk
        :return:
        """
        assert (len(secrets_to_be_encrypted) == len(pks))
        enc_secrets = []
        for i in range(len(pks)):
            enc_secrets.append(self.rsa_handler.rsa_enc_long_bytes(secrets_to_be_encrypted[i], pks[i]))

        return enc_secrets

    def encrypt_secrets(self, pks: list, secrets_to_be_encrypted: list, is_secrets_encoded_b64: bool) -> bytes:
        """
        encrypt some secrets layer by layer. ATTENTION!! secret  can not be empty.
        :param is_secrets_encoded_b64:
        :param pks:
        :param secrets_to_be_encrypted:
        :return:
        """
        assert len(pks) == len(secrets_to_be_encrypted)
        result = b''
        secrets_encoded = []
        if not is_secrets_encoded_b64:
            secrets_encoded = [b64.b64encode(secret) for secret in secrets_to_be_encrypted]
        else:
            secrets_encoded = secrets_to_be_encrypted

        pks_iterable = iter(pks)
        secrets_encoded_iterable = iter(secrets_encoded)
        for times in range(len(pks)):
            result += next(secrets_encoded_iterable)
            temp_result = self.rsa_handler.rsa_enc_long_bytes(result, next(pks_iterable))
            temp_result_encoded = b64.b64encode(temp_result) + b'===='
            result = temp_result_encoded

        return result

    def get_a_secret_from_wrapped(self, wrapped: bytes, sk) -> tuple:
        """
        decrypt a wrapped secret, and returns remainder wrapped secrets and wanted secret
        :param sk:
        :param wrapped:
        :return:
        """
        if not isinstance(wrapped, bytes):
            print('Wrapped secret type error.', wrapped)
            return None, None

        if not isinstance(sk, PrivateKey):
            print('RSA private key type error.', wrapped)
            return None, None

        wrapped_decoded = b64.b64decode(wrapped)
        try:
            wrapped_decrypted = self.rsa_handler.rsa_dec_long_bytes(wrapped_decoded, sk)
            other_secrets, wanted_secret = strip_secret(wrapped_decrypted)
            return other_secrets, wanted_secret
        except:
            # 解密失败说明不是给自己的，直接return None
            return None, None

    def get_transactions_to_pack(self, num_to_get=0):
        r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/transactions/get")
        if not r.status_code == 201:
            print("Message from client.get_transactions_to_pack: unable to get transactions from pool.")

        else:
            txs_list_str = r.text
            # 从交易池获得来的交易排序一下
            # todo: delete 'sorted'
            txs_list = sorted(eval(txs_list_str), key=lambda x: x["transaction_id"])
            self.block_chain.transactions.extend(txs_list)
            print("Got transactions: {} to be mine...".format(str(txs_list)))

    def mine(self):
        packed_transactions_ids = get_transactions_ids(self.block_chain.transactions)

        proof = self.block_chain.proof_of_work()
        previous_hash = self.block_chain.hash_block(self.block_chain.last_block)
        new_block = self.block_chain.create_block(proof, previous_hash=previous_hash)
        # tell pool to drop txs_in
        form = json.dumps({
            "tx_ids": str(packed_transactions_ids)
        })

        is_drop_success = False
        r = requests.post("http://" + POOL_URL + ":" + POOL_PORT + "/transactions/drop", json=form)
        if r.status_code == 201:
            is_drop_success = True

        mine_message = {
            'message': "New Block Forged",
            'block_number': new_block['block_number'],
            'transactions': new_block['transactions'],
            'nonce': new_block['nonce'],
            'previous_hash': new_block['previous_hash'],
            'packed_transactions_ids': str(packed_transactions_ids),
            'pool_drop_txs': str(is_drop_success)
        }
        return mine_message
