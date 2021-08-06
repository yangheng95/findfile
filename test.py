# -*- coding: utf-8 -*-
# file: test.py
# time: 2021/8/5
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.

from findfile import find_file, find_files, find_dir, find_dirs

search_path = './'

key = ['target', '.txt']  # str or list, the files whose absolute path contain all the keys in the key are the target files

exclude_key = ['dev', '.ignore']  # str or list, the files whose absolute path contain any exclude key are ignored

target_file = find_file(search_path, key, exclude_key, recursive=False)   # return the first target file, recursive means to search in all subdirectories

target_files = find_files(search_path, key, exclude_key, recursive=True)   # return all the target files, only the first param are required

target_dir = find_dir(search_path, key, exclude_key)  # search directory instead of file

target_dirs = find_dirs(search_path, key, exclude_key)  # search directories