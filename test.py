import requests
import examples

# # data = {"height":"2", "number":"-1"}
# # a = requests.post("http://localhost:5000/node/get_blocks", data=data)

# # a = requests.get("http://localhost:5000/node/get_all_blocks")

# # a = requests.get("http://localhost:5000/node")

# # data = {"transaction":examples.Example_lib_transaction().ex_create_normal_transaction()}
# # a = requests.post("http://localhost:5000/node/send_transaction", data=data)

# data = {"address":"1CmUXbYYgCFJu99xXB6hVz5qyUUhm95AeS"}
# a = requests.post("http://localhost:5000/node/get_transactions", data=data)

# print(a.text)

# dicts = [{"addr":"truc","machin":"truc"}, {"addr":"bidule","machin":"bidule"}]
# from_addr = "truc"
# a = next((item for item in dicts if item["addr"] == from_addr), False)
# print(a)

# data = "Tx Hash : d076297e5fbd1e404daa163cf8a44cb80aa52fb4920e3fd20ce06f864ab49805\nInput :\n0\nPrevious tx : 133b5455ca6b4f724a6cb2b591be24759331776c557cebed8d332fbd098d834a\nFrom : 1CmUXbYYgCFJu99xXB6hVz5qyUUhm95AeS\nAmount : 100\nPublic Key : f900d5f5feb0ef62ddeef0356690c3cb974b7b1e3b53864024fb4b67cc04f7366babcb26e8cc3c886c036cffffe70788e7f2898e7fced40eab2daf6f2c92a132\nSignature : 324daef9cc9594cd9c7c63fc89a6e2ec0ba52066b70fdf20fdbbf55dd921461ef3b525fd60c2eb099dc273ba8604bdd73f3b782252836595d3d3c07bbda5ea6d\n1\nPrevious tx : 927900fc9b055a0f7671394b04e556cd0234b4ce179c4667cd674feff47b914e\nFrom : 1CmUXbYYgCFJu99xXB6hVz5qyUUhm95AeS\nAmount : 100\nPublic Key : f900d5f5feb0ef62ddeef0356690c3cb974b7b1e3b53864024fb4b67cc04f7366babcb26e8cc3c886c036cffffe70788e7f2898e7fced40eab2daf6f2c92a132\nSignature : 3ffc6d892521881cc043e97b185f419b32098337b8e114f290c4346866d632bdd1c12f73cc4950db431e5ac3b115499b3b1821e1835e53b0c2c8ae99b26234fb\nOutput :\n0\nTo : 1Bz3KJLQwHZ6kYSjBgHejVpxKFppP7ziT1\nAmount : 150\n1\nTo : 1CmUXbYYgCFJu99xXB6hVz5qyUUhm95AeS\nAmount : 50\n"
# with open("test.txt", "w") as fichier:
# 	fichier.write(data)

######################

# from multiprocessing import Process, Pipe
# import time

# # def f(conn):
# #   while True:
# #       data = conn.recv()
# #       calcul = data + " coucou"
# #       conn.send(calcul)
# #       time.sleep(2)

# class Truc:
#     def __init__(self, conn):
#         self.conn = conn
#         self.mine()

#     def mine(self):
#         # data = self.conn.recv()
#         self.conn.send("TEST")
#         time.sleep(5)
#         # while True:
#         #     time.sleep(2)

# if __name__ == '__main__':
#     parent_conn, child_conn = Pipe()
#     p = Process(target=Truc, args=(child_conn,), daemon=True)
#     p.start()
#     parent_conn.send(["2"])
#     print("A")
#     while True:
#         print("B")
#         print(parent_conn.recv())   # prints "[42, None, 'hello']"
#         parent_conn.send(["1"])


# ########################
# from multiprocessing import Process, Manager
# import time

# class Truc:
#     def __init__(self, aa):
#         print("T1", aa)
#         # print(help(aa))
#         aa.clear()
#         aa.update({"2":"2"})
#         aa.value = {"2":2}
#         time.sleep(2)
#         print("T2",aa)

# if __name__ == '__main__':
#     manager = Manager()

#     a = manager.dict()

#     p1 = Process(target=Truc, args=(a,), daemon=True)
#     p1.start()

#     print("N1",a)
#     a["BEBE"] = "bidule"
#     time.sleep(1)
#     print("N2",a)
#     time.sleep(30)


# class Truc:
#     def __init__(this):
#         this.truc = "wesh"
#         print(type(this))


# b = Truc()

# print(b.truc)