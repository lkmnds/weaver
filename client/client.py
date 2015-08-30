import socket
import time
import sys
import os

VERSION = '0.0.1'
BANNER = "Weaver v%s" % VERSION
PORT = 8012
BUFSIZE = 32768
F_BUFSIZE = 254 # 255 - 1 length byte

commands = [
    (['help'], 'prints help'),
    (['ls', 'list'], "list files on server archive"),
    (['exit'], 'exits connection'),
    (['lsc'], 'list files in client'),
    (['send'], 'send files in client to server'),
    ]

def printhelp():
    for c in commands:
        cmds = c[0]
        helptext = c[1]
        print '%s -- %s' % (cmds.join(' or '), helptext)

def main():
    tcp = socket.socket()
    print BANNER
    HOST = raw_input("IP: ")
    tcp.connect((HOST,PORT))
    print tcp.recv(BUFSIZE)
    while True:
        cmd = raw_input('@%s$ ' % HOST)
        if cmd == 'help':
            printhelp()
        elif cmd == 'exit':
            tcp.send("^CLOSE")
            tcp.close()
            return 0
        elif cmd in ['ls', 'list']:
            tcp.send('ls')
            lsdirs = tcp.recv(BUFSIZE)
            _lsdirs = eval(lsdirs)
            for d in _lsdirs:
               sys.stdout.write("%s " % d)
            sys.stdout.write("\n")
        elif cmd in ['lsc']:
            for d in os.listdir('.'):
                sys.stdout.write("%s " % d)
            sys.stdout.write("\n")
        elif cmd[:4] == 'get ':
            fname = cmd[4:]
            print 'getting %s' % fname
            tcp.send("GET^%s" % fname)
            f = open(fname, 'wb')
            length = ord(tcp.recv(1))
            count = length
            l = tcp.recv(length)
            while (l):
                print "Receiving... [%d]" % count
                #print repr(l)
                f.write(l)
                length = ord(tcp.recv(1))
                if chr(length) == '\x00': break
                l = tcp.recv(length)
                count += length
            f.write('')
            f.close()
            print 'done!'
        elif cmd[:5] == 'send ':
            fname = cmd[5:]
            print 'sending %s' % fname
            tcp.send("SEND^%s" % fname)
            f = open(fname, 'rb')
            l = f.read(F_BUFSIZE)
            length = chr(len(l))
            count = ord(length)
            while l:
                print 'Sending... [%d]' % (count)
                tcp.send(length + l)
                l = f.read(F_BUFSIZE)
                length = chr(len(l))
                count += ord(length)
            print 'loop completed, sending \\x00'
            tcp.send('\x00')
            f.close()
            

main()
