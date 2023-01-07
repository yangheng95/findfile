# -*- coding: utf-8 -*-
# file: __init__.py.py
# time: 2021/8/4
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.

__name__ = "findfile"
__version__ = "2.0.0dev"

from findfile.find import (
    find_files,
    find_file,
    find_dirs,
    find_dir,
    find_cwd_dir,
    find_cwd_file,
    find_cwd_dirs,
    find_cwd_files,
    rm_dirs,
    rm_files,
    rm_dir,
    rm_file,
    rm_cwd_files,
    rm_cwd_dirs,
)
from findfile.file_manager import (DiskCache, FileManager)