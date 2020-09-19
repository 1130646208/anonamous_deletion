#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2020/9/7 0:17
# @Author  : wsx
# @File    : my_ringsig_test.py
# @Software: PyCharm
# @Function: ...


from ring_signature.pysolcrypto.curve import randsn
from ring_signature.pysolcrypto.aosring import aosring_randkeys, aosring_check, aosring_sign


def test_aos():
    msg = randsn()
    keys = aosring_randkeys(4)
    pk, sk = keys
    print("pk {}, sk {}".format(pk, sk))
    sig = aosring_sign(*keys, message=msg)
    print("sig", sig)
    assert(aosring_check(*sig, message=msg))


if __name__ == "__main__":
    test_aos()
