from flask import Flask
from flask_restful import reqparse, abort, Api, Resource
from multiprocessing import Process
import time

from lib import lib_node


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


api.add_resource(Node, "/node")
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

# def recup_data_other_nodes():
#     while True:
#         node = lib_node.LibNode()
#         time.sleep(10)
#         print("avant")
#         node.add_block(str(int(node.get_node_info()["height"])+1), "hash4", "block")
#         print("apres")


if __name__ == '__main__':
    # process = Process(
    #     target=background_task,
    #     daemon=True)
    # process.start()
    
    app.run(debug=True, use_reloader=False) 

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