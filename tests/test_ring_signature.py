from ring_signature.ring_signature_handler import RingSigHandler

rh1 = RingSigHandler()
sk1 = rh1.key_pair.get('sk')
pk1 = rh1.key_pair.get('pk')
print('sk:', type(sk1), 'pk:', type(pk1))
print('sk:', sk1, 'pk:', pk1)

rh2 = RingSigHandler()
sk2 = rh2.key_pair.get('sk')
pk2 = rh2.key_pair.get('pk')

rh3 = RingSigHandler()
sk3 = rh3.key_pair.get('sk')
pk3 = rh3.key_pair.get('pk')

pkx = (pk1[1], pk1[0])

# todo 简化环签名
sig = rh1.ring_signature(([pk2, pk1, pk3], [pk1, sk1]), 123)
sig2 = rh1.ring_signature(([pk2, pk1, pk3], [pk1, sk1]), 123)
sig3 = rh2.ring_signature(([pk2, pk1, pk3], [pk2, sk2]), 123)
# 环签名返回的是pks, tees, cees.
# 大家的环签名第一部分都是一样的，不用担心身份泄露
print(sig)
print(sig2)
print(sig3)

# 不同的人可以验证某一个人的签名
rh3.verify_ring_signature(sig, 123)
rh2.verify_ring_signature(sig2, 123)
rh1.verify_ring_signature(sig3, 123)


rh3.verify_ring_signature(sig3, 123)
rh2.verify_ring_signature(sig2, 123)
rh1.verify_ring_signature(sig, 123)


