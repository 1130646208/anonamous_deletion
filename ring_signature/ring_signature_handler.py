from ring_signature.pysolcrypto.curve import randsn
from ring_signature.pysolcrypto.aosring import aosring_randkeys, aosring_check, aosring_sign, sbmul


class RingSigHandler:
    def __init__(self):
        self.__pk, self.__sk = self.__gen_key_pair()
        # 'key_pair' for internal or Client call, also for web transfer
        self.key_pair = {'pk': self.__pk, 'sk': self.__sk}
        # TODO: self.pk for web transfer

    @staticmethod
    def __gen_key_pair():
        skey = randsn()
        pkey = sbmul(skey)
        return pkey, skey

    @staticmethod
    def ring_signature(keys, msg):
        ring_sig = aosring_sign(*keys, message=msg)
        return ring_sig

    @staticmethod
    def verify_ring_signature(sig, msg):
        assert aosring_check(*sig, message=msg)
