# findfile - simplified solution of FileNotFoundError

This is a package for you to locate your target file(s)/dir(s) easily.

# Usage
## Install
```
pip install findfile
```

## ready to use
If you have been bothered by FileNotFoundError while the file does exist but misplaced, you can call

```
from findfile import find_file, find_files, find_dir, find_dirs

path_to_search = './'

key = ['target', '.txt']  # str or list, the files whose absolute path contain all the keys in the key are the target files

exclude_key = ['dev', '.ignore']  # str or list, the files whose absolute path contain any exclude key are ignored

target_file = find_file(path_to_search, key, exclude_keys, recursive=False)  # return all the target files, only the first two params are required

target_files = find_file(path_to_search, key, exclude_keys, recursive=True)  # recursive enable to search in all subdirectories

target_dir = find_file(path_to_search, key, exclude_keys, recursive=True)  # search directory instead of file

target_dirs = find_file(path_to_search, key, exclude_keys, recursive=True)  # search directories instead of file


```
