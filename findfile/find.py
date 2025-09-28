# -*- coding: utf-8 -*-
# file: find.py
# time: 2021/8/4
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.
import os
import re
import shutil
import warnings
from collections import deque
from functools import reduce
from pathlib import Path
from typing import Iterator, Sequence, Union


from termcolor import colored

__FINDFILE_IGNORE__ = [".FFIGNORE", ".ffignore", ".ffi", ".FFI"]

warnings.filterwarnings("once")


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


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _compile_patterns(
    patterns: Sequence[str] | None,
    use_regex: bool,
    *,
    disable_alert: bool = False,
) -> list[re.Pattern] | None:
    """Compile *patterns* once. Plain text keys are escaped; case‑insensitive."""
    if not patterns:
        return None
    compiled: list[re.Pattern] = []
    for p in patterns:
        try:
            if use_regex:
                compiled.append(re.compile(p, flags=re.IGNORECASE))
            else:
                compiled.append(re.compile(re.escape(p), flags=re.IGNORECASE))
        except re.error as exc:
            if not disable_alert:
                warnings.warn(
                    f"Pattern '{p}' could not be compiled: {exc}. Falling back to substring search.",
                    RuntimeWarning,
                )
            compiled.append(re.compile(re.escape(p), flags=re.IGNORECASE))
    return compiled


# MODIFIED: Split matching logic into separate functions for include and exclude
def _matches_any_include(path: Path, patterns: list[re.Pattern] | None) -> bool:
    """Check if path matches any include pattern (OR logic)."""
    if not patterns:
        return True
    s = str(path)
    return any(p.search(s) for p in patterns)


def _matches_any_exclude_or(path: Path, patterns: list[re.Pattern] | None) -> bool:
    """Check if path matches any exclude pattern (OR logic - NEW BEHAVIOR)."""
    if not patterns:
        return False
    s = str(path)
    return any(p.search(s) for p in patterns)  # OR logic: exclude if ANY pattern matches


def _matches_any_exclude_and(path: Path, patterns: list[re.Pattern] | None) -> bool:
    """Check if path matches all exclude patterns (AND logic - ORIGINAL BEHAVIOR)."""
    if not patterns:
        return False
    s = str(path)
    return all(p.search(s) for p in patterns)  # AND logic: exclude only if ALL patterns match


def _matches_any(path: Path, patterns: list[re.Pattern] | None) -> bool:
    """Original function kept for backward compatibility."""
    if not patterns:
        return True
    s = str(path)
    return all(p.search(s) for p in patterns)


# MODIFIED: Updated _iter_paths to support both OR and AND logic for exclusions
def _iter_paths(
        root: Path,
        want: str,
        include: list[re.Pattern] | None,
        exclude: list[re.Pattern] | None,
        max_depth: int,
        exclude_logic: str = "or",  # NEW PARAMETER
) -> Iterator[Path]:
    """Breadth‑first traversal that stops at *max_depth* (0 means only *root* itself)."""

    queue: deque[tuple[Path, int]] = deque([(root, 0)])
    while queue:
        current, depth = queue.popleft()
        try:
            if not current.exists() or current.is_symlink():
                continue  # skip broken links / non‑existent entries

            if depth > max_depth:
                continue

            # Decide whether to yield *current* before descending
            if (want == "file" and current.is_file()) or (want == "dir" and current.is_dir()):
                # MODIFIED: Use appropriate exclusion logic based on exclude_logic parameter
                should_include = _matches_any_include(current, include)

                if exclude_logic == "or":
                    should_exclude = _matches_any_exclude_or(current, exclude)
                else:  # "and" or any other value defaults to original behavior
                    should_exclude = _matches_any_exclude_and(current, exclude)

                if should_include and not should_exclude:
                    yield current

            # Descend only into directories (and only if we haven't exceeded depth)
            if current.is_dir() and depth < max_depth:
                for child in current.iterdir():
                    queue.append((child, depth + 1))
        except PermissionError:
            # Silently ignore unreadable directories
            continue


# ---------------------------------------------------------------------------
# MODIFIED Public API - Added exclude_logic parameter
# ---------------------------------------------------------------------------

def _find(
        search_path: Union[str, Path] | None = None,
        *,
        key: Sequence[str] | str | None = None,
        exclude_key: Sequence[str] | str | None = None,
        use_regex: bool = False,
        recursive: int | bool = 5,
        return_relative_path: bool = True,
        return_deepest_path: bool = False,
        disable_alert: bool = False,
        want: str = "file",  # "file" or "dir"
        exclude_logic: str = "or",  # NEW PARAMETER: "or" or "and"
) -> list[str]:
    """Internal unified implementation for both files and dirs.

    Parameters
    ----------
    exclude_logic : str, default "or"
        Logic for exclude_key patterns:
        - "or": exclude if path matches ANY exclude pattern (recommended)
        - "and": exclude if path matches ALL exclude patterns (original behavior)
    return_deepest_path
        When *True*, filter the resulting matches so that only those at the greatest
        depth (relative to *search_path* or CWD) are returned. Useful for "take the
        deepest hit" semantics.
    disable_alert
        Suppress warnings emitted when regex compilation fails.
    """

    root = Path(search_path or Path.cwd()).expanduser().resolve()

    # Compatibility shim: recursive=True behaves like depth 5 (legacy)
    if recursive is True:
        recursive = 5
    if recursive is False:
        recursive = 0

    # Normalise *key* arguments to list[str]
    if isinstance(key, str):
        key = [key]
    if isinstance(exclude_key, str):
        exclude_key = [exclude_key]

    # Merge with (optional) global ignore list
    try:
        exclude_combined: list[str] | None = (exclude_key or []) + list(__FINDFILE_IGNORE__)
    except Exception:
        exclude_combined = exclude_key

    include = _compile_patterns(key, use_regex, disable_alert=disable_alert)
    exclude = _compile_patterns(exclude_combined, use_regex, disable_alert=disable_alert)

    # MODIFIED: Pass exclude_logic parameter to _iter_paths
    path_iter = _iter_paths(
        root,
        want=want,
        include=include,
        exclude=exclude,
        max_depth=int(recursive),
        exclude_logic=exclude_logic,  # NEW PARAMETER
    )
    paths: list[Path] = list(path_iter)

    if not paths:
        return []

    # Retain only the deepest match(es) if requested
    if return_deepest_path:
        depths = [len(p.relative_to(root if root != Path.cwd() else Path.cwd()).parts) for p in paths]
        max_depth = max(depths)
        paths = [p for p, d in zip(paths, depths) if d == max_depth]

    if return_relative_path:
        return [str(p.relative_to(Path.cwd())) for p in paths]
    return [str(p) for p in paths]


def _find_files(**kwargs) -> list[str]:
    """Find files matching *key* within *search_path* (depth‑limited)."""
    return _find(want="file", **kwargs)


def _find_dirs(**kwargs) -> list[str]:
    """Find directories matching *key* within *search_path* (depth‑limited)."""
    return _find(want="dir", **kwargs)

def _find_files(**kwargs) -> list[str]:
    """Find files matching *key* within *search_path* (depth‑limited)."""

    return _find(want="file", **kwargs)


def _find_dirs(**kwargs) -> list[str]:
    """Find directories matching *key* within *search_path* (depth‑limited)."""

    return _find(want="dir", **kwargs)


def find_file(
    search_path: Union[str, Path] = None,
    and_key=None,
    exclude_key=None,
    use_regex=False,
    return_relative_path=True,
    return_deepest_path=False,
    disable_alert=False,
    **kwargs
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
            res += _find_files(
                search_path=search_path,
                key=key,
                use_regex=use_regex,
                exclude_key=exclude_key,
                return_relative_path=return_relative_path,
                return_deepest_path=return_deepest_path,
                disable_alert=disable_alert,
                **kwargs
            )
    else:
        res = _find_files(
            search_path=search_path,
            key=key,
            use_regex=use_regex,
            exclude_key=exclude_key,
            return_relative_path=return_relative_path,
            return_deepest_path=return_deepest_path,
            disable_alert=disable_alert,
            **kwargs
        )

    if not return_deepest_path:
        _res = reduce(lambda x, y: x if len(x) < len(y) else y, res) if res else None
    else:
        _res = reduce(lambda x, y: x if len(x) > len(y) else y, res) if res else None
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
    and_key=None,
    exclude_key=None,
    use_regex=False,
    return_relative_path=True,
    return_deepest_path=False,
    disable_alert=False,
    **kwargs
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
            res += _find_files(
                search_path=os.getcwd(),
                key=key,
                use_regex=use_regex,
                exclude_key=exclude_key,
                return_relative_path=return_relative_path,
                return_deepest_path=return_deepest_path,
                disable_alert=disable_alert,
                **kwargs
            )
    else:
        res = _find_files(
            search_path=os.getcwd(),
            key=key,
            use_regex=use_regex,
            exclude_key=exclude_key,
            return_relative_path=return_relative_path,
            return_deepest_path=return_deepest_path,
            disable_alert=disable_alert,
            **kwargs
        )

    if not return_deepest_path:
        _res = reduce(lambda x, y: x if len(x) < len(y) else y, res) if res else None
    else:
        _res = reduce(lambda x, y: x if len(x) > len(y) else y, res) if res else None
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
    and_key=None,
    exclude_key=None,
    use_regex=False,
    return_relative_path=True,
    disable_alert=False,
    **kwargs
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
            res += _find_files(
                search_path=os.getcwd(),
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                disable_alert=disable_alert,
                **kwargs
            )
    else:
        res = _find_files(
            search_path=os.getcwd(),
            key=key,
            exclude_key=exclude_key,
            use_regex=use_regex,
            return_relative_path=return_relative_path,
            disable_alert=disable_alert,
            **kwargs
        )
    return res


def find_files(
    search_path: Union[str, Path] = None,
    and_key=None,
    exclude_key=None,
    use_regex=False,
    return_relative_path=True,
    disable_alert=False,
    **kwargs
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
            res += _find_files(
                search_path=search_path,
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                disable_alert=disable_alert,
                **kwargs
            )
    else:
        res = _find_files(
            search_path=search_path,
            key=key,
            exclude_key=exclude_key,
            use_regex=use_regex,
            return_relative_path=return_relative_path,
            disable_alert=disable_alert,
            **kwargs
        )
    return res


def find_dir(
    search_path: Union[str, Path] = None,
    and_key=None,
    exclude_key=None,
    use_regex=False,
    return_relative_path=True,
    return_deepest_path=False,
    disable_alert=False,
    **kwargs
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
            res += _find_dirs(
                search_path=search_path,
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                return_deepest_path=return_deepest_path,
                **kwargs
            )

    else:
        res += _find_dirs(
            search_path=search_path,
            key=key,
            exclude_key=exclude_key,
            use_regex=use_regex,
            return_relative_path=return_relative_path,
            return_deepest_path=return_deepest_path,
            **kwargs
        )

    if not return_deepest_path:
        _res = reduce(lambda x, y: x if len(x) < len(y) else y, res) if res else None
    else:
        _res = reduce(lambda x, y: x if len(x) > len(y) else y, res) if res else None
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
    and_key=None,
    exclude_key=None,
    use_regex=False,
    return_relative_path=True,
    return_deepest_path=False,
    disable_alert=False,
    **kwargs
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
            res += _find_dirs(
                search_path=os.getcwd(),
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                return_deepest_path=return_deepest_path,
                disable_alert=disable_alert,
                **kwargs
            )

    else:
        res = _find_dirs(
            search_path=os.getcwd(),
            key=key,
            exclude_key=exclude_key,
            use_regex=use_regex,
            return_relative_path=return_relative_path,
            return_deepest_path=return_deepest_path,
            disable_alert=disable_alert,
            **kwargs
        )

    if not return_deepest_path:
        _res = reduce(lambda x, y: x if len(x) < len(y) else y, res) if res else None
    else:
        _res = reduce(lambda x, y: x if len(x) > len(y) else y, res) if res else None
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
    and_key=None,
    exclude_key=None,
    use_regex=False,
    return_relative_path=True,
    disable_alert=False,
    **kwargs
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
            res += _find_dirs(
                search_path=os.getcwd(),
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                disable_alert=disable_alert,
                **kwargs
            )

    else:
        res = _find_dirs(
            search_path=os.getcwd(),
            key=key,
            exclude_key=exclude_key,
            use_regex=use_regex,
            return_relative_path=return_relative_path,
            disable_alert=disable_alert,
            **kwargs
        )

    if kwargs.get("return_leaf_only", True):
        _res = []
        for i, x in enumerate(res):
            flag = True
            for j, y in enumerate(res[:i] + res[i + 1 :]):
                if y == x or y.startswith(x):
                    flag = False
                    break
            if flag:
                _res.append(x)
        res = _res

    return res


def find_dirs(
    search_path: Union[str, Path] = None,
    and_key=None,
    exclude_key=None,
    use_regex=False,
    return_relative_path=True,
    return_deepest_path=False,
    disable_alert=False,
    **kwargs
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
            res += _find_dirs(
                search_path=search_path,
                key=key,
                exclude_key=exclude_key,
                use_regex=use_regex,
                return_relative_path=return_relative_path,
                return_deepest_path=return_deepest_path,
                disable_alert=disable_alert,
                **kwargs
            )

    else:
        res = _find_dirs(
            search_path=search_path,
            key=key,
            exclude_key=exclude_key,
            use_regex=use_regex,
            return_relative_path=return_relative_path,
            return_deepest_path=return_deepest_path,
            disable_alert=disable_alert,
            **kwargs
        )

    if kwargs.get("return_leaf_only", True):
        _res = []
        for i, x in enumerate(res):
            flag = True
            for j, y in enumerate(res[:i] + res[i + 1 :]):
                if y == x or y.startswith(x):
                    flag = False
                    break
            if flag:
                _res.append(x)
        res = _res

    return res


def rm_files(path=None, and_key=None, exclude_key=None, **kwargs):
    key = kwargs.pop("key", and_key)

    if not path:
        path = os.getcwd()

    or_key = kwargs.pop("or_key", "")
    if or_key and key:
        raise ValueError("The key and or_key arg are contradictory!")

    if key:
        fs = _find_files(
            search_path=path,
            key=key,
            exclude_key=exclude_key,
            use_regex=kwargs.pop("use_regex", False),
            recursive=kwargs.pop("recursive", 10),
            return_relative_path=kwargs.pop("return_relative_path", False),
            **kwargs
        )

        print(colored("FindFile Warning: Remove files {}".format(fs), "red"))

        for f in fs:
            if os.path.exists(f):
                try:
                    os.remove(f)
                except Exception as e:
                    print(
                        colored(
                            "FindFile Warning: Remove file {} failed: {}".format(f, e),
                            "red",
                        )
                    )

    if or_key:
        fs = []
        for or_key in or_key:
            fs += _find_files(
                search_path=path,
                key=or_key,
                exclude_key=exclude_key,
                use_regex=kwargs.pop("use_regex", False),
                recursive=kwargs.pop("recursive", 10),
                return_relative_path=kwargs.pop("return_relative_path", False),
                **kwargs
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


def rm_dirs(path=None, and_key=None, exclude_key=None, **kwargs):
    key = kwargs.pop("key", and_key)

    if not path:
        path = os.getcwd()

    or_key = kwargs.pop("or_key", "")
    if or_key and key:
        raise ValueError("The key and or_key arg are contradictory!")

    if key:
        ds = _find_dirs(
            search_path=path,
            key=key,
            exclude_key=exclude_key,
            use_regex=kwargs.pop("use_regex", False),
            recursive=kwargs.pop("recursive", 10),
            return_relative_path=kwargs.pop("return_relative_path", False),
            **kwargs
        )

        print(colored("FindFile Warning: Remove dirs {}".format(ds), "red"))

        for d in ds:
            if os.path.exists(d):
                try:
                    shutil.rmtree(d)
                except Exception as e:
                    print(
                        colored(
                            "FindFile Warning: Remove dir {} failed: {}".format(d, e),
                            "red",
                        )
                    )

    if or_key:
        ds = []
        for or_key in or_key:
            ds += _find_dirs(
                search_path=path,
                key=or_key,
                exclude_key=exclude_key,
                use_regex=kwargs.pop("use_regex", False),
                recursive=kwargs.pop("recursive", 10),
                return_relative_path=kwargs.pop("return_relative_path", False),
                **kwargs
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


def rm_file(path=None, and_key=None, exclude_key=None, **kwargs):
    key = kwargs.pop("key", and_key)

    if not path:
        path = os.getcwd()

    or_key = kwargs.pop("or_key", "")
    if or_key and key:
        raise ValueError("The key and or_key arg are contradictory!")

    if key:
        fs = _find_files(
            search_path=path,
            key=key,
            exclude_key=exclude_key,
            use_regex=kwargs.pop("use_regex", False),
            recursive=kwargs.pop("recursive", 10),
            return_relative_path=kwargs.pop("return_relative_path", False),
            **kwargs
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
            fs += _find_files(
                search_path=path,
                key=or_key,
                exclude_key=exclude_key,
                use_regex=False,
                recursive=kwargs.pop("recursive", 10),
                return_relative_path=kwargs.pop("return_relative_path", False),
                **kwargs
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
                            "FindFile Warning: Remove file {} failed: {}".format(f, e),
                            "red",
                        )
                    )


def rm_dir(path=None, and_key=None, exclude_key=None, **kwargs):
    key = kwargs.pop("key", and_key)

    if not path:
        path = os.getcwd()

    or_key = kwargs.pop("or_key", "")
    if or_key and key:
        raise ValueError("The key and or_key arg are contradictory!")

    if key:
        ds = _find_dirs(
            search_path=path,
            key=key,
            exclude_key=exclude_key,
            use_regex=kwargs.pop("use_regex", False),
            recursive=kwargs.pop("recursive", 10),
            return_relative_path=kwargs.pop("return_relative_path", False),
            **kwargs
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
            ds += _find_dirs(
                search_path=path,
                key=or_key,
                exclude_key=exclude_key,
                use_regex=kwargs.pop("use_regex", False),
                recursive=kwargs.pop("recursive", 10),
                return_relative_path=kwargs.pop("return_relative_path", False),
                **kwargs
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


def rm_cwd_file(and_key=None, exclude_key=None, **kwargs):
    rm_file(os.getcwd(), and_key, exclude_key, **kwargs)


def rm_cwd_files(and_key=None, exclude_key=None, **kwargs):
    rm_files(os.getcwd(), and_key, exclude_key, **kwargs)


def rm_cwd_dir(and_key=None, exclude_key=None, **kwargs):
    rm_dir(os.getcwd(), and_key, exclude_key, **kwargs)


def rm_cwd_dirs(and_key=None, exclude_key=None, **kwargs):
    rm_dirs(os.getcwd(), and_key, exclude_key, **kwargs)
