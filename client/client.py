import socket
import time
import sys

VERSION = '0.0.1'
BANNER = "Weaver v%s" % VERSION
PORT = 8012
BUFSIZE = 32768

commands = [
    (['help'], 'prints help'),
    (['ls', 'LS', 'list', 'LIST'], "list files on server archive"),
    (['exit'], 'exits connection'),
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
        elif cmd in ['ls', 'LS', 'list', 'LIST']:
            tcp.send('ls')
            lsdirs = tcp.recv(BUFSIZE)
            _lsdirs = eval(lsdirs)
            for d in _lsdirs:
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

main()
