import socket
import os
from pathlib import Path
import json
import subprocess
import shutil

def send_data(output_file):
    """
    出力結果をクライアントに送信する関数

    :param output_file: クライアントに送信するファイルパス
    """
    # 出力結果をクライアントに送信する
    with open(output_file, 'rb') as f:
        # 一度に100000バイトずつ読み出し、送信する
        data = f.read(100000)
        while data:
            print("Sending...")
            connection.send(data)
            data = f.read(100000)

def change_resolution(input_file, output_file, resolution):
    """
    ffmegを使用して動画の解像度を変更する関数

    :param input_file: 入力のファイルパス
    :param output_file: 出力のファイルパス
    :param resolution: 新しい解像度(例: "1280x720")
    """
    command = [
        'ffmpeg',
        '-i', input_file,
        '-s', resolution,
        output_file
    ]

    # subproseccでffmpegコマンドを実行
    subprocess.run(command, check=True)

def change_aspect_ratio(input_file, output_file, aspect_ratio):
    """
    ffmegを使用して動画のアスペクト比を変更する関数

    :param input_file: 入力のファイルパス
    :param output_file: 出力のファイルパス
    :param aspect_ratio: 新しい解像度(例: "16/9")
    """
    command = [
        'ffmpeg',
        '-i', input_file,
        '-vf', f'setdar={aspect_ratio}',
        output_file
    ]

    # subproseccでffmpegコマンドを実行
    subprocess.run(command, check=True)

def convert_video_to_audio(input_file, output_file, audio_format='mp3'):
    """
    ffmegを使用して動画をオーディオに変換する関数

    :param input_file: 入力のファイルパス
    :param output_file: 出力のファイルパス
    :audio_format: 出力オーディオ形式(例 : 'mp3', 'wav', 'aac')
    """
    command = [
        'ffmpeg',
        '-i', input_file,
        '-vn',
        '-acodec', audio_format,
        output_file
    ]

    # subproseccでffmpegコマンドを実行
    subprocess.run(command, check=True)

def convert_to_gif(input_file, output_file, start_time, duration):
    """
    ffmegを使用して動画をgifに変換する関数

    :param input_file: 入力のファイルパス
    :param output_file: 出力のファイルパス
    :start_time: 切り抜きの開始時間
    :duration: 切り抜く時間間隔
    """
    command = [
        'ffmpeg',
        '-i', input_file,
        '-ss', start_time,
        '-t', duration,
        output_file
    ]

    # subproseccでffmpegコマンドを実行
    subprocess.run(command, check=True)

def compress_video(input_file, output_file, crf=23):
    """
    ffmegを使用して動画を圧縮する関数

    :param input_file: 入力のファイルパス
    :param output_file: 出力のファイルパス
    :param crf: CRF値(0〜51, 低いほど高品質)
    """
    command = [
        'ffmpeg',
        '-i', input_file,
        '-vcodec', 'libx264',
        '-crf', str(crf),
        output_file
    ]

    # subproseccでffmpegコマンドを実行
    subprocess.run(command, check=True)


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
        stream_rate = 100000

        print(header)

        print('Recieved header from client. Byte length: json_size {}, media_type_size {}, data_size {}'.format(json_size, media_type_size, data_size))

        json_string = connection.recv(json_size).decode('utf-8')

        # JSONが空でなかったら辞書に変換して、キーと値を取得
        if json_string:
            json_dict = json.loads(json_string)

        media_type = connection.recv(media_type_size).decode('utf-8')

        print('json: {}, media_type: {}'.format(json_string, media_type))

        # 読み取ったデータがないときは例外処理
        if data_size == 0:
            raise Exception('No data to read from client.')

        # 一時保存するファイル名
        input_temp_filename = "input_temp_file" + media_type

        # クライアントから受け取ったファイルをtemp配下にコピーする
        with open(os.path.join(dpath, input_temp_filename), 'wb+') as f:
            while data_size > 0:
                data = connection.recv(data_size if data_size <= stream_rate else stream_rate)
                f.write(data)
                print('received {} bytes'.format(len(data)))
                data_size -= len(data)
                print(data_size)

        print('Finished downloading the file from client')

        (key, value), = json_dict.items()
        input_file = os.path.join(dpath, input_temp_filename)
        output_temp_filename = "output_temp_file" + media_type
        output_file = os.path.join(dpath, output_temp_filename)
        output_audio_file = os.path.join(dpath, "output_temp_file.mp3")
        output_gif_file = os.path.join(dpath, "output_temp_file.gif")

        # 圧縮のとき
        if key == "0":

            # 動画を圧縮する
            compress_video(input_file, output_file)

            # 出力結果をクライアントに送信する
            send_data(output_file)

        # 解像度の変更のとき
        if key == "1":

            # 解像度を変更する
            change_resolution(input_file, output_file, value)

            # 出力結果をクライアントに送信する
            send_data(output_file)

        # アスペクト比変更のとき
        if key == "2":

            # アスペクト比を変更する
            change_aspect_ratio(input_file, output_file, value)

            # 出力結果をクライアントに送信する
            send_data(output_file)

        # 動画をオーディオ変換のとき
        if key == "3":

            # 動画をオーディオに変換する
            convert_video_to_audio(input_file, output_audio_file)

            # 出力結果をクライアントに送信する
            send_data(output_audio_file)

        # 動画を切り取ってGIF形式に変換するとき
        if key == "4":

            # 動画を切り取ってGIF形式に変換する
            convert_to_gif(input_file, output_gif_file, value[0], value[1])

            # 出力結果をクライアントに送信する
            send_data(output_gif_file)

    except Exception as e:
        print('Error: ' + str(e))
        message = "NG : ファイルの受信に失敗しました"
        connection.sendall(message.encode('utf-8'))

    finally:
        print("Closing current connection")
        shutil.rmtree(dpath)
        connection.close()
        break