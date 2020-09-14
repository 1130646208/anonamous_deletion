import hashlib
import time
import random
from typing import Dict
import base64 as b64

from helpers import reconstruct_ring_sig
from ring_signature.ring_signature_handler import RingSigHandler

MAX_TRANSACTIONS_LIMIT = 100


class TxPool:
    """
    交易池中存储的交易是字典类型的，在客户端处理时再转化成OrderedDict
    """
    def __init__(self):
        # tx looks like {'a_member_proof': 'some_tx(Dict)'}
        # because txs is a dict, so 'a_member_proof' can not be the same
        self.txs = dict()

        self.max_transactions_limit = MAX_TRANSACTIONS_LIMIT

    @property
    def txs_num(self):
        return len(self.txs)

    @property
    def txs_list(self):
        tl = []
        for k, v in self.txs.items():
            tl.append(dict({k: v}))
        return tl

    def add_tx(self, member_proof, new_tx: Dict):
        """
        type can be:
        txdata txdelete
        txdata:Dict({'transaction_id': '', 'transaction_type': 'txdata', 'content': 'encrypted_secret', 'timestamp': 'time...'})
        txdelete: Dict({'transaction_id': '', 'transaction_type': 'txdelete', 'content': 'encrypted_secret', 'timestamp': 'time...'})
        """

        if self._check_tx(new_tx):
            self.txs[member_proof] = new_tx
        else:
            raise ValueError("添加的交易不合法")

    def submit_transaction(self, membership_proof: str, transaction_type, content) -> bool:
        """
        Add a transaction to public transaction pool
        make transaction id unique
        """
        msg_digest = hashlib.md5(content.encode()).digest()
        msg_in_int = int.from_bytes(msg_digest, byteorder='big')
        assert self.verify_transaction_membership(membership_proof, msg_in_int)

        salt = random.randint(1, 500)
        current_time = time.time_ns()
        transaction_id = hashlib.md5(str(current_time + salt).encode()).hexdigest()
        transaction = {"transaction_id": transaction_id,
                       "transaction_type": transaction_type,
                       "content": content,
                       "timestamp": str(current_time)}

        if self.txs_num < self.max_transactions_limit:
            membership_proof_encoded = b64.b64encode(membership_proof.encode())
            self.add_tx(str(membership_proof_encoded), transaction)
            return True

        return False

    def verify_transaction_membership(self, proof: str, msg):
        """
        verify a whether transaction's membership_proof is valid or not
        :return:
        """
        membership_proof_raw = eval(proof)
        reconstructed_proof = reconstruct_ring_sig(membership_proof_raw)
        try:
            RingSigHandler.verify_ring_signature(reconstructed_proof, msg)
            return True
        except:
            return False

    @property
    def sorted_txs(self, by='timestamp'):
        """
        将txs中的交易，按照交易的‘by’字段进行排序，如：
        排序前{'proof1': Dict([('transaction_id', '',), ('transaction_type', 'txdata'), ('content', 'encrypted_secret'), ('timestamp', '123')]), 'proof2': OrderedDict([('transaction_type', 'txdata'), ('content', 'encrypted_secret'), ('timestamp', '12')])}
        排序后{'proof2': Dict([('transaction_id', '',), ('transaction_type', 'txdata'), ('content', 'encrypted_secret'), ('timestamp', '12')]), 'proof1': OrderedDict([('transaction_type', 'txdata'), ('content', 'encrypted_secret'), ('timestamp', '123')])}
        :param by:
        :return:
        """
        sorted_list = sorted(self.txs.items(), key=lambda x: x[1][by], reverse=False)
        return dict(sorted_list)

    @staticmethod
    def _check_tx(tx):
        """
        检查交易字段是否合法
        :param tx:
        :return:
        """
        if 'transaction_type' not in tx.keys():
            print('未指定交易类型')
            return False

        # if not tx['transaction_id'] == hashlib.md5(tx['timestamp'].encode()).hexdigest():
        #     return False

        required = {
            'txdata': ['transaction_id', 'transaction_type', 'content', 'timestamp'],
            'txdelete': ['transaction_id', 'transaction_type', 'content', 'timestamp']
        }

        if tx['transaction_type'] == 'txdata':
            if not len(tx.keys()) == len(required['txdata']):
                return False

            if not all(k in tx.keys() for k in required['txdata']):
                return False

        if tx['transaction_type'] == 'txdelete':
            if not len(tx.keys()) == len(required['txdelete']):
                return False

            if not all(k in tx.keys() for k in required['txdata']):
                return False

        return True

    def fetch_a_tx(self, valid_proof):
        """
        TAKE OUT a transaction from the tx pool
        :return:
        """
        return self.txs.pop(valid_proof)

    def drop_a_tx(self, tx_id):
        """
        DROP OUT a transaction from the tx pool
        :return:
        """
        for k, v in self.txs.items():
            if v.get('transaction_id') == tx_id:
                self.txs.pop(k)
            break

    def return_txs(self, return_num=0) -> list:
        """
        return txs to client to pack into block chain
        if return_num == -1 return all txs
        :return:
        """
        tx_to_return = []
        if return_num == 0:
            for i in range(0, self.txs_num):
                tx_to_return.append(self.txs_list[i])
        else:
            for i in range(0, return_num):
                tx_to_return.append(self.txs_list[i])
        return tx_to_return

    def drop_some_txs(self, tx_ids: list):
        for tx_id in tx_ids:
            self.drop_a_tx(tx_id)
