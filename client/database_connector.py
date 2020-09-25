from pymongo import MongoClient
import hashlib
import time
from bson import ObjectId


class DBConnector:
    def __init__(self, db_name, collection_name, mongo_url='localhost', mongo_port=27017):
        self.client = MongoClient(mongo_url, mongo_port)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def save_secret(self, secret: str, duration: int):
        # todo: add salt
        secret_to_insert = {
            "secret_content": secret,
            "secret_digest": hashlib.md5(secret.encode()).hexdigest(),
            "digest_salt": 0,
            "timestamp": time.time_ns(),
            "expired": False,
            "duration": duration,
        }
        self.collection.insert_one(secret_to_insert)

    def delete_secret(self, secret_digest: str):

        return self.collection.find_one_and_delete({"secret_digest": secret_digest})

    def return_secret(self, secret_digest):
        result = self.collection.find_one({"secret_digest": secret_digest})
        if result and self.check_expire(secret_digest):
            secret = result.get("secret_content")
        else:
            secret = None
        return secret

    def check_expire(self, secret_digest):
        result = self.collection.find_one({"secret_digest": secret_digest})
        if result:
            # 当时
            then = result.get("timestamp")
            # 现在
            now = time.time_ns()
            span = result.get("duration")
            if span == 0:
                pass
            elif now-then >= span:
                self.collection.update_one({"_id": result.get('_id')}, {'$set': {'expired': True}})
                return True

        return False









