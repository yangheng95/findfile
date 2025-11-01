# -*- coding: utf-8 -*-
# file: file_manager.py
# time: 10:22 2023/1/7
# author: yangheng <hy345@exeter.ac.uk>
# github: https://github.com/yangheng95
# huggingface: https://huggingface.co/yangheng
# google scholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# Copyright (C) 2021. All Rights Reserved.
import os
import pickle
import time
from pathlib import Path
from typing import Union, List


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


class DiskCache(list):
    def __init__(self, work_dir: Union[str, Path], **kwargs):
        recursive = kwargs.get("recursive", 30)
        # Resolve or locate working directory
        if work_dir and os.path.isdir(work_dir):
            self.work_dir = str(Path(work_dir).resolve())
        else:
            # Try to locate the directory by key in CWD
            located = find_dir(
                search_path=None,
                and_key=str(work_dir) if work_dir is not None else "",
                recursive=recursive,
                return_relative_path=False,
                disable_alert=True,
            )
            if not located:
                raise ValueError(f"Work directory '{work_dir}' not found")
            self.work_dir = located

        # Build initial list cache (absolute paths)
        self.disk_list_cache = find_files(
            self.work_dir,
            and_key="",
            recursive=recursive,
            return_relative_path=False,
            disable_alert=True,
        ) + find_dirs(
            self.work_dir,
            and_key="",
            recursive=recursive,
            return_relative_path=False,
            disable_alert=True,
        )

        self.kwargs = kwargs

        super().__init__(self.disk_list_cache)

    def recache(self, **kwargs):
        recursive = kwargs.get("recursive", self.kwargs.get("recursive", 30))
        files = find_files(
            self.work_dir,
            and_key="",
            recursive=recursive,
            return_relative_path=False,
            disable_alert=True,
        )
        dirs = find_dirs(
            self.work_dir,
            and_key="",
            recursive=recursive,
            return_relative_path=False,
            disable_alert=True,
        )
        self.disk_list_cache = files + dirs
        super().__init__(self.disk_list_cache)
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
        self.work_dir = (
            str(Path(work_dir).resolve()) if os.path.isdir(work_dir) else work_dir
        )
        # Use a stable cache file inside the work directory
        cache_file = None
        if self.work_dir and os.path.isdir(self.work_dir):
            cache_file = os.path.join(self.work_dir, ".findfile_disk_cache.pkl")

        # Build or load cache
        if cache_file and os.path.isfile(cache_file):
            with open(cache_file, "rb") as fp:
                self.disk_cache = pickle.load(fp)
        else:
            self.disk_cache = DiskCache(self.work_dir, **kwargs)
            if cache_file:
                with open(cache_file, "wb") as fp:
                    pickle.dump(self.disk_cache, fp)

    def readlines(self, file_type=None, mode="r", encoding="utf-8", **kwargs):
        if file_type is None:
            file_type = ["txt"]
        elif isinstance(file_type, str):
            file_type = [file_type]

        lines = []
        for f in self.disk_cache:
            if os.path.isfile(f):
                ext = Path(f).suffix.lower().lstrip(".")
                exts = [str(e).lower().lstrip(".") for e in file_type]
                if ext in exts and os.access(f, os.R_OK):
                    with open(f, mode=mode, encoding=encoding) as fp:
                        lines += fp.readlines()
        return lines

    def read(self, file_type=None, mode="r", encoding="utf-8", **kwargs):
        if file_type is None:
            file_type = ["txt"]
        elif isinstance(file_type, str):
            file_type = [file_type]

        lines = []
        for f in self.disk_cache:
            if os.path.isfile(f):
                ext = Path(f).suffix.lower().lstrip(".")
                exts = [str(e).lower().lstrip(".") for e in file_type]
                if ext in exts and os.access(f, os.R_OK):
                    with open(f, mode=mode, encoding=encoding) as fp:
                        lines += fp.readlines()
        return lines

    def writelines(self, content, mode="w", encoding="utf-8", **kwargs):
        for f in self.disk_cache:
            if os.path.isfile(f):
                with open(f, mode=mode, encoding=encoding) as fp:
                    fp.write(content)
