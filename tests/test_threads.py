from threading import Thread
import time


def func():
    time.sleep(1)
    print('thread done')


threads = [Thread(target=func) for _ in range(5)]

tik = time.time()

[(thread.start()) for thread in threads]
[(thread.join()) for thread in threads]

tok = time.time()

print(tok - tik)
