import hashlib
import time
import random
from typing import Dict
import base64 as b64
from copy import deepcopy

from helpers import reconstruct_ring_sig
from ring_signature.ring_signature_handler import RingSigHandler

MAX_TRANSACTIONS_LIMIT = 100


class TxPool:
    """
    交易池中存储的交易是字典类型的，在客户端处理时再转化成OrderedDict
    """

    def __init__(self):
        # tx looks like {'a_member_proof': 'some_tx(Dict)'}
        # because txs_in is a dict, so 'a_member_proof' can not be the same
        self.txs_in = []
        self.txs_out = []
        self.max_transactions_limit = MAX_TRANSACTIONS_LIMIT

    @property
    def txs_in_num(self):

        return len(self.txs_in)

    @property
    def txs_out_num(self):

        return len(self.txs_out)

    def add_tx(self, new_tx: Dict):
        """
        new_tx can be:
        txdata:Dict({'proof': '', 'transaction_id': '', 'transaction_type': 'txdata', 'content': 'encrypted_secret', 'timestamp': 'time...'})
        txdelete: Dict({'proof': '', 'transaction_id': '', 'transaction_type': 'txdelete', 'content': 'encrypted_secret', 'timestamp': 'time...'})
        """
        if self._check_tx(new_tx):
            self.txs_in.append(new_tx)
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
        membership_proof_encoded = b64.b64encode(membership_proof.encode())
        # transaction = {"membership_proof": str(membership_proof_encoded),
        #                "transaction_id": transaction_id,
        #                "transaction_type": transaction_type,
        #                "content": content,
        #                "timestamp": str(current_time)}

        transaction = {"membership_proof": 'omitted',
                       "transaction_id": transaction_id,
                       "transaction_type": transaction_type,
                       "content": content,
                       "timestamp": str(current_time)}

        if self.txs_in_num < self.max_transactions_limit:
            self.add_tx(transaction)
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
        sorted_list = sorted(self.txs_out, key=lambda x: x[by], reverse=False)
        return sorted_list

    @staticmethod
    def _check_tx(tx: dict):
        """
        检查交易字段是否合法
        :param tx:
        :return:
        """
        if 'transaction_type' not in tx.keys():
            print('Undefined transaction type.')
            return False

        if 'membership_proof' not in tx.keys():
            print('No transaction proof found.')
            return False

        # if not tx['transaction_id'] == hashlib.md5(tx['timestamp'].encode()).hexdigest():
        #     return False
        required = {
            'txdata': ['membership_proof', 'transaction_id', 'transaction_type', 'content', 'timestamp'],
            'txdelete': ['membership_proof', 'transaction_id', 'transaction_type', 'content', 'timestamp'],
            'txrecover': ['membership_proof', 'transaction_id', 'transaction_type', 'content', 'timestamp']
        }

        if tx['transaction_type'] == 'txdata':
            if not len(tx.keys()) == len(required['txdata']):
                print('Illegal txdata transaction.')
                return False

            if not all(k in tx.keys() for k in required['txdata']):
                print('Illegal txdata transaction.')
                return False

        elif tx['transaction_type'] == 'txdelete':
            if not len(tx.keys()) == len(required['txdelete']):
                print('Illegal txdelete transaction.')
                return False

            if not all(k in tx.keys() for k in required['txdelete']):
                print('Illegal txdelete transaction.')
                return False

        elif tx['transaction_type'] == 'txrecover':
            if not len(tx.keys()) == len(required['txrecover']):
                print('Illegal txdata transaction.')
                return False

            if not all(k in tx.keys() for k in required['txrecover']):
                print('Illegal txdata transaction.')
                return False
        else:
            return False

        return True

    def drop_a_tx(self, tx_id):
        """
        DROP OUT a transaction from the tx pool
        :return:
        """
        for tx in self.txs_out:
            if tx.get('transaction_id') == tx_id:
                self.txs_out.pop(self.txs_out.index(tx))
                break

    def return_txs(self) -> list:
        """
        return txs_in to client to pack into block chain
        :return:
        """
        # transfer txs before return tx
        self.transfer_txs()

        tx_to_return = []
        tx_to_return.extend(self.txs_out)
        self.txs_out.clear()
        return tx_to_return

    def drop_some_txs(self, tx_ids: list):
        for tx_id in tx_ids:
            self.drop_a_tx(tx_id)

        # transfer txs after drop packed txs
        # self.transfer_txs()

    def transfer_txs(self):
        """
        transfers txs from txs_in to txs_out when txs_out is empty
        :return:
        """
        if not self.txs_out:
            self.txs_out = deepcopy(self.txs_in)
            self.txs_in.clear()
