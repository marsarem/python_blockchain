import re
import sys
import codecs
import ecdsa
try:
    import lib_cryptography
    import search_in_blocks
    import lib_node
except :
    from lib import lib_cryptography
    from lib import search_in_blocks
    from lib import lib_node



class VerifyBlock:
    def __init__(self, block, hash_, previous_block_hash, block_height, coinbase):
        self.block = block
        self.hash_ = hash_

        self.previous_block_hash = previous_block_hash
        self.block_height = block_height

        self.coinbase = coinbase


    def check_hash(self):
        hash_ = lib_cryptography.hash(self.block)
        if hash_ != self.hash_:
            return "ERROR","Hash does not match"
        else:
            return "Ok", "Block hash match"

    def verify_block(self):
        try:
            header, transactions = self.block.split("\n\n", maxsplit=1)

            ## Header : 
            block_number, previous_block_hash, nonce = header.split("\n")

            # Block number
            block_number = re.findall(r"Block ([0-9]*)", block_number)
            if block_number == []:
                return "ERROR", "Error block number not found"
            if int(block_number[0]) != self.block_height:
                print(int(block_number[0]), self.block_height)
                return "ERROR", "Error block number"
 
            # Previous block hash
            previous_block_hash = re.findall(r"Previous Block Hash : ([0-9A-z]*)", previous_block_hash)
            if previous_block_hash == []:
                return "ERROR", "Error previous block hash not found"
            if previous_block_hash[0] != self.previous_block_hash:
                return "ERROR", "Error previous block hash"
 
            # Nonce
            nonce = re.findall(r"Nonce : ([0-9]*)", nonce)
            if nonce == []:
                return "ERROR", "Error nonce not found"
            

            ## Transactions : 
            transactions = transactions.split("\n\n")
            for i in range(len(transactions)):

                tx_number, tx_hash, tx_input_ouput = transactions[i].split("\n",maxsplit=2)

                # Transaction Number
                tx_number = re.findall(r"Transaction ([0-9]+):", tx_number)
                if tx_number == []:
                    return "ERROR", "Transaction number not found"
                if int(tx_number[0]) != i:
                    return "ERROR", "Transaction number doesn't match"

                # Transaction Hash
                tx_hash = re.findall(r"Tx Hash : ([A-z0-9]+)", tx_hash)
                if tx_hash == []:
                    return "ERROR", "Transaction hash not found"
                tx_hash = tx_hash[0]

                hash_ = lib_cryptography.hash(tx_input_ouput)
                if hash_ != tx_hash:
                    return "ERROR", "Transaction hash doesn't match"

                # Split inputs and outputs from a transaction
                tx_inputs = re.findall(r"Input :\n([A-z0-9\n\s:]*)\nOutput", tx_input_ouput)
                if tx_inputs == []:
                    return "ERROR", "Transaction inputs not found"
                tx_inputs = tx_inputs[0]

                tx_outputs = re.findall(r"Output :\n([A-z0-9\n\s:]*)", tx_input_ouput)
                if tx_outputs == []:
                    return "ERROR", "Transaction outputs not found"
                tx_outputs = tx_outputs[0]


                if i == 0: # The first transaction needs to be the COINBASE
                    # Check input
                    regex_input_coinbase = r"0\nPrevious tx : Coinbase\nAmount : ([0-9]+)"
                    search_coinbase_input = re.search(regex_input_coinbase, tx_inputs)
                    if search_coinbase_input == None:
                        return "ERROR", "Coinbase input not found"

                    amount_coinbase = search_coinbase_input.group(1)
                    if int(amount_coinbase) != self.coinbase:
                        return "ERROR", "Wrong coinbase amount"

                    regex_coinbase_num_block = r"Block number : ([0-9]+)"
                    search_coinbase_num_block = re.search(regex_coinbase_num_block, tx_inputs)
                    if search_coinbase_num_block == None:
                        return "ERROR", "Coinbase block number not found"

                    block_num = search_coinbase_num_block.group(1)
                    if int(block_num) != self.block_height:
                        return "ERROR","Coinbase block number does not match"

                    # Check output
                    regex_output_coinbase = r"0\nTo : ([A-z0-9]+)\nAmount : ([0-9]+)"
                    search_coinbase_output = re.search(regex_output_coinbase, tx_outputs)
                    if search_coinbase_output == None:
                        return "ERROR", "Coinbase output not found"

                    addr_receiver = search_coinbase_output.group(1)
                    if lib_cryptography.check_address(addr_receiver) != "Ok":
                        return "ERROR", "Error in coinbase reciever address"

                    amount_sent = search_coinbase_output.group(2)
                    if int(amount_sent) != self.coinbase:
                        return "ERROR", "Wrong coinbase amount"

                else: # Normal trasaction
                    # OSEF ?
                    # A IMPREMENTER
                    # found = False
                    # for i in range(len(self.list_transactions_pending)):
                    #     if tx_hash == self.list_transactions_pending[0]:
                    #         found = True
                    # if found == False:
                    #     return "ERROR", "Transaction not found in list transactions pending"
                        
                    

                    # Output
                    sum_output = 0

                    regex_output_tx = r"[0-9]+\nTo : ([A-z0-9]+)\nAmount : ([0-9]+)"
                    search_output_tx = re.findall(regex_output_tx, tx_outputs)
                    if search_output_tx == []:
                        return "ERROR", "Input tx not found"

                    input_txs = []
                    for i in range(len(search_output_tx)):
                        sum_output += int(search_output_tx[i][1])
                        address = search_output_tx[i][0]
                        if lib_cryptography.check_address(address) != "Ok":
                            return "ERROR", "Address check failed"


                    # Input
                    sum_input = 0
                    
                    regex_input_tx = r"[0-9]+\nPrevious tx : ([A-z0-9]+)\nFrom : ([A-z0-9]+)\nAmount : ([0-9]+)\nPublic Key : ([A-z0-9]+)\nSignature : ([A-z0-9]+)"
                    search_input_tx = re.findall(regex_input_tx, tx_inputs)
                    if search_input_tx == []:
                        return "ERROR", "Input tx not found"

                    input_txs = []
                    for i in range(len(search_input_tx)):
                        address = search_input_tx[i][1]
                        sum_input += int(search_input_tx[i][2])
                        signature = search_input_tx[i][4]
                        public_key = search_input_tx[i][3]
                        message_signed = f"Public Key : {public_key}\nOutput :\n{tx_outputs}"
                        signature_hex = codecs.decode(signature.encode(), 'hex')

                        public_key_hex = codecs.decode(public_key.encode(), 'hex')
                        verify_key = ecdsa.VerifyingKey.from_string(public_key_hex, curve=ecdsa.SECP256k1)
                        try:
                            verify_key.verify(signature_hex, message_signed.encode())
                        except ecdsa.keys.BadSignatureError as e:
                            return "ERROR", "Bad signature"


                        # Check if the previous transaction exists,
                        #  if the amount of the previous tx is >= amount of this transaction,
                        #  if the previous tx was not used before
                
                        previous_tx_hash = search_input_tx[i][0]

                        # We get all the blocks of the blockchain
                        blocks = lib_node.Database().get_all_blocks()

                        # We check if the previous_tx exists
                        previous_tx_exists = search_in_blocks.get_transactions_with_hash(blocks, previous_tx_hash)
                        if previous_tx_exists[0] != "Found":
                            return "ERROR", "Previous transaction not found"

                        # We check if the previous tx was not used before
                        previous_tx_found = search_in_blocks.get_transactions_with_hash_in_previous_tx(blocks, previous_tx_hash, address)
                        if previous_tx_found[0] == "Found":
                            return "ERROR", "Previous transaction already spent"


                    if sum_input != sum_output:
                        return "ERROR", "Sum input and output doesn't match"

                    if sum_input == 0:
                        return "ERROR", "Transaction with 0 coin"

            return "Ok",
        except Exception as e:
            raise e
            return "ERROR", f"Split block error"

    
class VerifyTransaction:
    def __init__(self, transaction):
        self.transaction = transaction
        if self.transaction[-1] == "\n":
            self.transaction = self.transaction[:-1]


    def verify_transaction(self):
        try:
            tx_hash, tx_input_ouput = self.transaction.split("\n",maxsplit=1)

            # Transaction Hash
            tx_hash = re.findall(r"Tx Hash : ([A-z0-9]+)", tx_hash)
            if tx_hash == []:
                return "ERROR", "Transaction hash not found"
            tx_hash = tx_hash[0]

            hash_ = lib_cryptography.hash(tx_input_ouput)
            if hash_ != tx_hash:
                return "ERROR", "Transaction hash doesn't match"

            # Split inputs and outputs from a transaction
            tx_inputs = re.findall(r"Input :\n([A-z0-9\n\s:]*)\nOutput", tx_input_ouput)
            if tx_inputs == []:
                return "ERROR", "Transaction inputs not found"
            tx_inputs = tx_inputs[0]

            tx_outputs = re.findall(r"Output :\n([A-z0-9\n\s:]*)", tx_input_ouput)
            if tx_outputs == []:
                return "ERROR", "Transaction outputs not found"
            tx_outputs = tx_outputs[0]

            # Output
            sum_output = 0

            regex_output_tx = r"[0-9]+\nTo : ([A-z0-9]+)\nAmount : ([0-9]+)"
            search_output_tx = re.findall(regex_output_tx, tx_outputs)
            if search_output_tx == []:
                return "ERROR", "Input tx not found"

            input_txs = []
            for i in range(len(search_output_tx)):
                sum_output += int(search_output_tx[i][1])
                address = search_output_tx[i][0]
                if lib_cryptography.check_address(address) != "Ok":
                    return "ERROR", "Address check failed"

            # Input
            sum_input = 0
            
            regex_input_tx = r"[0-9]+\nPrevious tx : ([A-z0-9]+)\nFrom : ([A-z0-9]+)\nAmount : ([0-9]+)\nPublic Key : ([A-z0-9]+)\nSignature : ([A-z0-9]+)"
            search_input_tx = re.findall(regex_input_tx, tx_inputs)
            if search_input_tx == []:
                return "ERROR", "Input tx not found"

            input_txs = []
            for i in range(len(search_input_tx)):
                address = search_input_tx[i][1]
                sum_input += int(search_input_tx[i][2])
                signature = search_input_tx[i][4]
                public_key = search_input_tx[i][3]
                message_signed = f"Public Key : {public_key}\nOutput :\n{tx_outputs}"
                signature_hex = codecs.decode(signature.encode(), 'hex')

                public_key_hex = codecs.decode(public_key.encode(), 'hex')
                verify_key = ecdsa.VerifyingKey.from_string(public_key_hex, curve=ecdsa.SECP256k1)
                try:
                    verify_key.verify(signature_hex, message_signed.encode())
                except ecdsa.keys.BadSignatureError as e:
                    return "ERROR", "Bad signature"


                # Check if the previous transaction exists,
                #  if the amount of the previous tx is >= amount of this transaction,
                #  if the previous tx was not used before
        
                previous_tx_hash = search_input_tx[i][0]

                # We get all the blocks of the blockchain
                blocks = lib_node.Database().get_all_blocks()

                # We check if the previous_tx exists
                previous_tx_exists = search_in_blocks.get_transactions_with_hash(blocks, previous_tx_hash)
                if previous_tx_exists[0] != "Found":
                    return "ERROR", "Previous transaction not found"

                # We check if the previous tx was not used before
                previous_tx_found = search_in_blocks.get_transactions_with_hash_in_previous_tx(blocks, previous_tx_hash, address)
                if previous_tx_found[0] == "Found":
                    return "ERROR", "Previous transaction already spent"




            if sum_input != sum_output:
                return "ERROR", "Sum input and output doesn't match"

            if sum_input == 0:
                return "ERROR", "Transaction with 0 coin"


            return "Ok"

        except Exception as e:
            print(e)
            return "ERROR", "Verify transaction failed"


def get_transactions_hash_in_block(block):
    list_transactions_hash = []
    try:
        header, transactions = block.split("\n\n", maxsplit=1)

        transactions = transactions.split("\n\n")
        for i in range(len(transactions)):

            tx_number, tx_hash, tx_input_ouput = transactions[i].split("\n",maxsplit=2)

            # Transaction Hash
            tx_hash = re.findall(r"Tx Hash : ([A-z0-9]+)", tx_hash)
            if tx_hash == []:
                continue
            tx_hash = tx_hash[0]

            list_transactions_hash.append(tx_hash)

        return list_transactions_hash
    except Exception as e:
        print(e)
        raise e
        return "ERROR", f"Get transactions hash error"


def get_tx_hash_from_tx(transaction):
    regex_tx_hash= r"Tx Hash : ([A-z0-9]+)"
    search_tx_hash = re.findall(regex_tx_hash, transaction)
    if search_tx_hash == []:
        return "ERROR", "Input tx not found"

    return search_tx_hash[0]




if __name__ == "__main__":
    print("Do not lauch this file.")
    # with open("test.txt", "r") as fichier:
    #     data = fichier.read().split("\n--\n")
    # hash_ = data[0]
    # block = data[1]
    # previous_block_hash = "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
    # block_height = 2
    # coinbase = 100
    # verify = VerifyBlock(block, hash_, previous_block_hash, block_height, coinbase)
    # print(verify.check_hash())
    # print(verify.verify_block())