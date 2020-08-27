from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from multiprocessing import Process
import time
import requests
import sys
import json

from lib import lib_node
from lib import lib_verify


app = Flask(__name__)
api = Api(app)

node = lib_node.LibNode()


class Node(Resource):
    def get(self):
        data = node.get_node_info()
        return data, 200


class NodeGetBlocks(Resource):
    def post(self): # If number == -1 : ça veut dire qu'on veut tt à partir de X
        parser = reqparse.RequestParser()
        parser.add_argument("height")
        parser.add_argument("number")
        args = parser.parse_args()
        data, code = node.get_blocks(args["height"], args["number"])
        return data, code


class NodeGetAllBlocks(Resource):
    def get(self):
        data, code = node.get_all_blocks()
        return data, code


class NodeGetPendingTransactions(Resource):
    def get(self):
        data, code = node.get_pending_transactions()
        return data, code


class MinerGetMinedBlock(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("hash")
        parser.add_argument("block")
        args = parser.parse_args()
        data, code = node.mined_block(args["hash"], args["block"])
        return data, code


class WalletSendTransaction(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("transaction")
        args = parser.parse_args()
        data, code = node.add_transaction_from_node(args["transaction"])
        return data, code

class WalletGetTransactions(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument("address")
        args = parser.parse_args()
        data, code = node.get_transactions_with_addr_from_node(args["address"])
        return data, code


api.add_resource(Node, "/node", "/")
api.add_resource(NodeGetBlocks, "/node/get_blocks")
api.add_resource(NodeGetAllBlocks, "/node/get_all_blocks")
api.add_resource(NodeGetPendingTransactions, "/node/get_pending_transactions")

api.add_resource(MinerGetMinedBlock, "/node/send_mined_block")

api.add_resource(WalletSendTransaction, "/node/send_transaction")
api.add_resource(WalletGetTransactions, "/node/get_transactions")
# api.add_resource(WalletGet)


# https://flask-restful.readthedocs.io/en/latest/quickstart.html
# https://fr.wikipedia.org/wiki/Liste_des_codes_HTTP
# https://github.com/satwikkansal/python_blockchain_app/blob/13ea6ee3859afc68305d86efa3977aabb4eb2e6b/node_server.py#L193
# https://en.bitcoin.it/wiki/Network

def background_task():
    session = requests.Session()
    while True:
        node = lib_node.LibNode()
        time.sleep(10)
        for node_remote in node.list_nodes:
            height_local_node = node.get_node_info()["height"]
            # print(node_remote)
            try:
                req = session.get(f"http://{node_remote}/node")
                data_req = req.json()
                height_remote_node = data_req["height"]
                if int(height_remote_node) > int(height_local_node):
                    print("Différence :",height_local_node, height_remote_node, node_remote)
                    # We ask for the last bloc we possibly share 
                    # On demande le dernier bloc en commun
                    # Si différent de notre dernier bloc : 
                    #     on demande celui d'avant
                    #     si différent : ....

                    temp_height = height_local_node
                    temp_list_new_blocks = []
                    while True:
                        if temp_height == 1:
                            print(f"CANNOT SYNC WITH {height_node}. The blockchain is entirely different.")
                            print("Please remove it from the list of nodes.")
                        # print(temp_height)

                        data = {"height":temp_height, "number":"1"}
                        req = requests.post(f"http://{node_remote}/node/get_blocks", data=data)
                        block = req.json()[0]
                        temp_list_new_blocks.append(block)

                        # print("block: ",block)
                        # print("node.get_blocks(temp_height, 1)",node.get_blocks(temp_height, 1))
                        
                        if block["hash"] == node.get_blocks(temp_height, 1)[0][0]["hash"]:
                            # print("Meme",temp_height)
                            break
                        else:
                            temp_height -= 1

                    # On recup la liste des blocs > height_local_node
                    data = {"height":height_local_node, "number":"-1"}
                    req = requests.post(f"http://{node_remote}/node/get_blocks", data=data)
                    blocks = req.json()
                    del blocks[0]
                    temp_list_new_blocks.extend(blocks)

                    # print("temp_list_new_blocks",temp_list_new_blocks)

                    # Verification + ajout à la blockchain
                    list_blocks = temp_list_new_blocks[1:]
                    first_block_height = list_blocks[0]["height"]
                    previous_block_hash = temp_list_new_blocks[0]["hash"]
                    # print("list_blocks",list_blocks)
                    # print(first_block_height, previous_block_hash)
                    verification = node.verify_add_to_blockchain(list_blocks, first_block_height, previous_block_hash)
                    if verification != "Ok":
                        print(verification)


                # We get pending transactions
                req = session.get(f"http://{node_remote}/node")
                data_req = req.json()
                pending_transactions_hash_remote = data_req["pending_transactions_hash"]
                if pending_transactions_hash_remote == "4f53cda18c2baa0c0354bb5f9a3ecbe5ed12ab4d8e11ba873c2f11161202b945":
                    continue

                pending_transactions_hash_local = node.get_node_info()["pending_transactions_hash"]
                pending_transactions_local = node.get_pending_transactions()[0]

                if pending_transactions_hash_local != pending_transactions_hash_remote:
                    # print("OUI !!!")
                    req = session.get(f"http://{node_remote}/node/get_pending_transactions")
                    pending_transactions_remote = req.json()

                    # print(pending_transactions_remote)

                    # On supprime les transactions qui sont déjà dans notre liste
                    # print("----")
                    print(pending_transactions_remote)
                    print("\n\n")
                    for remote_transaction in pending_transactions_remote:
                        # print(transaction)
                        for local_transaction in pending_transactions_local:
                            print(local_transaction["hash"], remote_transaction["hash"])
                            if local_transaction["hash"] == remote_transaction["hash"]:
                                pending_transactions_remote.remove(remote_transaction)
                    print("\n\n")
                    print(pending_transactions_remote)

                    if len(pending_transactions_remote) == 0:
                        continue

                    # # Delete all the transactions from the mined block that are in pending transactions
                    # pending_transactions = pending_transactions_remote
                    # if len(pending_transactions) > 0:
                    #     new_pending_transactions = pending_transactions[:]
                    #     list_transactions_hash = lib_verify.get_transactions_hash_in_block(block)
                    #     for hash_ in list_transactions_hash:
                    #         for pending_transaction in pending_transactions:
                    #             if hash_ == pending_transaction["hash"]:
                    #                 new_pending_transactions.remove(pending_transaction)


                    # On vérifie les transactions et on les ajoutes
                    # print("coucou")
                    # print(pending_transactions_remote)
                    node.add_transactions_from_node(pending_transactions_remote)
                    # print(node.get_node_info())

            except Exception as e:
                raise e
                print(e)
                # Amélioration possible : si trop d'erreur avec un node,
                # on peut le supprimer de la liste ou le mettre sur une liste 
                # des nodes offline

def sync(url_node):
    try:
        session = requests.Session()
        req = session.get(f"http://{url_node}/node/get_all_blocks")
        blocks = req.json()
        node.add_blocks(blocks)
    except Exception as e:
        print(e)
        print("SYNC FAILED !!!!")
        sys.exit(0)


if __name__ == '__main__':
    allow_sync = True   # You can choose to sync or not. 
                        # It must be False if you start a new blockchain

    # Check if node needs to be sync :
    if node.get_node_info()["height"] == 0:
        sync(node.list_nodes[0])


    process = Process(
        target=background_task,
        daemon=True)
    process.start()
    
    with open("config/config_node.json", "r") as fichier:
        data = json.load(fichier)

    port = data["port"]    

    app.run(debug=True, use_reloader=False, port=port) 

    # If we set use_realoader = True, it will launch 2 deamon process
    # http://blog.davidvassallo.me/2013/10/23/nugget-post-python-flask-framework-and-multiprocessing/

    # database = lib_node.Database()
    # blocks = [{"height": "990", "hash": "hash", "block": "block"}, {"height": "990", "hash": "hash", "block": "block"}]
    # print(database.get_list_nodes())
    # print(database.get_pending_transactions())
    # database.add_pending_transaction("TEST hash", "transac")
    # database.add_blocks(blocks)
    # print(database.get_blocks(1,1))
    # database.del_blocks(1)