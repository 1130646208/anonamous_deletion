from client.database_connector import DBConnector
import time

con = DBConnector("127_0_0_1", '5002')
# con.save_secret('adsgadgasdg', 123)
# r = con.collection.update_many({"duration": {"$lt": 200}}, {"$set": {"expired": False}})
# con.check_expire('e95751d625d8944220e5a19f13848ee4')
print(con.delete_secret('ebcc4d1d67b745e4a6f086f6be47f90f'))
# secret = con.return_secret('e95751d625d8944220e5a19f13848ee4')
# print(secret)
