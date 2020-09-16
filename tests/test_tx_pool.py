from pools.origin_tx_pool import TxPool
from collections import OrderedDict
import hashlib
import time

pool = TxPool()
time1 = time.time_ns()
pool.add_tx('proof1', OrderedDict({'transaction_id': hashlib.md5(str(time1).encode()).hexdigest(),
                                   'transaction_type': 'txdata',
                                   'content': 'encrypted_secret1',
                                   'timestamp': str(time1),
                                   }))

time.sleep(0.1)
time2 = time.time_ns()
pool.add_tx('proof2', OrderedDict({'transaction_id': hashlib.md5(str(time2).encode()).hexdigest(),
                                   'transaction_type': 'txdata',
                                   'content': 'encrypted_secret2',
                                   'timestamp': str(time2),
                                   }))

time.sleep(0.1)
time3 = time.time_ns()
pool.add_tx('proof3', OrderedDict({'transaction_id': hashlib.md5(str(time3).encode()).hexdigest(),
                                   'transaction_type': 'txdelete',
                                   'content': 'encrypted_secret3',
                                   'timestamp': str(time3),
                                   }))

print(pool.txs_in)
print(pool.sorted_txs)

pool.drop_a_tx('proof1')
print(pool.sorted_txs)
