import socket
import os
from pathlib import Path

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = '0.0.0.0'
server_port = 9002

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
        header = connection.recv(8)

        json_size = int.from_bytes(header[:2], "big")
        media_type_size = int.from_bytes(header[2:3], "big")
        data_size = int.from_bytes(header[3:8], "big")
        stream_rate = 1460

        print(header)

        print('Recieved header from client. Byte length: json_size {}, media_type_size {}, data_size {}'.format(json_size, media_type_size, data_size))

        json = connection.recv(json_size).decode('utf-8')

        media_type = connection.recv(media_type_size).decode('utf-8')

        print('json: {}, media_type: {}'.format(json, media_type))

        # 読み取ったデータがないときは例外処理
        if data_size == 0:
            raise Exception('No data to read from client.')

        # クライアントから受け取ったファイルを読み込む
        while data_size > 0:
            data = connection.recv(data_size if data_size <= stream_rate else stream_rate)
            print('received {} bytes'.format(len(data)))
            data_size -= len(data)
            print(data_size)

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