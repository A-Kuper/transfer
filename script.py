"""Данный модуль являетс CLI-приложением для перемещения и сортировки .mp3-файлов"""

import argparse
import os
from tinytag import TinyTag, TinyTagException


def tag_handler(source_path):
    """Функция брабатывает ID3-теги, переименовывает файлы, создает множества неповторящихся альбомов и исполниотелей

    Positional arguments:
    source_path - принимает значение исходной директории

    """
    artist_list = []
    album_list = []
    os.chdir(source_path)
    try:
        for root, dirs, files, in os.walk(source_path):
            for name in files:
                if name.endswith('.mp3'):
                    actual_path = os.path.join(source_path, f'{name}')
                    try:
                        temp_track = TinyTag.get(actual_path)
                        if temp_track.artist is None or temp_track.album is None:
                            continue
                        if temp_track.title is None:
                            temp_track.title = name
                        artist_list.append(temp_track.artist)
                        album_list.append(temp_track.album)
                        buf = f'{temp_track.title.lstrip().rstrip()} - ' \
                              f'{temp_track.artist.lstrip().rstrip()} - ' \
                              f'{temp_track.album.lstrip().rstrip()}.mp3'
                        os.rename(name, buf)

                    except TinyTagException:
                        print('Error')
    except FileNotFoundError:
        print('Файл не существует')

    global artists
    global albums
    artists = list(set(artist_list))
    albums = list(set(album_list))


def dir_maker(albums, artists, source_path, target_path):
    """Функция проверяет существование указанных путей в ФС. Если их нет, то создает пути
    И затем переносит файлы из исходной директории в целевую

    Positional arguments:
    albums - принимает множество названий альбомов
    artists - принимает множество названий исполнителей
    source_path - принимает значение исходной директории
    target_path - принимает значение целевой директории

    """
    try:
        if not os.path.exists(target_path):
            os.makedirs(target_path, mode=0o777, exist_ok=True)

        for i in artists:
            artist_path = os.path.join(target_path, f'{i.lstrip().rstrip()}')
            if not os.path.isdir(artist_path):
                os.makedirs(artist_path, mode=0o777, exist_ok=True)

            for albums in i:
                for root, dirs, files, in os.walk(source_path):
                    for name in files:
                        if name.endswith('.mp3'):
                            actual_path = os.path.join(source_path, f'{name}')
                            temp_track = TinyTag.get(actual_path)
                            if temp_track.artist == i:
                                album_path = os.path.join(artist_path, f'{temp_track.album.lstrip().rstrip()}')
                                if not os.path.isdir(album_path):
                                    album_path = os.makedirs(album_path, mode=0o777, exist_ok=True)
                                old_path_name = os.path.join(source_path, f'{name}')
                                new_path_name = os.path.join(album_path, f'{name}')
                                os.replace(old_path_name, new_path_name)
                                print(f'{old_path_name} -> {new_path_name}')

    except TypeError:
        dir_maker(albums, artists, source_path, target_path)
    except PermissionError:
        print('Не хватает прав доступа')
    except FileNotFoundError:
        print('Файл не найден')


parser = argparse.ArgumentParser()

parser.add_argument('-s', '--src-dir', help='Source directory.', default=os.getcwd())
parser.add_argument('-d', '--dst-dir', help='Destination directory.', default=os.getcwd())

args = parser.parse_args()

albums = []
artists = []

print('Start\n')

tag_handler(args.src_dir)
dir_maker(albums, artists, args.src_dir, args.dst_dir)

print("\nDone\n.")
