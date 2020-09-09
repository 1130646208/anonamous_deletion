from crypto_rsa.crypto_rsa import RSAHandler

r = RSAHandler()
print(type(r.pk))
c = r.rsa_encrypt('哈哈')
p = r.rsa_decrypt(c)
print(c)
print(p)
