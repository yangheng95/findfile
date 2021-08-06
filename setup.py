# -*- coding: utf-8 -*-
# file: setup.py
# time: 2021/4/22 0022
# author: yangheng <yangheng@m.scnu.edu.cn>
# github: https://github.com/yangheng95
# Copyright (C) 2021. All Rights Reserved.

from setuptools import setup, find_packages
setup(
    name='findfile',
    version='1.0',
    description='This package provides the function to search target file(s)/dir(s) using keyword,'
                ' alleviating the possibility of failure to find files by specifying relative/absolute path',

    url='https://github.com/yangheng95/findfile',
    # Author details
    author='Yang Heng',
    author_email='yangheng@m.scnu.edu.cn',
    python_requires=">=3.6",
    packages=find_packages(),
    include_package_data=True,
    exclude_package_date={'': ['.gitignore']},
    # Choose your license
    license='MIT',

)
