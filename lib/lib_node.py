import json
import re

try:
    import lib_cryptography
    import lib_verify
    import search_in_blocks
except :
    from lib import lib_cryptography
    from lib import lib_verify
    from lib import search_in_blocks


class Database:
    def __init__(self):
        self.path_data_node = "config/config_node.json"
        self.path_pending_transactions = "data/transactions.json"
        self.path_blockchain = "data/blockchain.json"
        # self.path_pending_transactions = "../data/transactions.json"
        # self.path_blockchain = "../data/blockchain.json"

        self.blockchain_hash = self.get_blockchain_hash()
        self.pending_transactions_hash = self.get_pending_transactions_hash()

        self.coinbase = "100"
        self.diff = "0000"

        self.list_nodes = self.get_list_nodes()

        self.initialize_last_hash_height()

    def detect_changes(self):
        new_blockchain_hash = self.get_blockchain_hash()
        if new_blockchain_hash != self.blockchain_hash:
            self.blockchain_hash = self.get_blockchain_hash()
            self.initialize_last_hash_height()
        self.pending_transactions_hash = self.get_pending_transactions_hash()


    def initialize_last_hash_height(self):
        with open(self.path_blockchain, "r") as file:
            data = json.load(file)

        self.last_block_hash = data[-1]["hash"]
        self.last_block_height = int(data[-1]["height"])


    def get_blockchain_hash(self):
        with open(self.path_blockchain, "r") as file:
            data = file.read()
        hash_ = lib_cryptography.hash(data)
        return hash_


    def get_pending_transactions_hash(self):
        with open(self.path_pending_transactions, "r") as file:
            data = file.read()
        hash_ = lib_cryptography.hash(data)
        return hash_


    def get_list_nodes(self):
        with open(self.path_data_node, "r") as file:
            data = json.load(file)
        list_nodes = data["list_nodes"]
        return list_nodes


    def get_pending_transactions(self):
        with open(self.path_pending_transactions, "r") as file:
            data = json.load(file)
        return data


    def get_blocks(self, height, number):
        with open(self.path_blockchain, "r") as file:
            data = json.load(file)

        blocks = []

        for i in range(height, height+number+1):
            blocks.append(data[i])

        return blocks


    def get_all_blocks(self):
        with open(self.path_blockchain, "r") as file:
            data = json.load(file)

        return data


    def add_pending_transaction(self, hash_, transaction):
        with open(self.path_pending_transactions, "r") as file:
            data = json.load(file)

        data.append({"hash":hash_, "transaction":transaction})

        with open(self.path_pending_transactions, "w") as file:
            json.dump(data, file, indent=4)


    def add_block(self, height, hash_, block):
        with open(self.path_blockchain, "r") as file:
            data = json.load(file)

        data.append({"height":height, "hash":hash_, "block":block})

        self.last_block_height = int(height)
        self.last_block_hash = hash_
        self.blockchain_hash = self.get_blockchain_hash()

        with open(self.path_blockchain, "w") as file:
            data = json.dump(data, file, indent=4)


    def add_blocks(self, blocks):
        with open(self.path_blockchain, "r") as file:
            data = json.load(file)

        data.extend(blocks)

        with open(self.path_blockchain, "w") as file:
            data = json.dump(data, file, indent=4)

    

    def del_blocks(self, height):
        with open(self.path_blockchain, "r") as file:
            data = json.load(file)

        data = data[:height]

        with open(self.path_blockchain, "w") as file:
            data = json.dump(data, file, indent=4)


    def set_pending_transactions(self, new_pending_transactions):
        with open(self.path_pending_transactions, "w") as file:
            json.dump(new_pending_transactions, file, indent=4)


class LibNode:
    def __init__(self):
        try:
            self.database = Database()
        except Exception as e:
            print("ERROR init database")
            print(e)
        self.list_nodes = self.database.list_nodes

    #########
    # Interract to Database
    #########

    def detect_changes(self):
        self.database.detect_changes()

    def get_node_info(self):
        try:
            self.detect_changes()
            data = {
            "height":str(self.database.last_block_height),
            "last_block_hash":str(self.database.last_block_hash),
            "blockchain_hash":str(self.database.blockchain_hash),
            "pending_transactions_hash":str(self.database.pending_transactions_hash),
            "diff":self.database.diff,
            "coinbase":self.database.coinbase
            }
            return data
        except Exception as e:
            return "ERROR", 500


    def get_blocks(self, height, number):
        try:
            self.detect_changes()
            try:
                height = int(height)
                number = int(number)
            except Exception as e:
                return "ERROR", 400

            if not(0 <= height <= self.database.last_block_height):
                return "ERROR", 400

            if number == -1:
                number = self.database.last_block_height - height

            if  number < 0:
                return "ERROR", 400

            if height + number > self.database.last_block_height:
                number = self.database.last_block_height - height

            blocks = self.database.get_blocks(height, number)
            return blocks, 200

        except Exception as e:
            print(e)
            return f"ERROR : {e}", 500
        

    def get_all_blocks(self):
        try:
            self.detect_changes()
            return self.database.get_all_blocks(), 200
        except Exception as e:
            return f"ERROR : {e}", 500


    def get_pending_transactions(self):
        try:
            self.detect_changes()
            return self.database.get_pending_transactions(), 200
        except Exception as e:
            return f"ERROR : {e}", 500


    def add_block(self, height, hash_, block):
        self.detect_changes()
        self.database.add_block(height, hash_, block)


    def add_blocks(self, list_blocks):
        self.detect_changes()
        self.database.add_blocks(list_blocks)


    def add_pending_transaction(self, hash_, transaction):
        self.detect_changes()
        self.database.add_pending_transaction(hash_, transaction)
        

    def del_blocks(self, height):
        self.detect_changes()
        self.database.del_blocks(height)


    ####
    # Verify blocks and pending transactions
    ####

    def verify_one_block(self, block, hash_, previous_block_hash, block_height, coinbase=None):
        if coinbase == None:
            coinbase = int(self.database.coinbase)
        # list_transactions_pending = self.database.get_pending_transactions()
        verify = lib_verify.VerifyBlock(block, hash_, previous_block_hash, block_height, coinbase)
        
        verif_hash = verify.check_hash()
        if verif_hash[0] != "Ok":
            return verif_hash

        verif_block = verify.verify_block()
        if verif_block[0] != "Ok":
            return verif_block

        return ["Ok"]


    def add_transaction_from_node(self, transaction):
        verify = lib_verify.VerifyTransaction(transaction).verify_transaction()
        if verify != "Ok":
            return verify, 400

        tx_hash, tx_input_ouput = transaction.split("\n",maxsplit=1)

        # Transaction Hash
        tx_hash = re.findall(r"Tx Hash : ([A-z0-9]+)", tx_hash)
        tx_hash = tx_hash[0]
        
        # We add this transaction to the list of pending tx
        try:
            self.add_pending_transaction(tx_hash, transaction)
            return "Ok", 200
        except Exception as e:
            raise e
            return "ERROR", 500


    def get_transactions_with_addr_from_node(self, address):
        try:
            blocks = self.get_all_blocks()[0]
            transactions = search_in_blocks.get_transactions_for_addr(blocks, address)
            return transactions, 200
        except Exception as e:
            return f"ERROR {e}", 500




    # Verification of a new block, received from a miner
    def mined_block(self, hash_, block):
        try:
            self.detect_changes()
            previous_block_hash = self.database.last_block_hash
            block_height = self.get_node_info()["height"]
            verify = self.verify_one_block(block, hash_, previous_block_hash, int(block_height)+1)
            if verify[0] == "ERROR":
                return verify, 400

            self.add_block(int(block_height)+1, hash_, block)

            # Delete all the transactions from the mined block that are in pending transactions
            pending_transactions = self.get_pending_transactions()[0]
            if len(pending_transactions) > 0:
                new_pending_transactions = pending_transactions[:]
                list_transactions_hash = lib_verify.get_transactions_hash_in_block(block)
                for hash_ in list_transactions_hash:
                    for pending_transaction in pending_transactions:
                        if hash_ == pending_transaction["hash"]:
                            new_pending_transactions.remove(pending_transaction)
                self.database.set_pending_transactions(new_pending_transactions)


            return "Ok", 200
        except Exception as e:
            raise e
            return f"ERROR : {e}", 500


    #################
    # Data recieved fom other node
    #################

    def verify_blocks(self, list_blocks, previous_block_hash, block_height):
        if len(list_blocks) == 1:
            block = list_blocks[0]["block"]
            hash_ = list_blocks[0]["hash"]
            verify_block = self.verify_one_block(block, hash_, previous_block_hash, block_height)
            if verify_block[0] != "Ok":
                # Here we can make a system of reputation for nodes. Too many bad blocks lead to a blacklist
                return verify_block
            else:
                return ["Ok"]
                try:
                    self.add_block(block_height, hash_, block)
                    return ["Ok"]
                except Exception as e:
                    return ["ERROR", e]

        else:
            for i in range(len(list_blocks)):
                # print("----",i)
                # print("block_height",block_height)
                block_height = list_blocks[i]["height"]
                # print("block_height",block_height)
                verify_block = self.verify_one_block(list_blocks[i]["block"], list_blocks[i]["hash"], previous_block_hash, block_height)
                if verify_block[0] != "Ok":
                    return verify_block
                previous_block_hash = list_blocks[i]["hash"]
                
            try:
                self.add_blocks(list_blocks)
                return ["Ok"]
            except Exception as e:
                return ["ERROR", e]

        return ["Ok"]


    def verify_add_to_blockchain(self, list_blocks, first_block_height, previous_block_hash):
        verification = self.verify_blocks(list_blocks, previous_block_hash, first_block_height)
        if verification[0] != "Ok":
            return verification
        
        actual_height = self.get_node_info()["height"]
        if int(first_block_height) <= int(actual_height):
            self.del_blocks(first_block_height)

        self.add_blocks(list_blocks)

        return "Ok"







if __name__ == "__main__":
    print("Do not launch this file manually")

    # with open("test.txt" , "r") as fichier:
    #     data = fichier.read().split("\n--\n")
    # list_blocks = [{
    #     "hash":data[0], "block":data[1], "height":2
    # }]
    # lib_no = LibNode()
    # a = lib_no.verify_blocks_from_node(list_blocks)
    # print(a)

    # with open("test2.txt", "r") as fichier:
    #     transaction = fichier.read()
    # print(LibNode().verify_transactions_from_node(transaction))