import hashlib
import json
from urllib.parse import urlparse
from time import time

import requests

from pow import POW


class Blockchain:
    """
    Class is responsible for managing the chain
    """

    def __init__(self):
        self.chain = []
        self.current_transactions = []
        self.new_block(previous_hash=1, proof=100)
        self.nodes = set()

    def new_block(self, proof: int, previous_hash: int | str = None) -> dict:
        """
        Creates a new block and adds it to the chain
        :param proof: the proof given by the Proof of Work algorithm
        :param previous_hash: hash of previous block
        :return: new block
        """
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash_block(self.chain[-1])
        }
        # reset list of current transactions
        self.current_transactions = []
        self.chain.append(block)

        return block

    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        """
        Adds a new transaction to the list of transactions
        :param sender: address of the sender
        :param recipient: address of the recipient
        :param amount: amount
        :return: index of the block that will hold this transaction
        """
        self.current_transactions.append(
            {
                'sender': sender,
                'recipient': recipient,
                'amount': amount
            }
        )
        return self.last_block['index'] + 1

    @staticmethod
    def hash_block(block: dict) -> str:
        """
        Hashes a block
        :return: hash string
        """
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @property
    def last_block(self) -> dict:
        """
        Returns the last block in the chain
        :return:
        """
        return self.chain[-1]

    def validate_chain(self, chain: list) -> bool:
        """
        Determine if a given blockchain is valid
        :param chain: a blockchain
        :return: <bool> True if valid, False if not
        """
        last_block = chain[0]
        current_index = 1
        while current_index < len(chain):
            block = chain[current_index]
            print(f'{last_block}')
            print(f'{block}')
            print(f"\n{"_"*10}\n")
            # Checking that the hash of the block is correct
            if block['previous_hash'] != self.hash_block(last_block):
                return False

            # Checking that the Proof of Work is correct
            if not POW.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_index += 1
        return True

    def register_node(self, address: str):
        """
        Add a new node to the list of nodes
        :param address: <str> Address of node. E.g. 'http://localhost:5000'
        """
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def resolve_conflicts(self) -> bool:
        """
        Consensus algorithm
        It resolves conflicts by replacing our chain
        with the longest one in the network
        :return <bool>: True if replaces else False
        """
        neighbours = self.nodes
        new_chain = None

        max_length = len(self.chain)
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > max_length and self.validate_chain(chain):
                    max_length = length
                    new_chain = chain

        if new_chain:
            self.chain = new_chain
            return True

        return False

