import rsa
import rsa.common
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

    def rsa_enc_long_bytes(self, bytes_str, pub_key):
        if not isinstance(bytes_str, bytes):
            return None
            # 导入rsa库
        import rsa.common
        key_length = rsa.common.byte_size(pub_key['n'])
        max_msg_length = key_length - 11

        count = len(bytes_str) // max_msg_length
        if len(bytes_str) % max_msg_length > 0:
            count = count + 1
        cry_bytes = b''
        # rsa加密要以max_msg_length分组, 每组分别加密(加密的数据长度为key_length, 解密时每key_length长度解密然后相加)
        for i in range(count):
            start = max_msg_length * i
            size = max_msg_length
            content = bytes_str[start: start + size]
            # rsa 分组 加密
            crypto = rsa.encrypt(content, pub_key)
            cry_bytes = cry_bytes + crypto

        return cry_bytes

    def rsa_dec_long_bytes(self, bytes_string, sk):
        # 导入rsa库
        import rsa.common
        key_length = rsa.common.byte_size(sk['n'])
        if len(bytes_string) % key_length != 0:
            # 如果数据长度不是key_length的整数倍, 则数据是无效的
            return None

        count = len(bytes_string) // key_length
        d_cty_bytes = b''
        # 分组解密
        for i in range(count):
            start = key_length * i
            size = key_length
            content = bytes_string[start: start + size]
            # rsa 分组 解密
            d_crypto = rsa.decrypt(content, sk)
            d_cty_bytes = d_cty_bytes + d_crypto
        return d_cty_bytes

