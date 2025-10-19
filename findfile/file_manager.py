# -*- coding: utf-8 -*-
# file: file_manager.py
# time: 10:22 2023/1/7
# author: yangheng <hy345@exeter.ac.uk>
# github: https://github.com/yangheng95
# huggingface: https://huggingface.co/yangheng
# google scholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# Copyright (C) 2021. All Rights Reserved.
import os.path
import pickle
import time
from pathlib import Path
from typing import Union, List


from findfile.find import accessible

from findfile.find import find_dir, find_dirs, find_file, find_files  # noqa: F401
from findfile.find import rm_dir, rm_dirs, rm_file, rm_files  # noqa: F401
from findfile.find import rm_cwd_dirs, rm_cwd_files  # noqa: F401
from findfile.find import (
    find_cwd_dir,
    find_cwd_dirs,
    find_cwd_file,
    find_cwd_files,
)  # noqa: F401

from findfile.find import __FINDFILE_IGNORE__


class DiskCache(List):
    def __init__(self, work_dir: Union[str, Path], **kwargs):
        if os.path.exists(work_dir):
            self.work_dir = work_dir
        else:
            self.work_dir = find_dir(
                work_dir,
                "",
            )

        self.disk_list_cache = find_files(
            self.work_dir,
            "",
            **kwargs,
        ) + find_dirs(
            self.work_dir,
            "",
            **kwargs,
        )

        self.kwargs = kwargs

        super().__init__(self.disk_list_cache)

    def recache(self, **kwargs):
        self.disk_file_cache = set(find_files(self.work_dir, "", **kwargs))
        super().__init__(self.disk_file_cache)
        return self

    def __iter__(self):
        return iter(self.disk_list_cache)

    def __getitem__(self, item):
        return self.disk_list_cache[item]

    def __setitem__(self, key, value):
        self.disk_list_cache[key] = value

    def __len__(self):
        return len(self.disk_list_cache)


class FileManager:

    def __init__(self, work_dir, **kwargs):

        self.find_dir = find_dir
        self.find_dirs = find_dirs
        self.find_file = find_file
        self.find_files = find_files
        self.rm_dir = rm_dir
        self.rm_dirs = rm_dirs
        self.rm_file = rm_file
        self.rm_files = rm_files
        self.rm_cwd_dirs = rm_cwd_dirs
        self.rm_cwd_files = rm_cwd_files
        self.find_cwd_dir = find_cwd_dir
        self.find_cwd_dirs = find_cwd_dirs
        self.find_cwd_file = find_cwd_file
        self.find_cwd_files = find_cwd_files

        self.__FINDFILE_IGNORE__ = __FINDFILE_IGNORE__

        self.recursive = kwargs.get("recursive", 30)
        self.work_dir = work_dir
        cache_file = f"{work_dir}_disk_cache_{time.strftime('%Y%m%d%H%M%S')}.pkl"
        if os.path.exists(work_dir):
            self.disk_cache = pickle.load(open(cache_file, "rb"))
        else:
            self.disk_cache = DiskCache(work_dir, **kwargs)
            pickle.dump(self.disk_cache, open(cache_file, "wb"))

    def readlines(
        self, file_type=Union[List, str], mode="r", encoding="utf-8", **kwargs
    ):
        if file_type is None:
            file_type = ["txt"]
        elif isinstance(file_type, str):
            file_type = [file_type]

        lines = []
        for f in self.disk_cache:
            if (
                f.split(".")[-1] in file_type in file_type
                and os.path.isfile(f)
                and accessible(f)
            ):
                with open(f, mode=mode, encoding=encoding) as fp:
                    lines += fp.readlines()
        return lines

    def read(self, file_type=Union[List, str], mode="r", encoding="utf-8", **kwargs):
        if file_type is None:
            file_type = ["txt"]
        elif isinstance(file_type, str):
            file_type = [file_type]

        lines = []
        for f in self.disk_cache:
            if (
                f.split(".")[-1] in file_type in file_type
                and os.path.isfile(f)
                and accessible(f)
            ):
                with open(f, mode=mode, encoding=encoding) as fp:
                    lines += fp.readlines()
        return lines

    def writelines(self, content, mode="w", encoding="utf-8", **kwargs):
        for f in self.disk_cache:
            if os.path.isfile(f):
                with open(f, mode=mode, encoding=encoding) as fp:
                    fp.write(content)
