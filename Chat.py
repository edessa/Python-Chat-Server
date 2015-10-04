import socket
import logging

from threading import Thread
from Queue import Queue

from serverutils.logutils import ubuntu_logger as logger


clients = {}

def queue_sync(sock, queue):
    """
    :type queue: Queue
    """

    while True:
        logger.info("Ready to send")
        data = queue.get()
        logger.info("Sending: {}".format(data))

        for k, v in clients.items():
            if k != sock:
                sock.sendto(data, v)


def serve(sock, queue):

    while True:
        logger.info("Ready to receive")
        data, addr = sock.recvfrom(4096)
        clients[sock] = addr
        logger.info("Received: {} from {}".format(data, addr))
        queue.put_nowait(data)


if __name__ == '__main__':

    ports = [5241, 5240]
    socks = []
    queues = []
    threads = []

    logger.addHandler(logging.StreamHandler())

    for port in ports:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('0.0.0.0', port))
        socks.append(sock)

        q = Queue()
        queues.append(q)
        t = Thread(target=serve, args=(sock, q))
        t.start()
        threads.append(t)

        t = Thread(target=queue_sync, args=(sock, q))
        t.start()
        threads.append(t)

    try:
        map(Thread.join, threads)
    finally:
        map(socket.socket.close, socks)
