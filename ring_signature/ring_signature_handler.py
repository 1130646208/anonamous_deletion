from ring_signature.pysolcrypto.curve import randsn
from ring_signature.pysolcrypto.aosring import aosring_randkeys, aosring_check, aosring_sign, sbmul


class RingSigHandler:
    def __init__(self):
        self.__key_pair = self.__gen_key_pair()
        self.__sk = self.__key_pair[1]
        self.__pk = self.__key_pair[0]
        self.key_pair = {'pk': self.__pk, 'sk': self.__sk}

    def __gen_key_pair(self):
        skey = randsn()
        pkey = sbmul(skey)
        return pkey, skey

    def ring_signaturer(self, keys, msg):
        ring_sig = aosring_sign(*keys, message=msg)
        return ring_sig

    @staticmethod
    def verify_ring_signature(sig, msg):
        assert aosring_check(*sig, message=msg)

