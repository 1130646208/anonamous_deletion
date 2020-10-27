import math

from rsa import DecryptionError
from client.client import Client
import base64 as b64
import random
import time
from threading import Thread
import numpy as np
import pandas as pd
from tqdm import tqdm
from argparse import ArgumentParser

print('Initializing Clients...')
all_clients = []
for i in tqdm(range(100)):
    all_clients.append(Client())


def test_hide_performance(N, n, k):
    secret = 'this is a secret key: 893472693982376'.encode()

    _N = N
    clients = []

    for i in range(_N):
        clients.append(all_clients[i])

    ring_sig_pks = [client.ring_sig_public_key for client in clients]
    rsa_pks = [client.rsa_public_key_origin for client in clients]

    client1 = clients[0]  # 负责将自己的秘密进行Shamir分享，并完成加密和环签名
    client2 = clients[2]  # 负责验证环签名

    # 1 Shamir秘密分享
    _n = n
    _k = k
    print('Start.# 1 Shamir Secret Sharing...')
    tik1 = time.time()
    secret_pieces = [item.encode() for item in client1.split_secret(b64.b64encode(secret), _k, _n)]

    # 2 加密分片
    print('Start.# 2 RSA encrypting Secret pieces...')
    secrets_to_hide = client1.encrypt_secrets_parallel(random.sample(rsa_pks, _n), secret_pieces)

    # 3 生成环签名&验证环签名
    print('Start.# 3 Ring Signature and Verify...')
    proofs = []
    for item in secrets_to_hide:
        proof = client1.gen_membership_proof(ring_sig_pks, str(item))
        client2.verify_ring_signature(proof, str(item))
        proofs.append(proof)
    tok1 = time.time()

    # 找到并解密分片
    def go_through_and_dec(one_client: Client):
        secret_for_me = None
        for item in secrets_to_hide:
            try:
                secret_for_me = one_client.rsa_handler.rsa_dec_long_bytes(item, one_client.rsa_private_key_origin)
            except DecryptionError:
                pass

        return secret_for_me
        # print(one_client, 'got secret', secret_for_me)

    # 4创建解密线程,找到并解密分片
    print('Start.# 4 Clients Find Secrets...')
    client_threads = [Thread(target=go_through_and_dec, args=(client,)) for client in clients]

    tik2 = time.time()
    [thread.start() for thread in client_threads]
    [thread.join() for thread in client_threads]
    tok2 = time.time()

    time_consumed = tok1 - tik1 + tok2 - tik2
    print('Time consumed:', time_consumed)
    return time_consumed


if __name__ == '__main__':
    k_to_n = 0.4
    n_to_N = 0.4
    data = pd.DataFrame(columns=['N', 't'])
    data['N'] = range(20, 100, 2)
    t = []
    for N in tqdm(range(20, 100, 2)):
        n = math.ceil(N*n_to_N)
        k = math.ceil(n*k_to_n)
        t.append(test_hide_performance(N, n, max(2, k)))
    data['t'] = t
    print(data)
    data.to_csv('result_k_to_n_' + str(k_to_n) + '_n_to_N_' + str(n_to_N) + '.csv')
