# Module 2: Creating a Cryptocurrency

# Requires Flask: pip install Flask==0.12.2
# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

########################################
# Part 1 - Building a Blockchain Class #
########################################

class Blockchain:
    
    def __init__(self):
        self.chain = []
        self.transactions = []
        self.create_block(proof = 1, prev_hash = '0')
        self.nodes = set()
    
    def create_block(self, proof, prev_hash):
        block = {'index': len(self.chain) + 1, 
                 'timestamp': str(datetime.datetime.now()),
                 'transactions': self.transactions,
                 'proof': proof,
                 'prev_hash': prev_hash}
        self.transactions = []
        self.chain.append(block)
        return block
    
    def get_prev_block(self):
        return self.chain[-1]
    
    def proof_of_work(self, prev_proof):
        new_proof = 1
        check_proof = False
        while check_proof is False:
            # arguments goes in sha256() should be an asymmetrical expression
            hash_operation = hashlib.sha256(str(new_proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
        return new_proof
    
    def hash(self, block):
        # make block into a string in json format
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    def is_chain_valid(self, chain):
        prev_block = chain[0]
        block_index = 1
        while block_index < len(chain):
            block = chain[block_index]
            if block['prev_hash'] != self.hash(prev_block):
                return False
            prev_proof = prev_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - prev_proof**2).encode()).hexdigest()
            if hash_operation[:4] != '0000':
                return False
            prev_block = block
            block_index += 1
        return True
    
    # pillar 1: being able to add transactions
    def add_transaction(self, sender, receiver, amount):
        self.transactions.append({'sender': sender,
                                 'receiver': receiver,
                                 'amount': amount})
        prev_block = self.get_prev_block()
        return prev_block['index'] + 1
        
    # pillar 2: creating a consensus
    def add_node(self, address):
        parsed_url = urlparse(address)
        # netloc: exactly the url without http://: IP + Port
        self.nodes.add(parsed_url.netloc)
    
    # this is the function to decide which chain do we choose: the longest chain
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        for node in network:
            # again, every node is the IP + Port, so we are checking through all ports
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
        if longest_chain: # if the longest chain is not None anymore
            self.chain = longest_chain
            return True
        return False
        
##################################
# Part 2 - Mining our Blockchain #
##################################

# Creating a Web App
# Using Flask: see the documentation on flask.pocoo.org
app = Flask(__name__)

# Creating an address for node on Port 5000
node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()

# use 'GET' method to read, use 'POST' to write
@app.route('/mine_block', methods = ['GET']) 
def mine_block():
    prev_block = blockchain.get_prev_block()
    prev_proof = prev_block['proof']
    proof = blockchain.proof_of_work(prev_proof)
    prev_hash = blockchain.hash(prev_block)
    blockchain.add_transaction(sender = node_address, receiver = 'Kelly', amount = 1) # reward
    block = blockchain.create_block(proof, prev_hash)
    
    response = {'message': 'Congrats! You just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'prev_hash': block['prev_hash'],
                'transactions': block['transactions']}
    
    # in 'GET' method, 200 is the http status code for "OK"
    return jsonify(response), 200 
    
# Getting the full Blockchain
@app.route('/get_chain', methods = ['GET'])
def get_chain():
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    return jsonify(response), 200

# Checking if a chain is valid
@app.route('/is_valid', methods = ['GET'])
def is_valid():
    validity = blockchain.is_chain_valid(blockchain.chain)
    if validity:
        message = 'Yep, the blockchain is valid.'
    else:
        message = 'Oh no! The blockchain is invalid!'
    response = {'message': message}
    return jsonify(response), 200

# Adding a new transaction to the blockchain
@app.route('/add_transaction', methods = ['POST'])
def add_transaction():
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount'] # to make sure that the input is valid
    if not all (key in json for key in transaction_keys):
        return 'Some fields are missing.', 400 # bad request
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {'message': f'This transaction will be added to Block {index}.'}
    return jsonify(response), 201 # 'OK' for POST method


##########################################
# Part 3 - Decentralizing our Blockchain #
##########################################
    
# Connecting new nodes
@app.route('/connect_nodes', methods = ['POST'])
def connect_nodes():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No nodes found.', 400
    for node in nodes:
        blockchain.add_node(node)
    response = {'message': 'All nodes are connected. The Lucoin Blockchain now contains:',
                'total_nodes': list(blockchain.nodes)}
    return jsonify(response), 201

# Replacing the chain by the longest one (if needed)
@app.route('/replace_chain', methods = ['GET'])
def replace_chain():
    replaced = blockchain.replace_chain()
    if replaced:
        response = {'message': 'The chain has been replaced with the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'The chain is already the longest one.',
                    'actual_chain': blockchain.chain}
    return jsonify(response), 200


# Running the app
app.run(host = '0.0.0.0', port = '5002')
