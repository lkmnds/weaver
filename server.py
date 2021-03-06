import socket
import thread
import os
import os.path
import sys
import subprocess

VERSION = '0.0.1'
BANNER = "Weaver v%s" % VERSION
WEBPORT = 8000
PORT = 8012
BUFSIZE = 32768
F_BUFSIZE = 254 # 255 - 1 (length byte)
PATH = "./archives"
USAGE = "use: %s HOST" % sys.argv[0]

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
        elif command[:5] == 'SEND^':
            fname = command.split('^')[1]
            f = open(os.path.join(PATH, fname), 'wb')
            length = ord(sock.recv(1))
            count = length
            l = sock.recv(length)
            while (l):
                print "Receiving... [%d]" % count
                #print repr(l)
                f.write(l)
                length = ord(sock.recv(1))
                if chr(length) == '\x00': break
                l = sock.recv(length)
                count += length
            f.write('')
            f.close()
            print 'done!'
        elif command in ['^CLOSE']:
            print 'close: %s' % cli
            break
    sockets.remove(sock)
    sock.close()
    thread.exit()

def main():
    webserver = subprocess.Popen(['python -m SimpleHTTPServer'], stdout=subprocess.PIPE, shell=True)
    print 'started HTTP server at %d' % WEBPORT
    tcp = socket.socket()
    if len(sys.argv) == 2:
        HOST = sys.argv[1]
    elif len(sys.argv) == 1:
        HOST = "localhost"
    else:
        print USAGE
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
