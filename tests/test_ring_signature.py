from ring_signature.ring_signature_handler import RingSigHandler

rh1 = RingSigHandler()
sk1 = rh1.key_pair.get('sk')
pk1 = rh1.key_pair.get('pk')

rh2 = RingSigHandler()
sk2 = rh2.key_pair.get('sk')
pk2 = rh2.key_pair.get('pk')

rh3 = RingSigHandler()
sk3 = rh3.key_pair.get('sk')
pk3 = rh3.key_pair.get('pk')

rh4 = RingSigHandler()
sk4 = rh4.key_pair.get('sk')
pk4 = rh4.key_pair.get('pk')

# 环签名返回的是pks, tees, cees.
# 大家的环签名第一部分都是一样的，不用担心身份泄露
# todo 简化环签名
sig = rh1.ring_signaturer(([pk2, pk1, pk3, pk4], [pk1, sk1]), 123)
sig2 = rh1.ring_signaturer(([pk2, pk1, pk3, pk4], [pk1, sk1]), 123)
sig3 = rh2.ring_signaturer(([pk2, pk1, pk3, pk4], [pk2, sk2]), 123)
print(sig)
print(sig2)
print(sig3)
rh3.verify_ring_signature(sig, 123)
rh2.verify_ring_signature(sig, 123)
rh1.verify_ring_signature(sig, 123)
rh4.verify_ring_signature(sig, 123)

rh3.verify_ring_signature(sig2, 123)
rh2.verify_ring_signature(sig2, 123)
rh1.verify_ring_signature(sig2, 123)
rh4.verify_ring_signature(sig2, 123)
