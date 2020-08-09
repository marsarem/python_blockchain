import codecs
import hashlib
import ecdsa
import secrets
import logging
import hashlib

"""
The creation of private key and address are from this tutorial :
https://medium.com/free-code-camp/how-to-create-a-bitcoin-wallet-address-from-a-private-key-eca3ddd9c05f
https://github.com/Destiner/blocksmith/blob/master/blocksmith/bitcoin.py
"""

class Keys:
    @staticmethod
    def generate_private_key(): # This is not secure but for test purpose it is enough
        while True:
            bits = secrets.randbits(256)
            bits_hex = hex(bits)
            private_key = bits_hex[2:]
            if len(private_key) == 64: # This fix an error : some keys have en len of 63 et it cause an error
                break
        logging.info(f"Private Key : {private_key}")
        return private_key

    @staticmethod
    def generate_address(private_key):
        public_key = Keys.__private_to_public(private_key)
        address = Keys.__public_to_address(public_key)
        logging.info(f"Address : {address}")
        return address
        
    @staticmethod
    def generate_compressed_address(private_key):
        public_key = Keys.__private_to_compressed_public(private_key)
        address = Keys.__public_to_address(public_key)
        logging.info(f"Compressed Address : {address}")
        return address
    
    @staticmethod
    def __private_to_public(private_key):
        private_key_bytes = codecs.decode(private_key, 'hex')
        # Get ECDSA public key
        key = ecdsa.SigningKey.from_string(private_key_bytes, curve=ecdsa.SECP256k1).verifying_key
        key_bytes = key.to_string()
        key_hex = codecs.encode(key_bytes, 'hex')
        # Add bitcoin byte
        bitcoin_byte = b'04'
        public_key = bitcoin_byte + key_hex
        return public_key
    
    @staticmethod
    def __private_to_compressed_public(private_key):
        private_hex = codecs.decode(private_key, 'hex')
        # Get ECDSA public key
        key = ecdsa.SigningKey.from_string(private_hex, curve=ecdsa.SECP256k1).verifying_key
        key_bytes = key.to_string()
        key_hex = codecs.encode(key_bytes, 'hex')
        # Get X from the key (first half)
        key_string = key_hex.decode('utf-8')
        half_len = len(key_hex) // 2
        key_half = key_hex[:half_len]
        # Add bitcoin byte: 0x02 if the last digit is even, 0x03 if the last digit is odd
        last_byte = int(key_string[-1], 16)
        bitcoin_byte = b'02' if last_byte % 2 == 0 else b'03'
        public_key = bitcoin_byte + key_half
        return public_key
    
    @staticmethod
    def __public_to_address(public_key):
        public_key_bytes = codecs.decode(public_key, 'hex')
        # Run SHA256 for the public key
        sha256_bpk = hashlib.sha256(public_key_bytes)
        sha256_bpk_digest = sha256_bpk.digest()
        # Run ripemd160 for the SHA256
        ripemd160_bpk = hashlib.new('ripemd160')
        ripemd160_bpk.update(sha256_bpk_digest)
        ripemd160_bpk_digest = ripemd160_bpk.digest()
        ripemd160_bpk_hex = codecs.encode(ripemd160_bpk_digest, 'hex')
        # Add network byte
        network_byte = b'00'
        network_bitcoin_public_key = network_byte + ripemd160_bpk_hex
        network_bitcoin_public_key_bytes = codecs.decode(network_bitcoin_public_key, 'hex')
        # Double SHA256 to get checksum
        sha256_nbpk = hashlib.sha256(network_bitcoin_public_key_bytes)
        sha256_nbpk_digest = sha256_nbpk.digest()
        sha256_2_nbpk = hashlib.sha256(sha256_nbpk_digest)
        sha256_2_nbpk_digest = sha256_2_nbpk.digest()
        sha256_2_hex = codecs.encode(sha256_2_nbpk_digest, 'hex')
        checksum = sha256_2_hex[:8]
        # Concatenate public key and checksum to get the address
        address_hex = (network_bitcoin_public_key + checksum).decode('utf-8')
        wallet = base58(address_hex)
        return wallet

def base58(address_hex):
    alphabet = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'
    b58_string = ''
    # Get the number of leading zeros and convert hex to decimal
    leading_zeros = len(address_hex) - len(address_hex.lstrip('0'))
    # Convert hex to decimal
    address_int = int(address_hex, 16)
    # Append digits to the start of string
    while address_int > 0:
        digit = address_int % 58
        digit_char = alphabet[digit]
        b58_string = digit_char + b58_string
        address_int //= 58
    # Add '1' for each 2 leading zeros
    ones = leading_zeros // 2
    for one in range(ones):
        b58_string = '1' + b58_string
    return b58_string
    

def hash(input_):
    hash_sha = hashlib.sha256()
    hash_sha.update(input_.encode())
    output = hash_sha.hexdigest()
    logging.info(f"hash : input : {input_}, output : {output}")
    return output

def check_address(address):
    import re

    regex = r"[13][a-km-zA-HJ-NP-Z0-9]{26,33}"

    check_addr = re.findall(regex, address)
    if check_addr == [address]:
        return "Ok"
    else:
        return "ERROR"



if __name__ == "__main__":
    print("Do not launch this file manually. Launch examples.py instead")


    # A mettre dans test unitaire ??
    # import re

    # for i in range(500):
    #     regex = r"[13][a-km-zA-HJ-NP-Z0-9]{26,33}"
    #     try:
    #         print("----")
    #         private_key = Keys.generate_private_key()
    #         print(private_key)
    #         address = Keys.generate_address(private_key)
    #         print(address)
    #     except Exception as e:
    #         print(e)
    #         sys.exit(0)

    #     a = re.findall(regex, address)
    #     print(a)
    #     if a == []:
    #         print("-----")
    #         print(address)
    #         print(a)

    # print("terminé")