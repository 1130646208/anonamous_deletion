import json
import time
import hashlib
import requests
from uuid import uuid4
from urllib.parse import urlparse

from helpers import get_block_hash, tx_list_to_ordered
from pools import POOL_PORT, POOL_URL

MINING_DIFFICULTY = 2


class BlockChain:

    def __init__(self):

        self.transactions = []
        self.chain = []
        self.pool = []
        # Generate random number to be used as node_id
        self.node_id = str(uuid4()).replace('-', '')
        # Create genesis block
        self.create_block(1, 'This is genesis block.')

    @property
    def last_block(self):
        return self.chain[-1]

    @property
    def nodes(self):
        r = requests.get("http://" + POOL_URL + ":" + POOL_PORT + "/nodes/ip")
        if r.status_code == 201:
            nodes_ip = r.text.split(';')[:-1]
            return nodes_ip
        else:
            return []

    def register_node(self, node_url):
        """
        Add a new node to the list of nodes
        """
        # Checking node_url has valid format
        parsed_url = urlparse(node_url)
        if parsed_url.netloc:
            self.nodes.add(parsed_url.netloc)
        elif parsed_url.path:
            # Accepts an URL without scheme like '192.168.0.5:5000'.
            self.nodes.add(parsed_url.path)
        else:
            raise ValueError('Invalid URL')

    def create_block(self, nonce, previous_hash):
        """
        Add a block of transactions to the block chain
        """
        block = {
            'block_number': len(self.chain) + 1,
            'timestamp': time.time_ns(),
            'transactions': self.transactions,
            'nonce': nonce,
            'previous_hash': previous_hash
        }

        # Reset the current list of transactions
        self.transactions = []
        self.chain.append(block)
        return block

    def proof_of_work(self):
        """
        Proof of work algorithm
        """
        last_block = self.chain[-1]
        last_hash = get_block_hash(last_block)
        nonce = 0
        ordered_transactions = tx_list_to_ordered(self.transactions)
        while self.valid_proof(ordered_transactions, last_hash, nonce) is False:
            nonce += 1

        return nonce

    @staticmethod
    def valid_proof(transactions, last_hash, nonce, difficulty=MINING_DIFFICULTY):
        """
        Check if a hash value satisfies the mining conditions. This function is used within the proof_of_work function.
        """
        guess = (str(transactions) + str(last_hash) + str(nonce)).encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:difficulty] == '0' * difficulty

    def valid_chain(self, chain):
        """
        check if a blockchain is valid
        """
        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            # Check that the hash of the block is correct
            if block['previous_hash'] != get_block_hash(last_block):
                return False
            transactions = block['transactions']
            ordered_transactions = tx_list_to_ordered(transactions)
            if not self.valid_proof(ordered_transactions, block['previous_hash'], block['nonce'], MINING_DIFFICULTY):
                return False

            last_block = block
            current_index += 1
        return True

    def resolve_conflicts(self):
        """
        Resolve conflicts between blockchain's nodes
        by replacing our chain with the longest one in the network.
        """
        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            print('[neighbor] http://' + node + '/chain')
            try:
                response = requests.get('http://' + node + '/chain')
            except Exception:
                print('Unable to connect [neighbor] http://{}/chain. Ignored.'.format(node))
                continue

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid chain longer than ours
        if new_chain:
            self.chain = new_chain
            return True

        return False

    @staticmethod
    def hash_block(block):
        """
        Create a SHA-256 hash of a block
        """
        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()
