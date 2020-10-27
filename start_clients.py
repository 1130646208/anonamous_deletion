import os
from threading import Thread

PATH = os.getcwd()


def start_a_client(port_num):
    cmd = 'python ' + PATH + '\\client_main.py' + ' -p ' + str(port_num)
    print(cmd)
    result = os.system(cmd)


if __name__ == '__main__':
    port_base = 5005
    node_num = 10
    for i in range(node_num):
        t = Thread(target=start_a_client, args=(str(port_base+i), ))
        t.start()
