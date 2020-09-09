import rsa
from Crypto.Cipher import AES


class RSAHandler:
    def __init__(self, bit_num=1024):
        self.pk, self.__sk = rsa.newkeys(bit_num)

    def rsa_encrypt(self, plain_text: str) -> bytes:
        plain_text_encoded = plain_text.encode()
        cipher_encoded = rsa.encrypt(plain_text_encoded, self.pk)
        print(type(cipher_encoded))
        return cipher_encoded

    def rsa_decrypt(self, cipher: bytes) -> str:
        plain_text_encoded = rsa.decrypt(cipher, self.__sk)
        return plain_text_encoded.decode()
