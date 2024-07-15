import socket
import sys
import os
from pathlib import Path
import json

def protocol_header(json_size, media_type_size, data_size):
    return json_size.to_bytes(2, "big") + media_type_size.to_bytes(1, "big") + data_size.to_bytes(5, "big")

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = '0.0.0.0'
server_port = 9002

print('connectig to {}'.format(server_address, server_port))

try:
    sock.connect((server_address, server_port))
except socket.error as err:
    print(err)
    sys.exit(1)

# サーバーから受信したファイルをoutputフォルダに格納する
dpath = 'output'
if not os.path.exists(dpath):
    os.makedirs(dpath)

try:
    # 操作内容の入力(0:圧縮、1:解像度の変更、2:アスペクト比の変更、3:音声に変換、4:切り取り)
    operation = int(input('動画処理内容を入力してください(0:圧縮、1:解像度の変更、2:アスペクト比の変更、3:音声に変換、4:切り取り) : '))

    # 圧縮のとき
    if operation == 0:
        compression_dict = {0 : 0}
        json_bits = json.dumps(compression_dict).encode('utf-8')

    # 解像度の変更のとき
    if operation == 1:
        resolution = input('変更する解像度を入力してください : ')
        resolution_dict = {1 : resolution}
        json_bits = json.dumps(resolution_dict).encode('utf-8')

    # アスペクト比の変更のとき
    if operation == 2:
        aspect_ratio = input('変更するアスペクト比を入力してください : ')
        aspect_ratio_dict = {2 : aspect_ratio}
        json_bits = json.dumps(aspect_ratio_dict).encode('utf-8')

    # 動画をオーディオに変換のとき
    if operation == 3:
        audio_dict = {3 : 3}
        json_bits = json.dumps(audio_dict).encode('utf-8')

    # 動画を切り取ってGIF形式に変換するとき
    if operation == 4:
        start_time = input('開始時間を入力してください : ')
        duration = input('切り取る時間を入力してください : ')
        clipping_dict = {4 : [start_time, duration]}
        json_bits = json.dumps(clipping_dict).encode('utf-8')

    # アップロードするファイルの入力
    filepath = input('アップロードするファイルを入力してください: ')

    # バイナリモードでファイルを読み込む
    with open(filepath, 'rb') as f:

        # ファイルサイズの算出
        f.seek(0, os.SEEK_END)
        data_size = f.tell()
        f.seek(0, 0)

        if data_size > pow(2, 40):
            raise Exception('ファイルは1TB以下にしてください')

        # 拡張子の取得
        filename = os.path.basename(f.name)
        path = Path(filename)
        media_type = path.suffix
        media_type_bits = media_type.encode('utf-8')

        header = protocol_header(len(json_bits), len(media_type_bits), data_size)

        # ヘッダーの送信
        sock.send(header)

        # JSONファイルの送信
        sock.send(json_bits)

        # メディアタイプの送信
        sock.send(media_type_bits)

        # 一度に100000バイトずつ読み出し、送信する
        data = f.read(100000)
        while data:
            print("Sending...")
            sock.send(data)
            data = f.read(100000)

        # サーバーから受け取ったファイルをoutput配下にコピーする
        if operation == 3:
            output_file_name = "output.mp3"
        elif operation == 4:
            output_file_name = "output.gif"
        else:
            output_file_name = "output" + media_type
        buffer_size = 4096
        with open(os.path.join(dpath, output_file_name), 'wb+') as f:
            while True:
                data = sock.recv(buffer_size)
                if not data:
                    break
                f.write(data)
            print('output download completed')

finally:
    print('closing socket')
    sock.close()