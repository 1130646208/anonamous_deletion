from client import client
import base64 as b64
a = client.Client()
pieces = a.split_secret(b64.b64encode(b'982713567005385676506450989333'), 5, 8)
print(pieces)

recovered = a.recover_secret(pieces[3:8])
print(recovered)
