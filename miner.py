import json
import time
import requests
from multiprocessing import Process, Manager

from lib import lib_miner


def main():
    print("--------")
    print("Miner V1")
    print("--------")
    # menu()
    Miner().mine()

def menu():
    print("1. Mine")
    print("2. Configure")
    action = input("> ")
    if action not in ["1", "2"]:
        print("ERROR")
        print()
        menu()

    if action == "1":
        Miner().mine()


class Miner():
    def __init__(self):
        self.path_config = "config/config_miner.json"

        self.pending_transactions = None
        self.pending_transactions_hash = None
        self.data_node = None

        self.last_node_requests = 0

        self.get_config()

    def get_config(self):
        with open(self.path_config, "r") as file:
            config = json.load(file)

        self.address = config["address"]
        self.node = config["node"]

            ###
            # private_key : 8528ee7d1bb67e9195c37ffb9551fe67d29bc382acf76956a19225676d207201
            #address : 1CmUXbYYgCFJu99xXB6hVz5qyUUhm95AeS

    def get_transactions(self):
        try:
            req = requests.get(self.node+"/node")
            data_node = req.json()
            if data_node["pending_transactions_hash"] != self.pending_transactions_hash:
                req2 = requests.get(self.node+"/node/get_pending_transactions")
                pending_transactions = req2.json()

                self.pending_transactions_hash = data_node["pending_transactions_hash"]
                self.pending_transactions = pending_transactions

            return self.pending_transactions
        except Exception as e:
            print(e)
            print("ERROR, Node pending transactions unreachable")

    def get_node_infos(self):
        try:
            req = requests.get(self.node+"/node")
            data_node = req.json()
            data = {
            "coinbase":data_node["coinbase"], 
            "height":data_node["height"], 
            "last_block_hash":data_node["last_block_hash"], 
            "diff":data_node["diff"], 
            "pending_transactions_hash":data_node["pending_transactions_hash"]}
            return ["Ok",data]
        except Exception as e:
            print(e)
            print("ERROR, Node infos unreachable")
            return ["ERROR",]


    def send_block(self, hash_, block):
        try:
            data = {"hash":hash_, "block":block}
            req = requests.post(self.node+"/node/send_mined_block", data=data)
            data_return = req.json()
            return data_return
        except Exception as e:
            print(e)
            print("ERROR while sending block. Node unreachable")


    def mine(self):
        manager = Manager()
        list_pending_transactions = manager.list()
        block_found = manager.list()
        node_infos_manager = manager.dict()

        block_found.append(None)

        mining_process = Process(target=lib_miner.Miner, 
            args=(self.address, list_pending_transactions, block_found, node_infos_manager), 
            daemon=True)
        mining_process.start()

        while True:

            if int(time.time()) - self.last_node_requests < 10:
                allow_requests = False
            else:
                allow_requests = True
                self.last_node_requests = int(time.time())

            if allow_requests == True:
                node_infos = self.get_node_infos()
                if node_infos[0] == "ERROR":
                    print("Retry in 10s")
                    time.sleep(10)
                    continue

                node_infos = node_infos[1]
                
                if node_infos["pending_transactions_hash"] != self.pending_transactions_hash:
                    self.pending_transactions = self.get_transactions()
                    self.pending_transactions_hash = node_infos["pending_transactions_hash"]
                    list_pending_transactions[:] = self.pending_transactions


                del node_infos["pending_transactions_hash"]
                if node_infos != self.data_node:
                    self.data_node = node_infos
                    node_infos = self.data_node

                    # node_infos_manager.clear()
                    node_infos_manager.update(node_infos)

            if block_found[0] == None:
                continue
            else:
                data_return = self.send_block(block_found[0]["hash"], block_found[0]["block"])
                if data_return == "Ok":
                    print("Block Found, accepted")
                else:
                    print("Block Found, rejected")
                    print(data_return)
                    
                block_found[0] = None


if __name__ == '__main__':
    main()