import struct

PROTO_PORT = 8012
PROTO_VERSION = '1'
BUFFER_SIZE = 32768

class ConfigFile:
    def __init__(self):
        self.config = {}

    def initialize(self, file_object):
        for line in file_object.readlines():
            configline = line.split(' ')
            print(configline)
            if len(configline) > 1:
                self.config[configline[0]] = configline[1]

# helpers for TCP
def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf

def send_msg(sock, data):
    length = len(data)
    sock.sendall(struct.pack('!I', length))
    sock.sendall(b'%s' % bytes(data, 'utf-8'))

def recv_msg(sock):
    lengthbuf = recvall(sock, 4)
    length, = struct.unpack('!I', lengthbuf)
    return recvall(sock, length)
