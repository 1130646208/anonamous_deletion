from flask_cors import CORS
from flask import Flask, request, jsonify
import time

from client.client import Client

a_client = Client()

if __name__ == '__main__':
    a_client.register_node('http://127.0.0.2:5222')
    a_client.register_node('http://127.0.0.5:6222')
    a_client.register_node('http://127.0.0.3:2335')
    for i in range(10):
        a_client.new_transaction(membership_proof='proof_0xaacddbb000'+str(i), transaction_type='txdata', content='0xab3562ba98')
