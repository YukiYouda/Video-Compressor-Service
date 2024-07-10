import socket
import sys

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = '0.0.0.0'
server_port = 9001

print('connectig to {}'.format(server_address, server_port))

try:
    sock.connect((server_address, server_port))
except socket.error as err:
    print(err)
    sys.exit(1)

try:
    filepath = input('Type in a file to upload: ')
finally:
    print('closing socket')
    sock.close()