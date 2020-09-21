
MAX_IP_NUM_LIMIT = 10000


class TxDonePool:

    def __init__(self):
        self.txs_done = set()
        self.max_tx_num_limit = MAX_IP_NUM_LIMIT

    @property
    def tx_done_num(self):
        return len(self.txs_done)

    def add_tx(self, txs_done: list):
        for tx in txs_done:
            self.txs_done.add(tx)

    def submit_txs_done(self, txs_done: list):
        if self.tx_done_num < self.max_tx_num_limit:
            self.add_tx(txs_done)
            return True
        return False

    def get_all_txs_done(self):
        return list(self.txs_done)

