from client import client

a = client.Client()
pieces = a.split_secret(b'aGVsbG8gISEhIHNlY3JldCBzaGFyZSEhIQ====', 5, 8)
print(pieces)

recovered = a.recover_secret(pieces[3:8])
print(recovered)
