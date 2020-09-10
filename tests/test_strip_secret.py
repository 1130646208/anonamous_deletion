import rsa
from helpers import strip_secret
import base64 as b64
from crypto_rsa.crypto_rsa import RSAHandler

pk1, sk1 = rsa.newkeys(512)
pk2, sk2 = rsa.newkeys(512)
pk3, sk3 = rsa.newkeys(512)
# ascii only
data1 = b64.b64encode(b'1')
data2 = b64.b64encode(b'2')
data3 = b64.b64encode(b'3')
# data1 = '2345'.encode()
# data2 = '2436'.encode()
# data3 = '235126'.encode()

r = RSAHandler(512)
result = r.encrypt_secrets([pk1, pk2, pk3], [data1, data2, data3], True)
print(result)

other, wanted = r.get_a_secret_from_wrapped(result, sk3)
print(other, b64.b64decode(wanted))

other, wanted2 = r.get_a_secret_from_wrapped(other, sk2)
print(other, b64.b64decode(wanted2))

other, wanted3 = r.get_a_secret_from_wrapped(other, sk1)
if not other:
    print('the last secret!!')
print(b64.b64decode(wanted3))

