import rsa
import base64 as b64
from crypto_rsa.crypto_rsa import RSAHandler

pk1, sk1 = rsa.newkeys(1024)
pk2, sk2 = rsa.newkeys(1024)
pk3, sk3 = rsa.newkeys(1024)
data1 = b64.b64encode(b'hello1')
data2 = b64.b64encode(b'hello2')
data3 = b64.b64encode(b'hello3')
#
r = RSAHandler()
enc1 = b64.b64encode(r.rsa_enc_long_bytes(data1, pk1))
print('一层加密', enc1)
#
temp = enc1 + data2
#
enc2 = b64.b64encode(r.rsa_enc_long_bytes(temp, pk2))

print('二层加密', enc2)

enc2_d = r.rsa_dec_long_bytes(b64.b64decode(enc2), sk2)
print('第二层解密之后（第一层数据）：', enc2_d)

index = enc2_d.rfind(b'=')
data2 = enc2_d[index+1:]

missing_padding = 4 - len(data2) % 4
if missing_padding:
    data2 += b'=' * missing_padding
print(b64.b64decode(data2))

# r = RSAHandler()
# msg = b'IiWZlcYIYNT1wOdObw4/EcQy2OwA9tlwDSeGhgMLtukcg8nT1jjAeZx7tkAGblhUSk3bs+78YsaP51N3nMc0l26BqBn86CGYFZlYOkR4YDOdPxvPsIAH7mO6kpOCSu1bp9iNSkuE7Ps5DTWOhE4m+L2cpPkojEd5WIP0DsXSW7s='
# c = r.rsa_enc_long_bytes(msg, r.pk)
# print(c)
# d = r.rsa_dec_long_bytes(c)
# print(d)
# assert msg == d
