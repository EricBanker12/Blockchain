import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_transaction(self, sender, recipient, amount):
        """
        :param sender: <str> Address of the sender
        :param recipient: <str> Address of the Recipient
        :param amount: <int> Amount
        :return: <int> The index of the `block` that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
            'index': len(self.chain) + 1,
        })
    
    def new_block(self, proof, previous_hash=None):
        """
        Create a new Block in the Blockchain

        A block should have:
        * Index
        * Timestamp
        * List of current transactions
        * The proof used to mine this block
        * The hash of the previous block

        :param proof: <int> The proof given by the Proof of Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous Block
        :return: <dict> New Block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'currentTransactions': self.current_transactions,
            'proof': proof,
            'previousHash': previous_hash or self.hash(self.last_block)
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block

    def hash(self, block):
        """
        Creates a SHA-256 hash of a Block

        :param block": <dict> Block
        "return": <str>
        """

        # Use json.dumps to convert json into a string
        # We must make sure that the Dictionary is Ordered,
        # or we'll have inconsistent hashes
        # Use hashlib.sha256 to create a hash
        # It requires a `bytes-like` object, which is what
        # .encode() does.
        # It converts the Python string into a byte string.

        # Create the block_string
        block_string = json.dumps(block, sort_keys=True)

        # Hash this string using sha256
        block_hash = hashlib.sha256(block_string.encode())

        # By itself, the sha256 function returns the hash in a raw string
        # that will likely include escaped characters.
        # This can be hard to read, but .hexdigest() converts the
        # hash to a string of hexadecimal characters, which is
        # easier to work with and understand

        # Return the hashed block string in hexadecimal format
        return block_hash.hexdigest()

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3
        leading zeroes?  Return true if the proof is valid
        :param block_string: <string> The stringified block to use to
        check in combination with `proof`
        :param proof: <int?> The value that when combined with the
        stringified previous block results in a hash that has the
        correct number of leading zeroes.
        :return: True if the resulting hash is a valid proof, False otherwise
        """
        block_string = json.dumps(block, sort_keys=True)
        guess = f'{block_string}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()

        return guess_hash[:6] == "000000"


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    data = request.get_json()

    if not 'proof' in data or not 'id' in data:
        return jsonify({'message': 'Missing "proof" or "id"'}), 400

    # Forge the new Block by adding it to the chain with the proof
    if blockchain.valid_proof(blockchain.last_block, data['proof']):
        blockchain.new_transaction('0', data['id'], 1)
        new_block = blockchain.new_block(data['proof'])

        response = {
            # Send a JSON response with the new block
            'message': 'New Block Forged',
            'newBlock': new_block,
        }
    else:
        response = {
            'message': 'Proof Not Valid.'
        }

    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # Return the chain and its current length
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/last_block', methods=['GET'])
def last_block():
    response = {
        'lastBlock': blockchain.last_block
    }
    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    data = request.get_json()

    if not 'sender' in data or not 'recipient' in data or not 'amount' in data:
        return jsonify({'message': 'Missing "sender", "recipient" or "amount"'}), 400
    
    blockchain.new_transaction(data['sender'], data['recipient'], data['amount'])

    response = {
        'message': f'Transaction added to next block at index {len(blockchain.chain)+1}'
    }
    
    return jsonify(response), 200

# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
