import json
import codecs
import ecdsa
import requests
import sys


from lib import lib_cryptography
from lib import lib_transactions

class Wallet():
    def __init__(self):
        self.path_config = "config/config_wallet.json"

        self.get_config()


    def get_config(self):
        with open(self.path_config, "r") as file:
            config = json.load(file)

        self.addresses = config["addresses"]
        self.node = config["node"]


    def create_address(self):
        private_key = lib_cryptography.Keys.generate_private_key()
        address = lib_cryptography.Keys.generate_address(private_key)
        
        with open(self.path_config, "r") as file:
            config = json.load(file)

        config["addresses"].append({"private_key":private_key, "address":address})

        with open(self.path_config, "w") as file:
            json.dump(config, file, indent=4)

        self.get_config()

        print("Keys generated")
        return private_key, address


    def delete_address(self, private_key):
        address = lib_cryptography.Keys.generate_address(private_key)

        with open(self.path_config, "r") as file:
            config = json.load(file)

        dict_addr = {"private_key":private_key, "address":address}

        try:
            config["addresses"].remove(dict_addr)
            with open(self.path_config, "w") as file:
                json.dump(config, file, indent=4)

            self.get_config()

            print("Address deleted")

        except ValueError:
            print("Address not found")


    def send_money(self, from_addr, from_private_key, to_addr, amount):
        # Récup tt les transactions
        # Indentifier celles qui n'ont pas été utilisées
        # On les prend au fur et à mesure pour envoyer

        # We get all transactions with from_addr
        data = {"address":from_addr}
        req_transactions = requests.post(f"{self.node}/node/get_transactions", data=data)
        
        if req_transactions.status_code != 200:
            return "ERROR", f"Node responce : {req_transactions.text}"

        transactions = req_transactions.json()


        # Identifier les transactions dont le tx_hash n'est pas utilisé dans un output
        free_transactions = []

        i = 0
        for transaction in transactions:
            tx_hash_ = transaction["transaction_headers"]["transaction_hash"]
            found = False

            for transaction2 in transactions:
                for input_ in transaction2["inputs"]:
                    if tx_hash_ == input_["previous_tx"]:
                        found = True
                        break

                if found == True:
                    break

            if found == False:
                free_transactions.append(transaction)

            i += 1


        # Creation of the transaction :
        transaction_used = []
        amount_left = int(amount)

        for transaction in free_transactions:
            amount_in_tx = next((item for item in transaction["outputs"] if item["addr"] == from_addr), False)
            if amount_in_tx == False:
                continue

            amount_in_tx = amount_in_tx["amount"]

            if amount_left > 0:
                transaction_used.append(
                    {"tx_hash":transaction["transaction_headers"]["transaction_hash"], 
                    "amount":int(amount_in_tx)})
                amount_left -= int(amount_in_tx)

        if amount_left > 0:
            return "ERROR", "Not enough funds"

         #Creation of inputs
        
        input_txs = []
        for transaction in transaction_used:
            input_txs.append({
                "amount":transaction["amount"],
                "from_addr":from_addr,
                "private_key":from_private_key,
                "previous_tx":transaction["tx_hash"]
                })


        output_txs = [{"amount":amount, "to_addr":to_addr}]

        # On envoie l'exédent à l'addresse de l'exp
        if amount_left != 0:
            output_txs.append({"amount":-amount_left, "to_addr":from_addr})

        final_transaction = lib_transactions.Transaction().create_transaction(input_txs, output_txs)

        # print(final_transaction)

        # Send the transaction to the node
        data = {"transaction":final_transaction}
        req_send_transactions = requests.post(f"{self.node}/node/send_transaction", data=data)
        
        if req_send_transactions.status_code != 200:
            return ["ERROR", f"Node response : {req_send_transactions.text}"]

        else:
            return ["Ok"]


    def list_addresses_amount(self):
        text = ""
        for address in self.addresses:
            address = address["address"]

            # We get all transactions with from_addr
            data = {"address":address}
            req_transactions = requests.post(f"{self.node}/node/get_transactions", data=data)
            if req_transactions.status_code != 200:
                return "ERROR", f"Node responce : {req_transactions.text}"

            transactions = req_transactions.json()

            # Identifier les transactions dont le tx_hash n'est pas utilisé dans un output
            free_transactions = []
            i = 0
            for transaction in transactions:
                tx_hash_ = transaction["transaction_headers"]["transaction_hash"]
                found = False

                for transaction2 in transactions:
                    for input_ in transaction2["inputs"]:
                        if tx_hash_ == input_["previous_tx"]:
                            found = True
                            break

                    if found == True:
                        break

                if found == False:
                    free_transactions.append(transaction)
                i += 1

            amount = 0
            for transaction in free_transactions:
                amount_in_tx = next((item for item in transaction["outputs"] if item["addr"] == address), False)
                if amount_in_tx == False:
                    continue
                
                amount_in_tx = amount_in_tx["amount"]
                amount += int(amount_in_tx)

            text += f"{address} : {amount}\n"
        return "Ok",text


class Cli:
    def __init__(self):
        print("Wallet V1")
        self.wallet = Wallet()

        while True:
            self.menu()

    def menu(self):
        print("1. Créer une addresse")
        print("2. Lister les addresses avec leur solde")
        print("3. Lister les transactions pour une addresse (output dans le fichier test.txt)")
        print("4. Envoyer de l'argent")
        ask = input("> ")
        if ask == "1":
            private_key, address = self.wallet.create_address()
            print("private_key :",private_key)
            print("address :",address)

        elif ask == "2":
            return_ = self.wallet.list_addresses_amount()
            if return_[0] != "Ok":
                print(return_)
            else:
                print(return_[1])

        elif ask == "3":
            print("En cours de dev")

        elif ask == "4":
            print("Envoyer de l'argent")
            from_addr = input("Adresse expéditeur : ")
            from_private_key = input("Clé privée expéditeur : ")
            to_addr = input("Adresse destinataire : ")
            amount = int(input("Quantité de crypto : "))
            
            send_return = self.wallet.send_money(from_addr, from_private_key, to_addr, amount)
            if send_return[0] == "Ok":
                print("Argent envoyé")
            else:
                print(send_return)

        input("Press ENTER to continue...")
        print()



if __name__ == "__main__":
    Cli()

    # print(Wallet().list_addresses_amount()[1])

    # wallet = Wallet()
    # # wallet.create_address()
    # # wallet.delete_address("ba0fb2e63a3ccf38312f94dc332f55abeba4e4d2ca1004da68222866b10d695b")
    
    # from_addr = "1CmUXbYYgCFJu99xXB6hVz5qyUUhm95AeS"
    # from_private_key = "8528ee7d1bb67e9195c37ffb9551fe67d29bc382acf76956a19225676d207201"
    # to_addr = "1Bz3KJLQwHZ6kYSjBgHejVpxKFppP7ziT1"
    # amount = 150
    # a = wallet.send_money(from_addr, from_private_key, to_addr, amount)
    # print(a)