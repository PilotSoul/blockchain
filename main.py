from flask import Flask, jsonify, request
from uuid import uuid4
from blockchain import Blockchain
from pow import POW

app = Flask(__name__)

node_id = str(uuid4()).replace('-', '')

b_chain = Blockchain()
pw = POW()


@app.route("/mine", methods=['GET'])
def mine():
    last_block = b_chain.last_block
    last_proof = last_block['proof']
    proof = pw.proof_of_work(last_proof)

    # reward for mining
    b_chain.new_transaction(
        sender='0',
        recipient=node_id,
        amount=1
    )
    previous_hash = b_chain.hash_block(last_block)
    block = b_chain.new_block(proof, previous_hash)
    return jsonify(
        {
            'message': "New Block Forged",
            'index': block['index'],
            'transactions': block['transactions'],
            'proof': block['proof'],
            'previous_hash': block['previous_hash'],
        }
    ), 200


@app.route("/transactions/new", methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'recipient', 'amount']
    if not all(v in values for v in required):
        return 'Missing values', 400

    index = b_chain.new_transaction(values['sender'], values['recipient'], values['amount'])
    response_text = f'Transaction will be added to Block {index}'
    return jsonify(response_text), 201


@app.route("/chain", methods=['GET'])
def full_chain():
    response = {
        'chain': b_chain.chain,
        'length': len(b_chain.chain),
    }
    return jsonify(response), 200


@app.route("/nodes/register", methods=['POST'])
def register_nodes():
    """
    Register nodes
    :return:
    """
    values = request.get_json()
    nodes = values.get('nodes')

    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        b_chain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(b_chain.nodes),
    }
    return jsonify(response), 201


@app.route("/nodes/resolve", methods=['GET'])
def resolve_nodes():
    """
    Resolve conflicts in nodes
    :return:
    """
    replaced = b_chain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': b_chain.chain
        }
    else:
        response = {
            'message': 'Our chain is main',
            'chain': b_chain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5027)


