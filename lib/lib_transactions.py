import codecs
import ecdsa
import sys
import logging

try:
    import lib_cryptography
except :
    from lib import lib_cryptography




class Transaction:
    def __init__(self):
        pass

    def create_input_transaction(self, amount, from_addr, private_key, previous_tx, id_of_input_tx, str_output_tx):
        logging.debug("create_input_transaction(self, amount, from_addr, private_key, previous_tx, id_of_input_tx)")
        logging.debug(f"create_input_transaction(self,{amount},{from_addr},{private_key},{previous_tx},{id_of_input_tx})")

        # Get verifying, signing and public keys
        private_key_bytes = codecs.decode(private_key, 'hex')
        signing_key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1)
        verifying_key = signing_key.verifying_key
        public_key_bytes = verifying_key.to_string()
        public_key_str = codecs.encode(public_key_bytes, 'hex').decode()


        data =  f"{id_of_input_tx}\n" \
                f"Previous tx : {previous_tx}\n" \
                f"From : {from_addr}\n" \
                f"Amount : {amount}\n" \
                f"Public Key : {public_key_str}\n"

        # Signature
        msg_to_sign = f"Public Key : {public_key_str}\n{str_output_tx}".encode()
        signature = signing_key.sign(msg_to_sign)
        signature_hex = codecs.encode(signature, 'hex')
        data += f"Signature : {signature_hex.decode()}"

        logging.debug("data : "+data.replace("\n"," -- "))


        ## Verify signature

        # Get public then verify key
        public_key_str = data.split("\n")[4].split(" : ")[1]
        public_key_hex = codecs.decode(public_key_str.encode(), 'hex')
        verify_key = ecdsa.VerifyingKey.from_string(public_key_hex, curve=ecdsa.SECP256k1)

        # Get message to sign and signature
        msg_to_sign = data.split("\n")[4] + "\n" + str_output_tx
        signature = data.split("\n")[5].split(" : ")[1]
        signature_hex = codecs.decode(signature.encode(), 'hex')
        try:
            verify_key.verify(signature_hex, msg_to_sign.encode())
        except ecdsa.keys.BadSignatureError as e:
            print("ERROR in lib_wallet.py, Transaction(), create_input_transaction()")
            print("ERROR BAD SIGNATURE !!!")
            sys.exit(0)

        # return input transaction
        return data


    def create_output_transaction(self, amount, to_addr, id_of_output_tx):
        logging.debug("create_output_transaction(self, amount, to_addr, id_of_output_tx)")
        logging.debug(f"create_input_transaction(self,{amount},{to_addr},{id_of_output_tx}")

        data =  f"{id_of_output_tx}\n" \
                f"To : {to_addr}\n" \
                f"Amount : {amount}"

        logging.debug("Data : "+data)
        return data


    def create_transaction(self, input_txs, output_txs):
        logging.debug("create_transaction(self, input_txs, output_txs)")
        logging.debug(f"create_transaction(self,{input_txs},{output_txs}")

        # Generate output part of transaction
        str_output_tx = "Output :"
        id_of_output_tx = 0
        for output_tx in output_txs:
            amount = output_tx["amount"]
            to_addr = output_tx["to_addr"]

            data = self.create_output_transaction(amount, to_addr, id_of_output_tx)
            str_output_tx = str_output_tx + "\n"+ data
            id_of_output_tx += 1

        # Generate input part of transaction
        # We need output part in input part because the sender needs to sign the output
        str_input_tx = "Input :"
        id_of_input_tx = 0
        for input_tx in input_txs:
            amount = int(input_tx["amount"])
            from_addr = input_tx["from_addr"]
            private_key = input_tx["private_key"]
            previous_tx = input_tx["previous_tx"]

            data = self.create_input_transaction(amount, from_addr, private_key, previous_tx, id_of_input_tx, str_output_tx)
            str_input_tx = str_input_tx + "\n" + data
            id_of_input_tx += 1

        logging.debug("Str_input_tx : " + str_input_tx)

        transaction = str_input_tx + "\n" + str_output_tx

        transaction_hash = lib_cryptography.hash(transaction)
        # print("COUCOU")
        # print(transaction)
        # print("----")
        transaction = f"Tx Hash : {transaction_hash}\n" + transaction + "\n"


        logging.debug("transaction : " + transaction.replace("\n"," -- "))        

        return transaction


    def create_coinbase(self, amount, to_addr, block_num):
        logging.debug("create_coinbase(self, amount, to_addr)")
        logging.debug(f"create_coinbase(self,{amount},{to_addr}")

        transaction =   "Input :\n" \
                        "0\n" \
                        "Previous tx : Coinbase\n" \
                        f"Amount : {amount}\n" \
                        f"Block number : {block_num}\n" \
                        "Output :\n" \
                        "0\n" \
                        f"To : {to_addr}\n" \
                        f"Amount : {amount}" \


        transaction_hash = lib_cryptography.hash(transaction)
        transaction = f"Tx Hash : {transaction_hash}\n" + transaction + "\n"

        return transaction



if __name__ == '__main__':
    print("Do not launch this file manually. Launch examples.py instead")
