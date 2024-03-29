# -*- coding: utf-8 -*-
# file: test.py
# time: 2021/8/5
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.

from findfile import (
    find_file,
    find_files,
    find_dir,
    find_dirs,
    find_cwd_dir,
    find_cwd_dirs,
    find_cwd_file,
    find_cwd_files,
    rm_file,
    rm_files,
    rm_dir,
    rm_dirs,
)

search_path = "./"

and_key = [
    "find",
    ".py",
]  # str or list, the files whose absolute path contain all the keys in the key are the target files
# key = ['.']  # str or list, the files whose absolute path contain all the keys in the key are the target files

exclude_key = [
    "dev",
    ".ignore",
]  # str or list, the files whose absolute path contain any exclude key are ignored

target_file = find_file(
    search_path,
    and_key,
    exclude_key,
    recursive=3,
    return_relative_path=False,
    use_regex=False,
    return_deepest_path=True,
)  # return the first target file, recursive means to search in all subdirectories
print(target_file)

target_file = find_file(
    search_path,
    and_key,
    exclude_key,
    recursive=3,
    return_relative_path=False,
    return_deepest_path=False,
)  # return the first target file, recursive means to search in all subdirectories
print(target_file)

target_files = find_files(
    search_path, and_key, exclude_key, recursive=3
)  # return all the target files, only the first param are required
print(target_files)

target_dir = find_dir(
    search_path, and_key, exclude_key
)  # search directory instead of file
print(target_dir)

target_dirs = find_dirs(search_path, and_key, exclude_key)  # search directories
print(target_dirs)

# rm_file(key=['findfile', 'lib'])
# rm_files(key=['findfile', 'lib'])
# rm_dir(key=['dist'])
# rm_dirs(key=['dist'])
# rm_dir(or_key=['dist', 'egg'])
rm_dirs(or_key=["dist", "egg"])
