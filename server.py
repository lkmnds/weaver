import socket
import thread
import os
import os.path
import sys

VERSION = '0.0.1'
BANNER = "Weaver v%s" % VERSION
WEBPORT = 8000
PORT = 8012
BUFSIZE = 32768
F_BUFSIZE = 254 # 255 - 1 (length byte)
PATH = "./archives"

sockets = []

def new_client(sock, client):
    sock.send("Welcome to a Weaver v%s server!\n" % VERSION)
    sockets.append(sock)
    cli = client[0]
    while True:
        command = sock.recv(BUFSIZE)
        if command in ['ls', 'LS', 'list', 'LIST']:
            print 'list: %s' % cli
            k = os.listdir(PATH)
            sock.send(str(k))
        elif command[:4] == 'GET^':
            fn = command.split('^')[1]
            f = open(os.path.join(PATH, fn), 'rb')
            print 'sending %s' % fn
            l = f.read(F_BUFSIZE)
            length = chr(len(l))
            count = ord(length)
            while l:
                print 'Sending... [%d]' % (count)
                sock.send(length + l)
                l = f.read(F_BUFSIZE)
                length = chr(len(l))
                count += ord(length)
            print 'loop completed, sending \\x00'
            sock.send('\x00')
            f.close()
        elif command in ['^CLOSE']:
            print 'close: %s' % cli
            break
    sockets.remove(sock)
    sock.close()
    thread.exit()

def main():
    os.system("python -m SimpleHTTPServer &")
    print 'started HTTP server at %d' % WEBPORT
    tcp = socket.socket()
    HOST = "localhost"
    tcp.bind((HOST,PORT))
    tcp.listen(2)
    print 'listening at %s:%d' % (HOST,PORT)
    try:
        while True:
            con, cli = tcp.accept()
            thread.start_new_thread(new_client, (con, cli))
    except KeyboardInterrupt:
        print 'CTRL-C pressed, exiting.'
        for sock in sockets:
            sock.close()
        return 0

if __name__=='__main__':
    sys.exit(main())

