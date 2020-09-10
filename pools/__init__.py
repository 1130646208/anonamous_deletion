from .ip_pool import IPPool
from .tx_pool import TxPool
from .ring_sig_pk_pool import RingSigPKPool
from .rsa_pk_pool import RSAPKPool

POOL_URL = '127.0.0.1'
POOL_PORT = '8000'
public_ip_pool = IPPool()
public_tx_pool = TxPool()
public_ring_sig_pk_pool = RingSigPKPool()
public_rsa_pk_pool = RSAPKPool()
