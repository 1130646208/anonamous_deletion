import requests

import json

r = requests.get('http://127.0.0.1:8000/transactions/all')

j = json.loads(r.text)

trans_str = j.get("transactions").replace('\'', '\"')
print(trans_str)
trans_dict = json.loads(trans_str)
print(trans_dict)




print(type(r.text), r.text)
