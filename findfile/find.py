# -*- coding: utf-8 -*-
# file: find.py
# time: 2021/8/4
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.
import os


def find_files(dir_path: str, key: str, exclude_keys=[], recursive=True) -> list:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose name contain the 'key',
    'exclude_keys': list or str, file name contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the target files
    '''
    res = []

    if exclude_keys and isinstance(exclude_keys, str):
        exclude_keys = [exclude_keys]
    else:
        exclude_keys = []

    if os.path.isfile(dir_path):
        if key.lower() in dir_path.lower():
            if exclude_keys:
                for exclude_key in exclude_keys:
                    if not (exclude_key and exclude_key in dir_path.lower()):
                        res.append(dir_path)
            else:
                res.append(dir_path)

    elif os.path.isdir(dir_path):
        items = os.listdir(dir_path)
        for file in items:
            if recursive:
                res += find_files(os.path.join(dir_path, file), key, exclude_keys, recursive)
            else:
                if key.lower() in file.lower():
                    if exclude_keys:
                        for exclude_key in exclude_keys:
                            if not (exclude_key and exclude_key in file.lower()):
                                res.append(dir_path)
                    else:
                        res.append(dir_path)
    if len(res) > 1:
        print('Warning: multiple targets {} found but return the first'.format(res))

    return res


def find_file(dir_path: str, key: str, exclude_keys=[], recursive=True) -> str:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose name contain the 'key',
    'exclude_key': file name contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the first target file
    '''
    res = find_files(dir_path, key, exclude_keys, recursive)
    return res[0] if res else None


def find_dirs(dir_path: str, key: str, exclude_keys=[], recursive=True) -> list:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose name contain the 'key',
    'exclude_key': file name contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the target dris
    '''
    res = []

    if exclude_keys and isinstance(exclude_keys, str):
        exclude_keys = [exclude_keys]
    else:
        exclude_keys = []

    if os.path.isdir(dir_path):
        if key.lower() in dir_path.lower():
            if exclude_keys:
                for exclude_key in exclude_keys:
                    if not (exclude_key and exclude_key in dir_path.lower()):
                        res.append(dir_path)
            else:
                res.append(dir_path)

    if recursive:
        dirs = os.listdir(dir_path)
        for d in dirs:
            res += find_file(os.path.join(dir_path, d), key, exclude_keys, recursive)

    if len(res) > 1:
        print('Warning: multiple targets {} found but return the first'.format(res))

    return res


def find_dir(dir_path: str, key: str, exclude_keys=[], recursive=True) -> str:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose name contain the 'key',
    'exclude_key': file name contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the first target dir
    '''
    res = find_dirs(dir_path, key, exclude_keys, recursive)
    return res[0] if res else None
