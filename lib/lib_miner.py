import logging
import random
import time
# from multiprocessing import Process, Array

try:
    import lib_cryptography
    import lib_transactions
except :
    from lib import lib_cryptography
    from lib import lib_transactions


# Récup les transactions du node + la diff + le reward
# Ajoute la coinbase
# Hash les transactions + le nonce (= bloc)
# Vérifie que ça corresponde à la diff
# Renvoie le bloc + hash au node


class Miner:
    def __init__(self, address, list_pending_transactions, block_found, node_infos):
        self.list_pending_transactions = list_pending_transactions 
        self.block_found = block_found
        self.node_infos = node_infos
        self.address = address

        # Creation of variables
        self.transactions = None
        self.transactions_without_coinbase = None
        self.transactions_str = None
        self.diff = None
        self.coinbase = None
        self.last_block_hash = None
        self.last_block_num = None

        self.mine()


    # This is the header of the block
    def get_data_before_nonce(self):
        block_num = int(self.last_block_num) + 1

        data =  f"Block {block_num}\n" \
                f"Previous Block Hash : {self.last_block_hash}\n"

        return data


    # Add coinbase in the first position in the list of transactions
    def add_coinbase(self, transactions, address, amount, block_num=""): 
        if block_num == "":
            block_num = self.last_block_num + 1
        coinbase = lib_transactions.Transaction().create_coinbase(amount,address,block_num)
        # print("----")
        # print(transactions)
        transactions.insert(0, coinbase)

        logging.debug(coinbase.replace("\n","---"))
        return transactions

    # Transform the list of transactions to a string (which will be added to the block)
    def list_transactions_to_str(self):
        data_transactions = ""
        for i in range(len(self.transactions)):
            if isinstance(self.transactions[i], dict) == True:
                tx = self.transactions[i]["transaction"]
            else:
                tx = self.transactions[i]

            data_transactions += f"Transaction {i}:\n" + tx + "\n"
        
        # Delete empty lines at the end
        data_transactions = data_transactions[:-2]

        return data_transactions
        
        

    def mine(self):
        # a = 0
        while dict(self.node_infos) == {}:
            time.sleep(1)

        print("Mining...")

        while True:
            # a += 1
            # print(a)

            data = self.node_infos

            
            if data["diff"] != self.diff:
                self.diff = data["diff"]

            if data["coinbase"] != self.coinbase:
                self.coinbase = data["coinbase"]

            # Last bloc hash and last block num should be modified at the same time.
            if data["last_block_hash"] != self.last_block_hash or data["height"] != self.last_block_num:
                self.last_block_hash = data["last_block_hash"]
                self.last_block_num = data["height"]
                self.data_before_nonce = self.get_data_before_nonce()


            if list(self.list_pending_transactions) != self.transactions_without_coinbase:
                self.transactions_without_coinbase = list(self.list_pending_transactions)
                self.transactions = self.add_coinbase(self.transactions_without_coinbase, self.address, self.coinbase, int(self.last_block_num)+1)
                self.transactions_str = self.list_transactions_to_str()


            nonce = random.randint(1,100000000)
            block = self.data_before_nonce + f"Nonce : {nonce}\n\n" + self.transactions_str
            hash_ = lib_cryptography.hash(block)


            if hash_[:len(self.diff)] == self.diff and self.block_found[0] == None:
                logging.info("Bloc found")
                self.block_found[0] = {"hash":hash_, "block":block}
                
                

if __name__ == '__main__':
    print("Do not launch this file. Use mine.py")
    # private_key = lib_cryptography.Keys.generate_private_key()
    # address = lib_cryptography.Keys.generate_address(private_key)

    # miner = Miner(address)
    # miner.mine()
    # miner.add_coinbase(transactions, address, 100)