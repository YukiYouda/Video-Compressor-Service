import socket
import sys
import os

def protocol_header(filename_length, data_length):
    return filename_length.to_bytes(1, "big") + data_length.to_bytes(32, "big")

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
    filepath = input('アップロードするファイルを入力してください: ')

    # バイナリモードでファイルを読み込む
    with open(filepath, 'rb') as f:

        # mp４でないファイルは弾く
        file_header = f.read(12)
        if b'ftyp' in file_header:

            # ファイルサイズの算出
            f.seek(0, os.SEEK_END)
            file_size = f.tell()
            f.seek(0, 0)

            if file_size > pow(2, 32):
                raise Exception('ファイルは4GB以下にしてください')

            filename = os.path.basename(f.name)
            filename_bits = filename.encode('utf-8')

            header = protocol_header(len(filename_bits), file_size)

            # ヘッダーの送信
            sock.send(header)

            # ファイル名の送信
            sock.send(filename_bits)

            # 一度に1460バイトずつ読み出し、送信する
            data = f.read(1460)
            while data:
                print("Sending...")
                sock.send(data)
                data = f.read(1460)
        else:
            print('ファイルがmp4形式ではありません')
finally:
    print('closing socket')
    sock.close()