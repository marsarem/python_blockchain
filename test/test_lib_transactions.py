import unittest

from mon_module import get

# Cette classe est un groupe de tests. Son nom DOIT commencer
# par 'Test' et la classe DOIT hériter de unittest.TestCase.
class TestFonctionGet(unittest.TestCase):

    # Chaque méthode dont le nom commence par 'test_'
    # est un test.
    def test_get_element(self):

        simple_comme_bonjour = ('pomme', 'banane')
        element = get(simple_comme_bonjour, 0)

        # Le test le plus simple est un test d'égalité. On se
        # sert de la méthode assertEqual pour dire que l'on
        # s'attend à ce que les deux éléments soient égaux. Sinon
        # le test échoue.
        self.assertEqual(element, 'pomme')

# Ceci lance le test si on exécute le script
# directement.
if __name__ == '__main__':
    unittest.main()


# private_key = lib_cryptography.Keys.generate_private_key()
#     address = lib_cryptography.Keys.generate_address(private_key)
#     print(private_key)
#     print(address)

#     input_tx = [{
#         "amount":300,
#         "from_addr":address,
#         "private_key":private_key,
#         "previous_tx":"None"
#     },{
#         "amount":300,
#         "from_addr":address,
#         "private_key":private_key,
#         "previous_tx":"None"
#     }]
#     output_txs = [{
#         "amount":300,
#         "to_addr":address
#     },{
#         "amount":200,
#         "to_addr":address
#     }
#     ]
#     a = Transaction().create_transaction(input_tx, output_txs)
#     print("---")
#     print(a)