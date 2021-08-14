# -*- coding: utf-8 -*-
# file: find.py
# time: 2021/8/4
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.
import os


def find_files(search_path: str, key='', exclude_key=None, recursive=True) -> list:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose name contain the 'key',
    'exclude_keys': list or str, file name contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the target files
    '''

    if not search_path:
        search_path = os.getcwd()

    res = []

    if not exclude_key:
        exclude_key = []
    if isinstance(exclude_key, str):
        exclude_key = [exclude_key]

    if isinstance(key, str):
        key = [key]

    if os.path.isfile(search_path):
        has_key = True
        for k in key:
            if not k.lower() in search_path.lower():
                has_key = False
                break

        if has_key:
            if exclude_key:
                has_exclude_key = False
                for exclude_key in exclude_key:
                    if exclude_key.lower() in search_path.lower():
                        has_exclude_key = True
                if not has_exclude_key:
                    res.append(search_path)
            else:
                res.append(search_path)

    if os.path.isdir(search_path):
        items = os.listdir(search_path)
        for file in items:
            if recursive:
                res += find_files(os.path.join(search_path, file), key, exclude_key, recursive)

    return res


def find_file(search_path: str, key='', exclude_key=None, recursive=True, disable_alert=False) -> str:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose name contain the 'key',
    'exclude_key': file name contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the first target file
    '''
    res = find_files(search_path, key, exclude_key, recursive)

    if len(res) > 1 and not disable_alert:
        print('FindFile Warning: multiple targets {} found but return the first'.format(res))

    return res[0] if res else None


def find_dirs(search_path: str, key='', exclude_key=None, recursive=True) -> list:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose name contain the 'key',
    'exclude_key': file name contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the target dirs
    '''

    if not search_path:
        search_path = os.getcwd()

    res = []

    if not exclude_key:
        exclude_key = []
    if isinstance(exclude_key, str):
        exclude_key = [exclude_key]

    if isinstance(key, str):
        key = [key]

    if os.path.isdir(search_path):
        has_key = True
        for k in key:
            if not k.lower() in search_path.lower():
                has_key = False
                break

        if has_key:
            if exclude_key:
                has_exclude_key = False
                for exclude_key in exclude_key:
                    if exclude_key.lower() in search_path.lower():
                        has_exclude_key = True
                if not has_exclude_key:
                    res.append(search_path)
            else:
                res.append(search_path)

    if os.path.isdir(search_path):
        items = os.listdir(search_path)
        for file in items:
            if recursive:
                res += find_dirs(os.path.join(search_path, file), key, exclude_key, recursive)

    return res


def find_dir(search_path: str, key='', exclude_key=None, recursive=True, disable_alert=False) -> str:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose name contain the 'key',
    'exclude_key': file name contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the first target dir
    '''
    res = find_dirs(search_path, key, exclude_key, recursive)

    if len(res) > 1 and not disable_alert:
        print('FindFile Warning: multiple targets {} found but return the first'.format(res))

    return res[0] if res else None
