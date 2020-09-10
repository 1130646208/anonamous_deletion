import rsa
import base64 as b64
from crypto_rsa.crypto_rsa import RSAHandler

from helpers import strip_secret

pk1, sk1 = rsa.newkeys(512)
pk2, sk2 = rsa.newkeys(512)
pk3, sk3 = rsa.newkeys(512)

r = RSAHandler()
data1 = b64.b64encode(b'secret1: wangshuangxing~')
data2 = b64.b64encode(b'secret2: fengyue@')
data3 = b64.b64encode(b'secret3: good!')

# enc1 = b64.b64encode(r.rsa_enc_long_bytes(data1, pk1))
# print('一层加密', enc1)
# temp = enc1 + data2
# enc2 = b64.b64encode(r.rsa_enc_long_bytes(temp, pk2))
#
# print('二层加密', enc2)
#
# enc2_d = r.rsa_dec_long_bytes(b64.b64decode(enc2), sk2)
# print('第二层解密之后（第一层数据）：', enc2_d)
#
# index = enc2_d.rfind(b'=')
# data2 = enc2_d[index+1:]
#
# missing_padding = 4 - len(data2) % 4
# if missing_padding:
#     data2 += b'=' * missing_padding
# print(b64.b64decode(data2))

# 多层加密
result = r.encrypt_secrets([pk1, pk2], [data1, data2], True)
print('result:', result)
# 逐层解密
# 先decode
result_decoded = b64.b64decode(result)
print('result_decoded:', result_decoded)
# 再解密
result2 = r.rsa_dec_long_bytes(result_decoded, sk2)
print('result2:', result2)
# 取出秘密
secret2 = strip_secret(result2)[1]
print(b64.b64decode(secret2))
# 解码秘密
result2_decoded = b64.b64decode(result2)
# 剩下的密文，重复上述操作
result3 = strip_secret(result2)[0]
print(result3)
# 第二轮，先解码
result3_decoded = b64.b64decode(result3)
print(result3_decoded)
# 再解密
result4 = r.rsa_dec_long_bytes(result3_decoded, sk1)
print(b64.b64decode(result4))

