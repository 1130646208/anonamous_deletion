import threading


class Baa:
    def __init__(self):
        self.a = [1, 2, 3, 4, 5, 6]

    def get(self):
        return self.a[0]
