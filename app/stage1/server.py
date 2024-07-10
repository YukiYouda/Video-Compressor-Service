import socket
import os
from pathlib import Path

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '0.0.0.0'
server_port = 9001

# クライアントから受信したファイルをtempフォルダに格納する
dpath = 'temp'
if not os.path.exists(dpath):
    os.makedirs(dpath)

print('Starting up on {} port {}'.format(server_address, server_port))

sock.bind((server_address, server_port))

sock.listen(1)

while True:
    connection, client_address = sock.accept()

    try:
        print('connection from', client_address)
    except Exception as e:
        print('Error: ' + str(e))
    finally:
        print("Closing current connection")
        connection.close()