import hashlib
import json
from collections import OrderedDict

from py_ecc.fields import bn128_FQ
from py_ecc.fields.field_properties import field_properties
from rsa.key import PublicKey


def get_block_hash(block: dict):
    """
    Create a SHA-256 hash of a block
    """
    # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
    block_string = json.dumps(block, sort_keys=True).encode()

    return hashlib.sha256(block_string).hexdigest()


def str_vector_to_tuple(str_vec: str) -> list:
    """
    converts format: '123,4564;1987,654;...' to format [tuple(int, int), tuple(int, int)...]
    :param str_vec:
    :return:
    """
    pks_in_tuple = []
    xy_xy = str_vec.split(';')[:-1]
    for xy in xy_xy:
        pks_in_tuple.append(tuple([int(item) for item in xy.split(',')]))

    return pks_in_tuple


def tuple_vector_to_str(vector: list) -> str:
    """
    converts format: [tuple(int, int) tuple(int, int)] to format '123,346;462,34569;'
    :param vector:
    :return:
    """
    vec_str = ''
    temp = []
    for _tuple in vector:
        for xy in _tuple:
            temp.append(str(xy))
        vec_str += ','.join(temp)
        vec_str += ';'
        temp.clear()

    return vec_str


def rsa_pk_to_tuple(rsa_pk):
    return rsa_pk['n'], rsa_pk['e']


def int_to_bn128_FQ(int_num: int) -> bn128_FQ:
    bn128_FQ.field_modulus = field_properties["bn128"]["field_modulus"]
    return bn128_FQ(int_num)


def reconstruct_ring_sig(sig: tuple):
    # sig looks like
    # ([(x, y), (x, y), (x, y)], [a, b, c], d) that x, y is type of bn128_FQ
    reconstructed = [[]]
    for pk in sig[0]:
        reconstructed[0].append(tuple([int_to_bn128_FQ(xy) for xy in pk]))

    reconstructed.append(sig[1])
    reconstructed.append(sig[2])
    return tuple(reconstructed)


def reconstruct_rsa_pk(pk: tuple):
    return PublicKey(pk[0], pk[1])


def strip_secret(wrapped_decrypted: bytes) -> tuple:
    has_equator = True
    secret_r_bound_index = 0
    try:
        secret_r_bound_index = wrapped_decrypted.index(b'=')
    except:
        # 没有‘=’
        has_equator = False
        return None, wrapped_decrypted

    if has_equator:
        while wrapped_decrypted[secret_r_bound_index] == 61:
            if secret_r_bound_index < len(wrapped_decrypted) - 1:
                secret_r_bound_index += 1
            else:
                break
        # 在最后几个
        if secret_r_bound_index == len(wrapped_decrypted) - 1:
            return None, wrapped_decrypted

        else:
            other_secrets = wrapped_decrypted[:secret_r_bound_index]
            wanted_secret = wrapped_decrypted[secret_r_bound_index:]
            return other_secrets, wanted_secret


def get_transactions_ids(transactions: list):
    # transactions looks like
    # [{"id": 1, "type": "1234"}, {"id": 2, "type": "12345"}, {"id": 3, "type": "12346"}]
    transactions_ids = []
    for transaction in transactions:
        transaction_id = transaction.get("transaction_id")
        transactions_ids.append(transaction_id)

    return transactions_ids


def tx_list_to_ordered(transactions: list) -> list:
    transaction_elements = ['sender_address', 'recipient_address', 'value']
    transactions_ordered = [OrderedDict((k, transaction[k]) for k in transaction_elements) for transaction in
                            transactions]
    return transactions_ordered
