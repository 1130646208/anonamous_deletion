import hashlib
import json


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
