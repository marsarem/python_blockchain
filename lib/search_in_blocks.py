import re
import sys

"""
A quoi sert ce fichier ? 
- a trouver tt les transactions auquelles une addresse X a participé
- a trouver une transaction avec son hash

"""


class GetTransactions:
    def __init__(self, blocks): #, address="", tx_hash=""):
        # self.address = address
        self.blocks = blocks 

        blocks = []
        for i in self.blocks:
            if isinstance(i, dict) == True:
                blocks.append(i["block"])
            else:
                blocks.append(i)

        self.blocks = blocks

        # self.blocks is a list of str blocks
        # We will assume that the blocks are correct. 
        # Maybe the blocks should be checked in a real blockchain

        # get() will return a list containing all the transactions which are in all the blocks
        # This is the format of a transaction : 
        """
        {
            "block_headers":{"height":height, "previous_block_hash":, "nonce":},
            "transaction_headers":{"transaction_hash":},
            "inputs":[{"addr":addr, "amount":amount, "last_tx_hash":last_tx_hash}, ...],
            "outputs":[{"addr":addr, "amount":amount}, ...]
        }
        """

    def get(self):
        list_transactions = [] 

        for block in self.blocks:
            if block == "GENESIS BLOCK":
                continue
            try: 
                
                header, transactions = block.split("\n\n", maxsplit=1)

                ## Header : 
                block_number, previous_block_hash, nonce = header.split("\n")

                # Block number
                block_number = re.findall(r"Block ([0-9]*)", block_number)
                block_number = block_number[0]
     
                # Previous block hash
                previous_block_hash = re.findall(r"Previous Block Hash : ([0-9A-z]*)", previous_block_hash)
                previous_block_hash = previous_block_hash[0]
     
                # Nonce
                nonce = re.findall(r"Nonce : ([0-9]*)", nonce)
                nonce = nonce[0]
                

                ## Transactions : 
                transactions = transactions.split("\n\n")
                for i in range(len(transactions)):
                    transaction = {
                        "block_headers":{"height":block_number, "previous_block_hash":previous_block_hash, "nonce":nonce}
                    }

                    tx_number, tx_hash, tx_input_ouput = transactions[i].split("\n",maxsplit=2)

                    # Transaction Number
                    tx_number = re.findall(r"Transaction ([0-9]+):", tx_number)
                    tx_number = tx_number[0]

                    # Transaction Hash
                    tx_hash = re.findall(r"Tx Hash : ([A-z0-9]+)", tx_hash)
                    tx_hash = tx_hash[0]

                    transaction["transaction_headers"] = {"transaction_hash":tx_hash}


                    # Split inputs and outputs from a transaction
                    tx_inputs = re.findall(r"Input :\n([A-z0-9\n\s:]*)\nOutput", tx_input_ouput)
                    tx_inputs = tx_inputs[0]

                    tx_outputs = re.findall(r"Output :\n([A-z0-9\n\s:]*)", tx_input_ouput)
                    tx_outputs = tx_outputs[0]

                    list_inputs = []
                    list_outputs = []

                    if i == 0: # The first transaction is the COINBASE
                        # Check input
                        regex_input_coinbase = r"0\nPrevious tx : Coinbase\nAmount : ([0-9]+)"
                        search_coinbase_input = re.search(regex_input_coinbase, tx_inputs)

                        amount_coinbase = search_coinbase_input.group(1)

                        # Check output
                        regex_output_coinbase = r"0\nTo : ([A-z0-9]+)\nAmount : ([0-9]+)"
                        search_coinbase_output = re.search(regex_output_coinbase, tx_outputs)

                        addr_receiver = search_coinbase_output.group(1)
                        amount_sent = search_coinbase_output.group(2)

                        list_inputs.append({
                            "addr":"COINBASE", "amount":str(amount_coinbase), "previous_tx":"COINBASE"
                            })

                        list_outputs.append({
                            "addr":addr_receiver, "amount":str(amount_sent)
                            })

                    else: # Normal transaction
                        # Output
                        sum_output = 0

                        regex_output_tx = r"[0-9]+\nTo : ([A-z0-9]+)\nAmount : ([0-9]+)"
                        search_output_tx = re.findall(regex_output_tx, tx_outputs)

                        for i in range(len(search_output_tx)):
                            amount_sent = int(search_output_tx[i][1])
                            sum_output += amount_sent

                            address = search_output_tx[i][0]

                            list_outputs.append({
                            "addr":address, "amount":str(amount_sent)
                            })

                        # Input
                        sum_input = 0
                        
                        regex_input_tx = r"[0-9]+\nPrevious tx : ([A-z0-9]+)\nFrom : ([A-z0-9]+)\nAmount : ([0-9]+)\nPublic Key : ([A-z0-9]+)\nSignature : ([A-z0-9]+)"
                        search_input_tx = re.findall(regex_input_tx, tx_inputs)

                        for i in range(len(search_input_tx)):
                            amount = int(search_input_tx[i][2])
                            sum_input += amount
                            signature = search_input_tx[i][4]
                            public_key = search_input_tx[i][3] 

                            address = search_input_tx[i][1]
                            previous_tx = search_input_tx[i][0]

                            list_inputs.append({
                            "addr":address, "amount":str(amount), "previous_tx":previous_tx
                            })

                    transaction["inputs"] = list_inputs
                    transaction["outputs"] = list_outputs
                    list_transactions.append(transaction)

                
            except Exception as e:
                # raise e
                # print(e)
                # continue
                return "ERROR", f"Error while searching in block ({e})"
        return "Ok",list_transactions


def get_transactions_for_addr(blocks, address):
    transactions_with_addr = [] # This will be the list of the transactions in which there is the address

    # Get all transactions from the blocks
    transactions = GetTransactions(blocks).get()
    if transactions[0] == "Ok":
        transactions = transactions[1]
    else:
        return transactions


    for transaction in transactions:
        # Check if there is the address in inputs or outputs
        
        is_address = False #Is the address in the block ?

        # Check inputs :
        inputs = transaction["inputs"]
        for i in range(len(inputs)):
            if inputs[i]["addr"] == address:
                is_address = True
                break

        # Check outputs :
        outputs = transaction["outputs"]
        for i in range(len(outputs)):
            if outputs[i]["addr"] == address:
                is_address = True
                break

        if is_address == True:
            transactions_with_addr.append(transaction)
    return transactions_with_addr


def get_transactions_with_hash(blocks, hash_):
    
    # Get all transactions from the blocks
    transactions = GetTransactions(blocks).get()
    if transactions[0] == "Ok":
        transactions = transactions[1]
    else:
        return transactions


    for transaction in transactions:

        tx_hash = transaction["transaction_headers"]["transaction_hash"]

        if tx_hash == hash_:
            return ["Found",transaction]

    return ["Not Found"]


def get_transactions_with_hash_in_previous_tx(blocks, hash_, address):

    # Get all transactions from the blocks
    transactions = GetTransactions(blocks).get()
    if transactions[0] == "Ok":
        transactions = transactions[1]
    else:
        return transactions


    for transaction in transactions:

        inputs = transaction["inputs"]
        for i in range(len(inputs)):
            if inputs[i]["previous_tx"] == hash_ and inputs[i]["addr"] == address:
                return ["Found",transaction]


    return ["Not Found"]

    

if __name__ == "__main__":
    print("Do not lauch this file. Use exemple.py instead")