# -*- coding: utf-8 -*-
# file: find.py
# time: 2021/8/4
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.
import os
import re

def accessible(search_path):
    try:
        os.listdir(search_path)
    except OSError:
        return False
    return True


def find_files(search_path: str, key='', exclude_key=None, use_regex=False, recursive=True, return_relative_path=True) -> list:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose absolute path contain the 'key',
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
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
            try:
                if use_regex:
                    if not re.findall(k.lower(), search_path.lower()):
                        has_key = False
                        break
                else:
                    if not k.lower() in search_path.lower():
                        has_key = False
                        break
            except re.error:
                print('Regex pattern error, using string-based search')
                if not k.lower() in search_path.lower():
                    has_key = False
                    break

        if has_key:
            if exclude_key:
                has_exclude_key = False
                for ex_key in exclude_key:
                    try:
                        if use_regex:
                            if re.findall(ex_key.lower(), search_path.lower()):
                                has_exclude_key = True
                                break
                        else:
                            if ex_key.lower() in search_path.lower():
                                has_exclude_key = True
                                break
                    except re.error:
                        print('Regex pattern error, using string-based search')
                        if ex_key.lower() in search_path.lower():
                            has_exclude_key = True
                            break
                if not has_exclude_key:
                    res.append(search_path.replace(os.getcwd()+os.sep, '') if return_relative_path else search_path)
            else:
                res.append(search_path.replace(os.getcwd()+os.sep, '') if return_relative_path else search_path)

    if os.path.isdir(search_path) and accessible(search_path):
        items = os.listdir(search_path)
        for file in items:
            if recursive:
                res += find_files(os.path.join(search_path, file), key, exclude_key, use_regex=use_regex, recursive=recursive)

    return res


def find_file(search_path: str, key='', exclude_key=None, use_regex=False, recursive=True, return_relative_path=True, disable_alert=False) -> str:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose absolute path contain the 'key',
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the first target file
    '''
    res = find_files(search_path, key, exclude_key, use_regex=use_regex, recursive=recursive, return_relative_path=return_relative_path)

    if len(res) > 1 and not disable_alert:
        print('FindFile Warning: multiple targets {} found but return the first'.format(res))

    return res[0] if res else None


def find_dirs(search_path: str, key='', exclude_key=None, use_regex=False, recursive=True, return_relative_path=True) -> list:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose absolute path contain the 'key',
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
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
            try:
                if use_regex:
                    if not re.findall(k.lower(), search_path.lower()):
                        has_key = False
                        break
                else:
                    if not k.lower() in search_path.lower():
                        has_key = False
                        break
            except re.error:
                print('Regex pattern error, using string-based search')
                if not k.lower() in search_path.lower():
                    has_key = False
                    break

        if has_key:
            if exclude_key:
                has_exclude_key = False
                for ex_key in exclude_key:
                    try:
                        if use_regex:
                            if re.findall(ex_key.lower(), search_path.lower()):
                                has_exclude_key = True
                                break
                        else:
                            if ex_key.lower() in search_path.lower():
                                has_exclude_key = True
                                break
                    except re.error:
                        print('Regex pattern error, using string-based search')
                        if ex_key.lower() in search_path.lower():
                            has_exclude_key = True
                            break
                if not has_exclude_key:
                    res.append(search_path.replace(os.getcwd()+os.sep, '') if return_relative_path else search_path)
            else:
                res.append(search_path.replace(os.getcwd()+os.sep, '') if return_relative_path else search_path)

    if os.path.isdir(search_path) and accessible(search_path):
        items = os.listdir(search_path)
        for file in items:
            if recursive:
                res += find_dirs(os.path.join(search_path, file), key, exclude_key, use_regex, recursive)

    return res


def find_dir(search_path: str, key='', exclude_key=None, use_regex=False, recursive=True, return_relative_path=True, disable_alert=False) -> str:
    '''
    'dir_path': path to search
    'key': find a set of files/dirs whose absolute path contain the 'key',
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the first target dir
    '''
    res = find_dirs(search_path, key, exclude_key, use_regex, recursive, return_relative_path)

    if len(res) > 1 and not disable_alert:
        print('FindFile Warning: multiple targets {} found but return the first'.format(res))

    return res[0] if res else None


def find_cwd_file(key='', use_regex=False, exclude_key=None, recursive=True, return_relative_path=True, disable_alert=False):
    '''
    'key': find a set of files/dirs whose absolute path contain the 'key',
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the first target file in current working directory
    '''
    return find_file(os.getcwd(), key, exclude_key, use_regex, recursive, return_relative_path, disable_alert)


def find_cwd_files(key='', use_regex=False, exclude_key=None, recursive=True, return_relative_path=True):
    '''
    'key': find a set of files/dirs whose absolute path contain the 'key',
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the target files in current working directory
    '''
    return find_files(os.getcwd(), key, exclude_key, use_regex, recursive, return_relative_path)


def find_cwd_dir(key='', use_regex=False, exclude_key=None, recursive=True, return_relative_path=True, disable_alert=False):
    '''
    'key': find a set of files/dirs whose absolute path contain the 'key',
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the target dir in current working directory
    '''
    return find_dir(os.getcwd(), use_regex, key, exclude_key, recursive, return_relative_path, disable_alert)


def find_cwd_dirs(key='', exclude_key=None, use_regex=False, recursive=True, return_relative_path=True):
    '''
    'key': find a set of files/dirs whose absolute path contain the 'key',
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path

    :return the target dirs in current working directory
    '''
    return find_dirs(os.getcwd(), key, exclude_key, use_regex, recursive, return_relative_path)
