# -*- coding: utf-8 -*-
# file: find.py
# time: 2021/8/4
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.
import os
import re
import shutil
from functools import reduce
from pathlib import Path


def accessible(search_path):
    try:
        os.listdir(search_path)
    except OSError:
        return False
    return True


def covert_path_sep(key_list):
    if isinstance(key_list, str):
        key_list = [key_list]
    new_key_list = []
    for key in key_list:
        if key and os.path.splitext(key):
            new_key_list.append(os.path.split(Path(key)))
        else:
            new_key_list.append(key)
    return key_list


def find_files(search_path: str,
               key='',
               exclude_key=None,
               use_regex=False,
               recursive=True,
               return_relative_path=True,
               **kwargs) -> list:
    '''
    'search_path': path to search
    'key': find a set of files/dirs whose absolute path contain the 'key'
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path
    'return_relative_path' return the relative path instead of absolute path

    :return the files whose path contains the key(s)
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
                    res.append(search_path.replace(os.getcwd() + os.sep, '') if return_relative_path else search_path)
            else:
                res.append(search_path.replace(os.getcwd() + os.sep, '') if return_relative_path else search_path)

    if os.path.isdir(search_path) and accessible(search_path):
        items = os.listdir(search_path)
        for file in items:
            if recursive:
                res += find_files(os.path.join(search_path, file), key, exclude_key, use_regex=use_regex, recursive=recursive)

    return res


def find_file(search_path: str,
              key='',
              exclude_key=None,
              use_regex=False,
              recursive=True,
              return_relative_path=True,
              return_deepest_path=False,
              disable_alert=False,
              **kwargs) -> str:
    '''
    'search_path': path to search
    'key': find a set of files/dirs whose absolute path contain the 'key'
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path
    'return_relative_path' return the relative path instead of absolute path
    'return_deepest_path' True/False to return the deepest/shortest path if multiple targets found
    'disable_alert' no alert if multiple targets found

    :return the file whose path contains the key(s)
    '''
    res = find_files(search_path=search_path,
                     key=key,
                     exclude_key=exclude_key,
                     use_regex=use_regex,
                     recursive=recursive,
                     return_relative_path=return_relative_path)

    if len(res) > 1 and not disable_alert:
        print('FindFile Warning: multiple targets {} found but return the {} path'.format(res, 'deepest' if return_deepest_path else 'shortest'))
    if not return_deepest_path:
        return reduce(lambda x, y: x if len(x) < len(y) else y, res) if res else None
    else:
        return reduce(lambda x, y: x if len(x) > len(y) else y, res) if res else None


def find_dirs(search_path: str,
              key='',
              exclude_key=None,
              use_regex=False,
              recursive=True,
              return_relative_path=True,
              **kwargs) -> list:
    '''
    'search_path': path to search
    'key': find a set of files/dirs whose absolute path contain the 'key'
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path
    'return_relative_path' return the relative path instead of absolute path

    :return the dirs whose path contains the key(s)
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
                    res.append(search_path.replace(os.getcwd() + os.sep, '') if return_relative_path else search_path)
            else:
                res.append(search_path.replace(os.getcwd() + os.sep, '') if return_relative_path else search_path)

    if os.path.isdir(search_path) and accessible(search_path):
        items = os.listdir(search_path)
        for file in items:
            if recursive:
                res += find_dirs(os.path.join(search_path, file), key, exclude_key, use_regex, recursive)

    return res


def find_dir(search_path: str,
             key='',
             exclude_key=None,
             use_regex=False,
             recursive=True,
             return_relative_path=True,
             return_deepest_path=False,
             disable_alert=False,
             **kwargs) -> str:
    '''
    'search_path': path to search
    'key': find a set of files/dirs whose absolute path contain the 'key'
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path
    'return_relative_path' return the relative path instead of absolute path
    'return_deepest_path' True/False to return the deepest/shortest path if multiple targets found
    'disable_alert' no alert if multiple targets found

    :return the dir path
    '''
    res = find_dirs(search_path=search_path,
                    key=key,
                    exclude_key=exclude_key,
                    use_regex=use_regex,
                    recursive=recursive,
                    return_relative_path=return_relative_path)

    if len(res) > 1 and not disable_alert:
        print('FindFile Warning: multiple targets {} found but return the {} path'.format(res, 'deepest' if return_deepest_path else 'shortest'))
    if not return_deepest_path:
        return reduce(lambda x, y: x if len(x) < len(y) else y, res) if res else None
    else:
        return reduce(lambda x, y: x if len(x) > len(y) else y, res) if res else None


def find_cwd_file(key='',
                  use_regex=False,
                  exclude_key=None,
                  recursive=True,
                  return_relative_path=True,
                  return_deepest_path=False,
                  disable_alert=False,
                  **kwargs):
    '''
    'key': find a set of files/dirs whose absolute path contain the 'key'
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path
    'return_relative_path' return the relative path instead of absolute path
    'return_deepest_path' True/False to return the deepest/shortest path if multiple targets found
    'disable_alert' no alert if multiple targets found

    :return the target file path in current working directory
    '''
    return find_file(search_path=os.getcwd(),
                     key=key,
                     use_regex=use_regex,
                     exclude_key=exclude_key,
                     recursive=recursive,
                     return_relative_path=return_relative_path,
                     return_deepest_path=return_deepest_path,
                     disable_alert=disable_alert,
                     **kwargs)


def find_cwd_files(key='',
                   use_regex=False,
                   exclude_key=None,
                   recursive=True,
                   return_relative_path=True,
                   **kwargs):
    '''
    'key': find a set of files/dirs whose absolute path contain the 'key'
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path
    'return_relative_path' return the relative path instead of absolute path

    :return the target files' path in current working directory
    '''
    return find_files(search_path=os.getcwd(),
                      key=key,
                      exclude_key=exclude_key,
                      use_regex=use_regex,
                      recursive=recursive,
                      return_relative_path=return_relative_path,
                      **kwargs)


def find_cwd_dir(key='',
                 use_regex=False,
                 exclude_key=None,
                 recursive=True,
                 return_relative_path=True,
                 return_deepest_path=False,
                 disable_alert=False,
                 **kwargs):
    '''
    'key': find a set of files/dirs whose absolute path contain the 'key',
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path
    'return_relative_path' return the relative path instead of absolute path
    'return_deepest_path' True/False to return the deepest/shortest path if multiple targets found
    'disable_alert' no alert if multiple targets found

    :return the target dir path in current working directory
    '''

    return find_dir(search_path=os.getcwd(),
                    key=key,
                    use_regex=use_regex,
                    exclude_key=exclude_key,
                    recursive=recursive,
                    return_relative_path=return_relative_path,
                    return_deepest_path=return_deepest_path,
                    disable_alert=disable_alert,
                    **kwargs)


def find_cwd_dirs(key='',
                  exclude_key=None,
                  use_regex=False,
                  recursive=True,
                  return_relative_path=True,
                  **kwargs):
    '''
    'key': find a set of files/dirs whose absolute path contain the 'key'
    'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
    'recursive' recursive search in dir_path
    'return_relative_path' return the relative path instead of absolute path

    :return the target dirs' path in current working directory
    '''
    return find_dirs(search_path=os.getcwd(),
                     key=key,
                     exclude_key=exclude_key,
                     use_regex=use_regex,
                     recursive=recursive,
                     return_relative_path=return_relative_path,
                     **kwargs)


def rm_files(path=None, key=None, exclude_key=None, **kwargs):
    if not path:
        path = os.getcwd()

    or_key = kwargs.pop('or_key', '')
    if or_key and key:
        raise ValueError('The key and or_key arg are contradictory!')

    if key:
        fs = find_files(search_path=path,
                        key=key,
                        exclude_key=exclude_key,
                        use_regex=False,
                        recursive=True,
                        return_relative_path=True,
                        **kwargs)

        print('FindFile Warning: Remove file', fs)

        for f in fs:
            os.remove(f)

    if or_key:
        fs = []
        for or_key in or_key:
            fs += find_files(search_path=path,
                             key=or_key,
                             exclude_key=exclude_key,
                             use_regex=False,
                             recursive=True,
                             return_relative_path=True,
                             **kwargs)

        print('FindFile Warning: Remove file', fs)

        for f in fs:
            os.remove(f)


def rm_dirs(path=None, key=None, exclude_key=None, **kwargs):
    if not path:
        path = os.getcwd()

    or_key = kwargs.pop('or_key', '')
    if or_key and key:
        raise ValueError('The key and or_key arg are contradictory!')

    if key:
        ds = find_dirs(search_path=path,
                       key=key,
                       exclude_key=exclude_key,
                       use_regex=False,
                       recursive=True,
                       return_relative_path=True,
                       **kwargs)

        print('FindFile Warning: Remove dir', ds)

        for d in ds:
            shutil.rmtree(d)

    if or_key:
        ds = []
        for or_key in or_key:
            ds += find_dirs(search_path=path,
                            key=or_key,
                            exclude_key=exclude_key,
                            use_regex=False,
                            recursive=True,
                            return_relative_path=True,
                            **kwargs)

        print('FindFile Warning: Remove dir', ds)

        for d in ds:
            shutil.rmtree(d)


def rm_file(path=None, key=None, exclude_key=None, **kwargs):
    if not path:
        path = os.getcwd()

    or_key = kwargs.pop('or_key', '')
    if or_key and key:
        raise ValueError('The key and or_key arg are contradictory!')

    if key:
        fs = find_files(search_path=path,
                        key=key,
                        exclude_key=exclude_key,
                        use_regex=False,
                        recursive=True,
                        return_relative_path=True,
                        **kwargs)

        if len(fs) > 1:
            raise ValueError('Multi-files detected while removing single file.')

        print('FindFile Warning: Remove file', fs)

        for f in fs:
            os.remove(f)

    if or_key:
        fs = []
        for or_key in or_key:
            fs += find_files(search_path=path,
                             key=or_key,
                             exclude_key=exclude_key,
                             use_regex=False,
                             recursive=True,
                             return_relative_path=True,
                             **kwargs)
        if len(fs) > 1:
            raise ValueError('Multi-files detected while removing single file.')

        print('FindFile Warning: Remove file', fs)

        for f in fs:
            os.remove(f)


def rm_dir(path=None, key=None, exclude_key=None, **kwargs):
    if not path:
        path = os.getcwd()

    or_key = kwargs.pop('or_key', '')
    if or_key and key:
        raise ValueError('The key and or_key arg are contradictory!')

    if key:
        ds = find_dirs(search_path=path,
                       key=key,
                       exclude_key=exclude_key,
                       use_regex=False,
                       recursive=True,
                       return_relative_path=True,
                       **kwargs)

        if len(ds) > 1:
            raise ValueError('Multi-dirs detected while removing single file.')

        print('FindFile Warning: Remove dir', ds)

        for d in ds:
            shutil.rmtree(d)

    if or_key:
        ds = []
        for or_key in or_key:
            ds += find_dirs(search_path=path,
                            key=or_key,
                            exclude_key=exclude_key,
                            use_regex=False,
                            recursive=True,
                            return_relative_path=True,
                            **kwargs)

        if len(ds) > 1:
            raise ValueError('Multi-dirs detected while removing single file.')

        print('FindFile Warning: Remove dir', ds)

        for d in ds:
            shutil.rmtree(d)
