import codecs
import ecdsa
import sys
import logging
import json

from lib import lib_cryptography
from lib import lib_transactions
from lib import search_in_blocks
from lib import lib_verify


def main():
    # logging.basicConfig(level=logging.INFO,\
    #   format='%(asctime)s :: %(levelname)s :: %(message)s')

    # Examples Lib_transaction
    # This is just an example. It is not a real transaction
    # Example_lib_transaction().ex_create_normal_transaction()
    Example_lib_transaction().ex_create_coinbase_transaction()

    # Examples Lib_cryptography
    # Example_lib_cryptography().ex_keys()
    # Example_lib_cryptography().hash_sha256()

    #Examples search_in_blocks
    # Example_search_in_blocks().get_transactions_in_all_blockchain()
    # Example_search_in_blocks().get_transactions_with_addr()

    pass




class Example_lib_cryptography:
    def ex_keys(self):
        # Generate private key + address
        private_key = lib_cryptography.Keys.generate_private_key()
        address = lib_cryptography.Keys.generate_address(private_key)
        print("private_key :",private_key)
        print("address :",address)

        # Get signing and verifing keys from private key (signing key = public key)
        private_key_bytes = codecs.decode(private_key, 'hex')
        signing_key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        verifying_key = signing_key.verifying_key

        # Sign message
        message = b"message"
        signature = signing_key.sign(message)

        # Verify message
        print("Signature vérifiée : ",verifying_key.verify(signature, message))

    def hash_sha256(self):
        hash_ = lib_cryptography.hash("GENESIS BLOCK")
        print(hash_)


class Example_lib_transaction:
    def __init__(self):
        pass

    def ex_create_normal_transaction(self):

        private_key = lib_cryptography.Keys.generate_private_key()
        address = lib_cryptography.Keys.generate_address(private_key)

        private_key2 = lib_cryptography.Keys.generate_private_key()
        address2 = lib_cryptography.Keys.generate_address(private_key2)

        input_tx = [{
            "amount":300,
            "from_addr":address,
            "private_key":private_key,
            "previous_tx":"None"
        },{
            "amount":100,
            "from_addr":address,
            "private_key":private_key,
            "previous_tx":"None"
        }]
        output_txs = [{
            "amount":200,
            "to_addr":address
        },{
            "amount":200,
            "to_addr":address2
        }
        ]
        transaction = lib_transactions.Transaction().create_transaction(input_tx, output_txs)
        
        print(transaction)

        # return transaction
        # hash_ = lib_verify.get_tx_hash_from_tx(transaction)
        # print(hash_)

    def ex_create_coinbase_transaction(self):
        private_key = lib_cryptography.Keys.generate_private_key()
        address = lib_cryptography.Keys.generate_address(private_key)
        print(private_key)
        print(address)
        block_num = 3
        transaction = lib_transactions.Transaction().create_coinbase(100,address, block_num)
        print(transaction)

class Example_search_in_blocks:
    def get_transactions_in_all_blockchain(self):
        with open("data/blockchain.json") as file:
            data = json.load(file)

        blocks = []
        for i in data:
            blocks.append(i["block"])

        transactions = search_in_blocks.GetTransactions(blocks).get()
        print(transactions)


    def get_transactions_with_addr(self):
        with open("data/blockchain.json") as file:
            blocks = json.load(file)

        # Optionnal
        # blocks = []
        # for i in data:
        #     blocks.append(i["block"])

        address = "1CmUXbYYgCFJu99xXB6hVz5qyUUhm95AeS"
        transactions = search_in_blocks.get_transactions_for_addr(blocks, address)
        print(transactions)


if __name__ == "__main__":
    main()