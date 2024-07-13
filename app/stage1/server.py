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

        # ヘッダーの読み取り
        header = connection.recv(33)

        filename_length = int.from_bytes(header[:1], "big")
        data_length = int.from_bytes(header[1:33], "big")
        stream_rate = 1460

        print(header)

        print('Recieved header from client. Byte length: Title length {}, Data Length {}'.format(filename_length, data_length))

        filename = connection.recv(filename_length).decode('utf-8')

        print('Filename: {}'.format(filename))

        # 読み取ったデータがないときは例外処理
        if data_length == 0:
            raise Exception('No data to read from client.')

        # クライアントから受け取ったファイルをtemp配下にコピーする
        with open(os.path.join(dpath, filename), 'wb+') as f:
            while data_length > 0:
                data = connection.recv(data_length if data_length <= stream_rate else stream_rate)
                f.write(data)
                print('received {} bytes'.format(len(data)))
                data_length -= len(data)
                print(data_length)

        print('Finished downloading the file from client')
        message = "OK : ファイルを正常に受信しました。"
        connection.sendall(message.encode('utf-8'))

    except Exception as e:
        print('Error: ' + str(e))
        message = "NG : ファイルの受信に失敗しました"
        connection.sendall(message.encode('utf-8'))

    finally:
        print("Closing current connection")
        connection.close()