import time
from threading import Thread
import numpy as np
import pandas as pd
from tqdm import tqdm
from argparse import ArgumentParser
from client.client import Client

print('Initializing Clients...')
all_clients = []
for i in tqdm(range(100)):
    all_clients.append(Client())


def test_ring_sig_and_client_num(_N):
    clients = []
    for i in range(_N):
        clients.append(all_clients[i])
    client1 = clients[0]  # 负责将自己的秘密进行Shamir分享，并完成加密和环签名
    client2 = clients[2]  # 负责验证环签名

    ring_sig_pks = [client.ring_sig_public_key for client in clients]
    tik = time.time()

    proof = client1.gen_membership_proof(ring_sig_pks, 'this is a secret key: 893472693982376')
    assert client2.verify_ring_signature(proof, 'this is a secret key: 893472693982376')
    tok = time.time()

    return tok - tik


if __name__ == '__main__':
    t = []
    data = pd.DataFrame(columns=['N', 't'])
    for N in tqdm(range(20, 100, 2)):
        t.append(test_ring_sig_and_client_num(N))
    data['N'] = range(20, 100, 2)
    data['t'] = t
    data.to_csv('ring_sig_and_client_num'+'.csv')
