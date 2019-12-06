import torrent_parser
import os

d = {}
d['info'] = {}
torrent_parser.create_torrent_file('t.torrent',d)
size = 0
path='C:\\Users\\Eziel\\Desktop\\vid\\abcd.mp4'
size += os.path.getsize(path)
print(size)