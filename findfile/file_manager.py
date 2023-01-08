# -*- coding: utf-8 -*-
# file: file_manager.py
# time: 10:22 2023/1/7
# author: yangheng <hy345@exeter.ac.uk>
# github: https://github.com/yangheng95
# huggingface: https://huggingface.co/yangheng
# google scholar: https://scholar.google.com/citations?user=NPq5a_0AAAAJ&hl=en
# Copyright (C) 2021. All Rights Reserved.
import os.path
import re
import shutil
import time
import warnings
from functools import reduce
from pathlib import Path
from typing import Union, Dict, List

from termcolor import colored

from findfile.find import accessible

import findfile
from findfile import find_dir


class DiskCache(List):
    def __init__(self, work_dir: Union[str, Path], **kwargs):
        if os.path.exists(work_dir):
            self.work_dir = work_dir
        else:
            self.work_dir = find_dir(
                work_dir,
                "",
            )

        self.disk_list_cache = findfile.find_files(
            self.work_dir,
            "",
            **kwargs,
        ) + findfile.find_dirs(
            self.work_dir,
            "",
            **kwargs,
        )

        self.kwargs = kwargs

        super().__init__(self.disk_list_cache)

    def recache(self, **kwargs):
        self.disk_file_cache = set(findfile.find_files(self.work_dir, "", **kwargs))
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

    # def __collect_disk_object(
    #     self, path: Union[str, Path], disk_file_cache: Dict = None
    # ):
    #
    #     if disk_file_cache is None:
    #         disk_file_cache = dict()
    #
    #     if isinstance(path, str) or isinstance(path, Path):
    #         objs = findfile.find_files(path, "", recursive=1) + findfile.find_dirs(
    #             path, "", recursive=1
    #         )
    #     else:
    #         raise ValueError(f"Invalid path: {path}")
    #
    #     if path in objs:
    #         objs.remove(path)
    #
    #     disk_file_cache[path] = objs
    #
    #     for obj in objs:
    #         if os.path.exists(obj) and os.path.isdir(obj):
    #             disk_file_cache[path][obj] = self.__collect_disk_object(obj)
    #
    #     return disk_file_cache


class FileManager:
    def __init__(self, work_dir, **kwargs):
        self.recursive = kwargs.get("recursive", 30)
        self.disk_cache = DiskCache(work_dir, recursive=self.recursive, **kwargs)
        self.work_dir = work_dir

    def readlines(self, mode="r", encoding="utf-8", **kwargs):
        lines = []
        for f in self.disk_cache:
            if os.path.isfile(f):
                with open(f, mode=mode, encoding=encoding) as fp:
                    lines += fp.readlines()
        return lines

    def read(self, mode="r", encoding="utf-8", **kwargs):
        lines = []
        for f in self.disk_cache:
            if os.path.isfile(f):
                with open(f, mode=mode, encoding=encoding) as fp:
                    lines += fp.read()
        return lines

    def writelines(self, content, mode="w", encoding="utf-8", **kwargs):
        for f in self.disk_cache:
            if os.path.isfile(f):
                with open(f, mode=mode, encoding=encoding) as fp:
                    fp.write(content)

    def find_file(
            self,
            search_path: Union[str, Path] = None,
            and_key=None,
            exclude_key=None,
            use_regex=False,
            return_relative_path=True,
            return_deepest_path=False,
            disable_alert=False,
            **kwargs,
    ) -> str:
        """
        'search_path': path to search
        'key': find a set of files/dirs whose absolute path contain the 'key'
        'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
        'recursive' integer, recursive search limit
        'return_relative_path' return the relative path instead of absolute path
        'return_deepest_path' True/False to return the deepest/shortest path if multiple targets found
        'disable_alert' no alert if multiple targets found

        :return the file whose path contains the key(s)
        """
        """
         'key': find a set of files/dirs whose absolute path contain the 'key'
         'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
         'recursive' integer, recursive search limit 
         'return_relative_path' return the relative path instead of absolute path
         :return the target files' path in current working directory
         """
        key = kwargs.pop("key", and_key)

        res = []
        or_key = kwargs.pop("or_key", "")
        if or_key and isinstance(or_key, str):
            or_key = [or_key]
        if or_key:
            if or_key and key:
                raise ValueError("The key and or_key arg are contradictory!")
            for key in or_key:
                res += self._find_files(
                    search_path=search_path,
                    key=key,
                    use_regex=use_regex,
                    exclude_key=exclude_key,
                    return_relative_path=return_relative_path,
                    return_deepest_path=return_deepest_path,
                    disable_alert=disable_alert,
                    **kwargs,
                )
        else:
            res = self._find_files(
                search_path=search_path,
                key=key,
                use_regex=use_regex,
                exclude_key=exclude_key,
                return_relative_path=return_relative_path,
                return_deepest_path=return_deepest_path,
                disable_alert=disable_alert,
                **kwargs,
            )

        if not return_deepest_path:
            _res = (
                reduce(lambda x, y: x if len(x) < len(y) else y, res) if res else None
            )
        else:
            _res = (
                reduce(lambda x, y: x if len(x) > len(y) else y, res) if res else None
            )
        if len(res) > 1 and not disable_alert:
            print(
                "FindFile Warning --> multiple targets {} found, only return the {} path: <{}>".format(
                    res,
                    "deepest" if return_deepest_path else "shortest",
                    colored(_res, "yellow"),
                )
            )
        return _res

    def find_cwd_file(
            self,
            and_key=None,
            exclude_key=None,
            use_regex=False,
            return_relative_path=True,
            return_deepest_path=False,
            disable_alert=False,
            **kwargs,
    ):
        """
        'key': find a set of files/dirs whose absolute path contain the 'key'
        'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
        'recursive' integer, recursive search limit
        'return_relative_path' return the relative path instead of absolute path
        'return_deepest_path' True/False to return the deepest/shortest path if multiple targets found
        'disable_alert' no alert if multiple targets found

        :return the target file path in current working directory
        """
        key = kwargs.pop("key", and_key)

        res = []
        or_key = kwargs.pop("or_key", "")
        if or_key and isinstance(or_key, str):
            or_key = [or_key]
        if or_key:
            if or_key and key:
                raise ValueError("The key and or_key arg are contradictory!")
            for key in or_key:
                res += self._find_files(
                    search_path=os.getcwd() if not self.disk_cache else self.disk_cache,
                    key=key,
                    use_regex=use_regex,
                    exclude_key=exclude_key,
                    return_relative_path=return_relative_path,
                    return_deepest_path=return_deepest_path,
                    disable_alert=disable_alert,
                    **kwargs,
                )
        else:
            res = self._find_files(
                search_path=os.getcwd() if not self.disk_cache else self.disk_cache,
                key=key,
                use_regex=use_regex,
                exclude_key=exclude_key,
                return_relative_path=return_relative_path,
                return_deepest_path=return_deepest_path,
                disable_alert=disable_alert,
                **kwargs,
            )

        if not return_deepest_path:
            _res = (
                reduce(lambda x, y: x if len(x) < len(y) else y, res) if res else None
            )
        else:
            _res = (
                reduce(lambda x, y: x if len(x) > len(y) else y, res) if res else None
            )
        if len(res) > 1 and not disable_alert:
            print(
                "FindFile Warning --> multiple targets {} found, only return the {} path: <{}>".format(
                    res,
                    "deepest" if return_deepest_path else "shortest",
                    colored(_res, "yellow"),
                )
            )
        return _res

    def find_cwd_files(
            self,
            and_key=None,
            exclude_key=None,
            use_regex=False,
            return_relative_path=True,
            disable_alert=False,
            **kwargs,
    ):
        """
        'key': find a set of files/dirs whose absolute path contain the 'key'
        'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
        'recursive' integer, recursive search limit
        'return_relative_path' return the relative path instead of absolute path

        :return the target files' path in current working directory
        """
        key = kwargs.pop("key", and_key)

        if kwargs.get("return_deepest_path", False):
            raise ValueError(
                "return_deepest_path is not supported in find_cwd_files() which return all the results."
            )

        res = []
        or_key = kwargs.pop("or_key", "")
        if or_key and isinstance(or_key, str):
            or_key = [or_key]
        if or_key:
            if or_key and key:
                raise ValueError("The key and or_key arg are contradictory!")
            for key in or_key:
                res += self._find_files(
                    search_path=os.getcwd() if not self.disk_cache else self.disk_cache,
                    key=key,
                    exclude_key=exclude_key,
                    use_regex=use_regex,
                    return_relative_path=return_relative_path,
                    disable_alert=disable_alert,
                    **kwargs,
                )
        else:
            res = self._find_files(
                search_path=os.getcwd() if not self.disk_cache else self.disk_cache,
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                disable_alert=disable_alert,
                **kwargs,
            )
        return res

    def find_files(
            self,
            search_path: Union[str, Path] = None,
            and_key=None,
            exclude_key=None,
            use_regex=False,
            return_relative_path=True,
            disable_alert=False,
            **kwargs,
    ):
        """
        'key': find a set of files/dirs whose absolute path contain the 'key'
        'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
        'recursive' integer, recursive search limit
        'return_relative_path' return the relative path instead of absolute path
        :return the target files' path in current working directory
        """
        key = kwargs.pop("key", and_key)

        if kwargs.get("return_deepest_path", False):
            raise ValueError(
                "return_deepest_path is not supported in find_files() which return all the results."
            )

        res = []
        or_key = kwargs.pop("or_key", "")
        if or_key and isinstance(or_key, str):
            or_key = [or_key]
        if or_key:
            if or_key and key:
                raise ValueError("The key and or_key arg are contradictory!")
            for key in or_key:
                res += self._find_files(
                    search_path,
                    key=key,
                    exclude_key=exclude_key,
                    use_regex=use_regex,
                    return_relative_path=return_relative_path,
                    disable_alert=disable_alert,
                    **kwargs,
                )
        else:
            res = self._find_files(
                search_path,
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                disable_alert=disable_alert,
                **kwargs,
            )
        return res

    def find_dir(
            self,
            search_path: Union[str, Path] = None,
            and_key=None,
            exclude_key=None,
            use_regex=False,
            return_relative_path=True,
            return_deepest_path=False,
            disable_alert=False,
            **kwargs,
    ) -> str:
        """
        'search_path': path to search
        'key': find a set of files/dirs whose absolute path contain the 'key'
        'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
        'recursive' integer, recursive search limit
        'return_relative_path' return the relative path instead of absolute path
        'return_deepest_path' True/False to return the deepest/shortest path if multiple targets found
        'disable_alert' no alert if multiple targets found

        :return the dir path
        """
        key = kwargs.pop("key", and_key)

        res = []
        or_key = kwargs.pop("or_key", "")
        if or_key and isinstance(or_key, str):
            or_key = [or_key]
        if or_key:
            if or_key and key:
                raise ValueError("The key and or_key arg are contradictory!")
            for key in or_key:
                res += self._find_dirs(
                    search_path=search_path,
                    key=key,
                    exclude_key=exclude_key,
                    use_regex=use_regex,
                    return_relative_path=return_relative_path,
                    return_deepest_path=return_deepest_path,
                    **kwargs,
                )

        else:
            res += self._find_dirs(
                search_path=search_path,
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                return_deepest_path=return_deepest_path,
                **kwargs,
            )

        if not return_deepest_path:
            _res = (
                reduce(lambda x, y: x if len(x) < len(y) else y, res) if res else None
            )
        else:
            _res = (
                reduce(lambda x, y: x if len(x) > len(y) else y, res) if res else None
            )
        if len(res) > 1 and not disable_alert:
            print(
                "FindFile Warning --> multiple targets {} found, only return the {} path: <{}>".format(
                    res,
                    "deepest" if return_deepest_path else "shortest",
                    colored(_res, "yellow"),
                )
            )
        return _res

    def find_cwd_dir(
            self,
            and_key=None,
            exclude_key=None,
            use_regex=False,
            return_relative_path=True,
            return_deepest_path=False,
            disable_alert=False,
            **kwargs,
    ):
        """
        'key': find a set of files/dirs whose absolute path contain the 'key',
        'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
        'recursive' integer, recursive search limit
        'return_relative_path' return the relative path instead of absolute path
        'return_deepest_path' True/False to return the deepest/shortest path if multiple targets found
        'disable_alert' no alert if multiple targets found

        :return the target dir path in current working directory
        """
        key = kwargs.pop("key", and_key)

        res = []
        or_key = kwargs.pop("or_key", "")
        if or_key and isinstance(or_key, str):
            or_key = [or_key]
        if or_key:
            if or_key and key:
                raise ValueError("The key and or_key arg are contradictory!")
            for key in or_key:
                res += self._find_dirs(
                    search_path=os.getcwd() if not self.disk_cache else self.disk_cache,
                    key=key,
                    exclude_key=exclude_key,
                    use_regex=use_regex,
                    return_relative_path=return_relative_path,
                    return_deepest_path=return_deepest_path,
                    disable_alert=disable_alert,
                    **kwargs,
                )

        else:
            res = self._find_dirs(
                search_path=os.getcwd() if not self.disk_cache else self.disk_cache,
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                return_deepest_path=return_deepest_path,
                disable_alert=disable_alert,
                **kwargs,
            )

        if not return_deepest_path:
            _res = (
                reduce(lambda x, y: x if len(x) < len(y) else y, res) if res else None
            )
        else:
            _res = (
                reduce(lambda x, y: x if len(x) > len(y) else y, res) if res else None
            )
        if len(res) > 1 and not disable_alert:
            print(
                "FindFile Warning --> multiple targets {} found, only return the {} path: <{}>".format(
                    res,
                    "deepest" if return_deepest_path else "shortest",
                    colored(_res, "yellow"),
                )
            )
        return _res

    def find_cwd_dirs(
            self,
            and_key=None,
            exclude_key=None,
            use_regex=False,
            return_relative_path=True,
            disable_alert=False,
            **kwargs,
    ):
        """
        'key': find a set of files/dirs whose absolute path contain the 'key'
        'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
        'recursive' integer, recursive search limit
        'return_relative_path' return the relative path instead of absolute path

        :return the target dirs' path in current working directory
        """

        key = kwargs.pop("key", and_key)

        if kwargs.get("return_deepest_path", False):
            raise ValueError(
                "return_deepest_path is not supported in find_cwd_dirs() which return all the results."
            )

        res = []
        or_key = kwargs.pop("or_key", "")
        if or_key and isinstance(or_key, str):
            or_key = [or_key]
        if or_key:
            if or_key and key:
                raise ValueError("The key and or_key arg are contradictory!")
            for key in or_key:
                res += self._find_dirs(
                    search_path=os.getcwd() if not self.disk_cache else self.disk_cache,
                    key=key,
                    exclude_key=exclude_key,
                    use_regex=use_regex,
                    return_relative_path=return_relative_path,
                    disable_alert=disable_alert,
                    **kwargs,
                )

        else:
            res = self._find_dirs(
                search_path=os.getcwd() if not self.disk_cache else self.disk_cache,
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                disable_alert=disable_alert,
                **kwargs,
            )

        if kwargs.get("return_leaf_only", True):
            _res = []
            for i, x in enumerate(res):
                flag = True
                for j, y in enumerate(res[:i] + res[i + 1:]):
                    if y == x or y.startswith(x):
                        flag = False
                        break
                if flag:
                    _res.append(x)
            res = _res

        return res

    def find_dirs(
            self,
            search_path: Union[str, Path] = None,
            and_key=None,
            exclude_key=None,
            use_regex=False,
            return_relative_path=True,
            return_deepest_path=False,
            disable_alert=False,
            **kwargs,
    ):
        """
        'key': find a set of files/dirs whose absolute path contain the 'key'
        'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
        'recursive' integer, recursive search limit
        'return_relative_path' return the relative path instead of absolute path

        :return the target dirs' path in current working directory
        """

        key = kwargs.pop("key", and_key)

        if kwargs.get("return_deepest_path", False):
            raise ValueError(
                "return_deepest_path is not supported in find_dirs() which return all the results."
            )

        res = []
        or_key = kwargs.pop("or_key", "")
        if or_key and isinstance(or_key, str):
            or_key = [or_key]
        if or_key:
            if or_key and key:
                raise ValueError("The key and or_key arg are contradictory!")
            for key in or_key:
                res += self._find_dirs(
                    search_path,
                    key=key,
                    exclude_key=exclude_key,
                    use_regex=use_regex,
                    return_relative_path=return_relative_path,
                    return_deepest_path=return_deepest_path,
                    disable_alert=disable_alert,
                    **kwargs,
                )

        else:
            res = self._find_dirs(
                search_path,
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                return_deepest_path=return_deepest_path,
                disable_alert=disable_alert,
                **kwargs,
            )

        if kwargs.get("return_leaf_only", True):
            _res = []
            for i, x in enumerate(res):
                flag = True
                for j, y in enumerate(res[:i] + res[i + 1:]):
                    if y == x or y.startswith(x):
                        flag = False
                        break
                if flag:
                    _res.append(x)
            res = _res

        return res

    def rm_files(self, path=None, and_key=None, exclude_key=None, **kwargs):
        key = kwargs.pop("key", and_key)

        if not path:
            path = os.getcwd()

        or_key = kwargs.pop("or_key", "")
        if or_key and key:
            raise ValueError("The key and or_key arg are contradictory!")

        if key:
            fs = self._find_files(
                search_path=path,
                key=key,
                exclude_key=exclude_key,
                use_regex=kwargs.pop("use_regex", True),
                recursive=kwargs.pop("recursive", 30),
                return_relative_path=kwargs.pop("return_relative_path", False),
                **kwargs,
            )

            print(colored("FindFile Warning: Remove files {}".format(fs), "red"))

            for f in fs:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception as e:
                        print(
                            colored(
                                "FindFile Warning: Remove file {} failed: {}".format(
                                    f, e
                                ),
                                "red",
                            )
                        )

        if or_key:
            fs = []
            for or_key in or_key:
                fs += self._find_files(
                    search_path=path,
                    key=or_key,
                    exclude_key=exclude_key,
                    use_regex=kwargs.pop("use_regex", True),
                    recursive=kwargs.pop("recursive", 30),
                    return_relative_path=kwargs.pop("return_relative_path", False),
                    **kwargs,
                )

            print(colored("FindFile Warning: Remove files {}".format(fs), "red"))

            for f in fs:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception as e:
                        print(
                            colored(
                                "FindFile Warning --> Remove file {} failed: {}".format(
                                    f, e
                                ),
                                "red",
                            )
                        )

    def rm_dirs(self, path=None, and_key=None, exclude_key=None, **kwargs):
        key = kwargs.pop("key", and_key)

        if not path:
            path = os.getcwd()

        or_key = kwargs.pop("or_key", "")
        if or_key and key:
            raise ValueError("The key and or_key arg are contradictory!")

        if key:
            ds = self._find_dirs(
                search_path=path,
                key=key,
                exclude_key=exclude_key,
                use_regex=kwargs.pop("use_regex", True),
                recursive=kwargs.pop("recursive", 30),
                return_relative_path=kwargs.pop("return_relative_path", False),
                **kwargs,
            )

            print(colored("FindFile Warning: Remove dirs {}".format(ds), "red"))

            for d in ds:
                if os.path.exists(d):
                    try:
                        shutil.rmtree(d)
                    except Exception as e:
                        print(
                            colored(
                                "FindFile Warning: Remove dir {} failed: {}".format(
                                    d, e
                                ),
                                "red",
                            )
                        )

        if or_key:
            ds = []
            for or_key in or_key:
                ds += self._find_dirs(
                    search_path=path,
                    key=or_key,
                    exclude_key=exclude_key,
                    use_regex=kwargs.pop("use_regex", True),
                    recursive=kwargs.pop("recursive", 30),
                    return_relative_path=kwargs.pop("return_relative_path", False),
                    **kwargs,
                )

            print(colored("FindFile Warning: Remove dirs {}".format(ds), "red"))

            for d in ds:
                if os.path.exists(d):
                    if os.path.exists(d):
                        try:
                            shutil.rmtree(d)
                        except Exception as e:
                            print(
                                colored(
                                    "FindFile Warning --> Remove dir {} failed: {}".format(
                                        d, e
                                    ),
                                    "red",
                                )
                            )

    def rm_file(self, path=None, and_key=None, exclude_key=None, **kwargs):
        key = kwargs.pop("key", and_key)

        if not path:
            path = os.getcwd()

        or_key = kwargs.pop("or_key", "")
        if or_key and key:
            raise ValueError("The key and or_key arg are contradictory!")

        if key:
            fs = self._find_files(
                search_path=path,
                key=key,
                exclude_key=exclude_key,
                use_regex=kwargs.pop("use_regex", True),
                recursive=kwargs.pop("recursive", 30),
                return_relative_path=kwargs.pop("return_relative_path", False),
                **kwargs,
            )

            if len(fs) > 1:
                raise ValueError("Multi-files detected while removing single file.")

            print(colored("FindFile Warning: Remove file {}".format(fs), "red"))

            for f in fs:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception as e:
                        print(
                            colored(
                                "FindFile Warning --> Remove file {} failed: {}".format(
                                    f, e
                                ),
                                "red",
                            )
                        )

        if or_key:
            fs = []
            for or_key in or_key:
                fs += self._find_files(
                    search_path=path,
                    key=or_key,
                    exclude_key=exclude_key,
                    use_regex=False,
                    recursive=kwargs.pop("recursive", 30),
                    return_relative_path=kwargs.pop("return_relative_path", False),
                    **kwargs,
                )
            if len(fs) > 1:
                raise ValueError("Multi-files detected while removing single file.")

            print(colored("FindFile Warning --> Remove file {}".format(fs), "red"))

            for f in fs:
                if os.path.exists(f):
                    try:
                        os.remove(f)
                    except Exception as e:
                        print(
                            colored(
                                "FindFile Warning: Remove file {} failed: {}".format(
                                    f, e
                                ),
                                "red",
                            )
                        )

    def rm_dir(self, path=None, and_key=None, exclude_key=None, **kwargs):
        key = kwargs.pop("key", and_key)

        if not path:
            path = os.getcwd()

        or_key = kwargs.pop("or_key", "")
        if or_key and key:
            raise ValueError("The key and or_key arg are contradictory!")

        if key:
            ds = self._find_dirs(
                search_path=path,
                key=key,
                exclude_key=exclude_key,
                use_regex=kwargs.pop("use_regex", True),
                recursive=kwargs.pop("recursive", 30),
                return_relative_path=kwargs.pop("return_relative_path", False),
                **kwargs,
            )

            if len(ds) > 1:
                raise ValueError("Multi-dirs detected while removing single file.")

            print(colored("FindFile Warning: Remove dirs {}".format(ds), "red"))

            for d in ds:
                if os.path.exists(d):
                    try:
                        shutil.rmtree(d)
                    except Exception as e:
                        print(
                            colored(
                                "FindFile Warning --> Remove dirs {} failed: {}".format(
                                    d, e
                                ),
                                "red",
                            )
                        )

        if or_key:
            ds = []
            for or_key in or_key:
                ds += self._find_dirs(
                    search_path=path,
                    key=or_key,
                    exclude_key=exclude_key,
                    use_regex=kwargs.pop("use_regex", True),
                    recursive=kwargs.pop("recursive", 30),
                    return_relative_path=kwargs.pop("return_relative_path", False),
                    **kwargs,
                )

            if len(ds) > 1:
                raise ValueError("Multi-dirs detected while removing single file.")

            print(colored("FindFile Warning: Remove dirs {}".format(ds), "red"))

            for d in ds:
                if os.path.exists(d):
                    try:
                        shutil.rmtree(d)
                    except Exception as e:
                        print(
                            colored(
                                "FindFile Warning --> Remove dirs {} failed: {}".format(
                                    d, e
                                ),
                                "red",
                            )
                        )

    def rm_cwd_file(self, and_key=None, exclude_key=None, **kwargs):
        self.rm_file(os.getcwd(), and_key, exclude_key, **kwargs)

    def rm_cwd_files(self, and_key=None, exclude_key=None, **kwargs):
        self.rm_files(os.getcwd(), and_key, exclude_key, **kwargs)

    def rm_cwd_dir(self, and_key=None, exclude_key=None, **kwargs):
        self.rm_dir(os.getcwd(), and_key, exclude_key, **kwargs)

    def rm_cwd_dirs(self, and_key=None, exclude_key=None, **kwargs):
        self.rm_dirs(os.getcwd(), and_key, exclude_key, **kwargs)

    def _find_files(
            self,
            search_path: Union[str, Path] = None,
            key=None,
            exclude_key=None,
            use_regex=False,
            return_relative_path=True,
            **kwargs,
    ) -> list:
        """
        'search_path': path to search
        'key': find a set of files/dirs whose absolute path contain the 'key'
        'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
        'recursive' integer, recursive search limit
        'return_relative_path' return the relative path instead of absolute path

        :return the files whose path contains the key(s)
        """
        recursive = kwargs.pop("recursive", 30)
        if recursive is True:
            recursive = 5

        if not search_path:
            search_path = self.disk_cache

        res = []

        if not exclude_key:
            exclude_key = []
        if isinstance(exclude_key, str):
            exclude_key = [exclude_key]

        if isinstance(key, str):
            key = [key]
        for sp in search_path:
            if os.path.isfile(sp):
                has_key = True
                for k in key:
                    try:
                        if use_regex:
                            if not re.findall(k, sp):
                                has_key = False
                                break
                        else:
                            if not k.lower() in sp.lower():
                                has_key = False
                                break
                    except re.error as e:
                        warnings.warn(
                            "FindFile Warning --> Regex pattern error: {}, using string-based search".format(
                                e
                            )
                        )
                        if not k.lower() in sp.lower():
                            has_key = False
                            break

                if has_key:
                    if exclude_key:
                        has_exclude_key = False
                        for ex_key in exclude_key:
                            try:
                                if use_regex:
                                    if re.findall(ex_key, sp):
                                        has_exclude_key = True
                                        break
                                else:
                                    if ex_key.lower() in sp.lower():
                                        has_exclude_key = True
                                        break
                            except re.error:
                                warnings.warn(
                                    "FindFile Warning ->> Regex pattern error, using string-based search"
                                )
                                if ex_key.lower() in sp.lower():
                                    has_exclude_key = True
                                    break
                        if not has_exclude_key:
                            res.append(
                                sp.replace(os.getcwd() + os.sep, "")
                                if return_relative_path
                                else sp
                            )
                    else:
                        res.append(
                            sp.replace(os.getcwd() + os.sep, "")
                            if return_relative_path
                            else sp
                        )

            if os.path.isdir(sp) and accessible(sp) and len(search_path) == 1:
                items = os.listdir(sp)
                for file in items:
                    if recursive:
                        res += self._find_files(
                            os.path.join(sp, file),
                            key=key,
                            exclude_key=exclude_key,
                            use_regex=use_regex,
                            recursive=recursive - 1,
                            return_relative_path=return_relative_path,
                            **kwargs,
                        )

        return list(set(res))

    def _find_dirs(
            self,
            search_path: Union[str, Path] = None,
            key=None,
            exclude_key=None,
            use_regex=False,
            return_relative_path=True,
            **kwargs,
    ) -> list:
        """
        'search_path': path to search
        'key': find a set of files/dirs whose absolute path contain the 'key'
        'exclude_key': file whose absolute path contains 'exclude_key' will be ignored
        'recursive' integer, recursive search limit
        'return_relative_path' return the relative path instead of absolute path

        :return the dirs whose path contains the key(s)
        """
        recursive = kwargs.pop("recursive", 30)
        if recursive is True:
            recursive = 5

        if not search_path:
            search_path = self.disk_cache

        res = []

        if not exclude_key:
            exclude_key = []
        if isinstance(exclude_key, str):
            exclude_key = [exclude_key]

        if isinstance(key, str):
            key = [key]
        for sp in search_path:
            if os.path.isdir(sp):
                if not use_regex:
                    has_key = all(k in sp for k in key)
                else:
                    has_key = all(re.findall(k, sp) for k in key)

                has_exclude_key = False
                if exclude_key:
                    if not use_regex:
                        has_key = all(k in sp for k in key)
                    else:
                        has_key = all(re.findall(k, sp) for k in key)

                    if has_key and exclude_key:
                        if not use_regex:
                            has_exclude_key = any(ex_key in sp for ex_key in exclude_key)
                        else:
                            has_exclude_key = any(re.findall(ex_key, sp) for ex_key in exclude_key)

                if has_key and not has_exclude_key:
                    res.append(
                        sp.replace(os.getcwd() + os.sep, "")
                        if return_relative_path
                        else sp
                    )

            if os.path.isdir(sp) and accessible(sp) and len(search_path) == 1:
                items = os.listdir(sp)
                for file in items:
                    if recursive:
                        res += self._find_dirs(
                            os.path.join(sp, file),
                            key=key,
                            exclude_key=exclude_key,
                            use_regex=use_regex,
                            recursive=recursive - 1,
                            return_relative_path=return_relative_path,
                            **kwargs,
                        )

        return list(set(res))

if __name__ == "__main__":
    # disk_cache = DiskCache(
    #     r"C:\Users\chuan\OneDrive - University of Exeter\AIProjects\PyABSA\CPDP\PROMISE-backup"
    # )
    print(time.localtime())
    fm = FileManager(
        r"C:\Users\chuan\OneDrive - University of Exeter\AIProjects\PyABSA\CPDP\PROMISE-backup"
    )
    print(time.localtime())
    java_files = fm.find_files(key=".java", use_regex=False, recursive=30)
    print(time.localtime())
    py_files = fm.find_files(key=".py")
    print(time.localtime())

    print(java_files)
