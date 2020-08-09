import lib_cryptography

a = """Input :
0
Previous tx : None
From : 18rfEAaWzD2ts27V5QNpLjxsnNFkxsmUwx
Amount : 300
Public Key : fdf5c926a3a014386fd87b572fffea66a9f3d3dbdca0568fca50c5c84b980bc56ce93f3db54dee3067421e8dc2e7b0b07db1ae8ab6a16c9a8844f34602f610c6
Signature : d699a60759892c04e23b34e144cd4891d5d7216cdb83b0c6e8d69a2a47abcd7beded5ebf8139e138de7b7a7b70071839e5fd5a06bdcfe433392a6a820583cf6c
1
Previous tx : None
From : 18rfEAaWzD2ts27V5QNpLjxsnNFkxsmUwx
Amount : 1
Public Key : fdf5c926a3a014386fd87b572fffea66a9f3d3dbdca0568fca50c5c84b980bc56ce93f3db54dee3067421e8dc2e7b0b07db1ae8ab6a16c9a8844f34602f610c6
Signature : a9d6339482a1773eadbf13c6ba044f092e8620a7a2b2f375294f9f5d70351cdce40d8982207e45dee67d5c01cfb2deef4a67c9dba93841166eee1960002d9364
Output :
0
To : 18rfEAaWzD2ts27V5QNpLjxsnNFkxsmUwx
Amount : 300
1
To : 1J914gcuhAakwuXreHCxiHVufdNoj33F2
Amount : 100"""

a = "Input :\n0\nPrevious tx : Coinbase\nAmount : 100\nOutput :\n0\nTo : 17zbs7vXMQ47x3NJBXyvFPubFpqdAdySec\nAmount : 100"

print(a)

print(lib_cryptography.hash(a))
print(lib_cryptography.hash(a+"\n"))