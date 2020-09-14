import json

# d = {"a": 1, "b": 2, "d": 3, "c": 4, "e": {"g": 2, "f": 3}}
# # 排序键值会把字典里面的字典的键值也排序
# print(json.dumps(d, sort_keys=True))

# ####################

a = [{'a': {"id": 1, "transaction_id": "1234"}}, {'b': {"id": 2, "transaction_id": "12345"}}, {'c': {"id": 3, "transaction_id": "12346"}}]

# for i in a:
#     transaction = list(i.values())[0]
#     i_d = transaction.get('id')
#     print(i_d)
from helpers import get_transactions_ids
b = get_transactions_ids(a)
print(b)
